"""
harness/diagnostics.py — DEV-ONLY profiling for a headless workload.

Wrap any sequence of Driver actions and get a machine-readable report:
  - DB queries: total + grouped by normalized statement (spots N+1s / rescans)
  - cProfile: top functions by cumulative time (where the time goes)
  - memory: process RSS delta + optional tracemalloc top allocators (leak hunting)
  - wall time

The **query counts** and the **cProfile shape** are hardware-independent — they tell
you WHERE the cost is and HOW it scales, which is what you actually fix. Wall-time and
RSS are *indicative on this box*, not a substitute for measuring on real hardware.

Stdlib only (cProfile, pstats, tracemalloc, sqlite3 trace, /proc). Dev-only — lives in
harness/, never shipped, never imported by src/.

    from harness.driver import Driver
    from harness.diagnostics import profile

    d = Driver(settings_overrides={"battle.cards_per_round": 1})
    with profile(d, label="10k battles", memory=True) as report:
        for _ in range(10_000):
            d.answer("good")
            if d.services.enemy_pokemon.hp <= 0:
                d.catch()
    report.print()           # human-readable; report.as_dict() for assertions
"""

from __future__ import annotations

import cProfile
import gc
import io
import os
import pstats
import re
import time
import tracemalloc
from contextlib import contextmanager

# Group statements that differ only by literal values, so an N+1 collapses to one
# row with a big count (string literals + bare numbers -> '?', whitespace squashed).
_NORM = [
    (re.compile(r"'[^']*'"), "?"),
    (re.compile(r"\b\d+\b"), "?"),
    (re.compile(r"\s+"), " "),
]


def _normalize(sql: str) -> str:
    s = sql.strip()
    for rx, rep in _NORM:
        s = rx.sub(rep, s)
    return s[:160]


def _rss_mb() -> float:
    """Current process resident set size in MiB (Linux /proc; resource fallback)."""
    try:
        with open("/proc/self/statm") as f:
            resident_pages = int(f.read().split()[1])
        return resident_pages * os.sysconf("SC_PAGE_SIZE") / (1024 * 1024)
    except Exception:
        try:
            import resource
            return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        except Exception:
            return 0.0


class Report:
    def __init__(self, label: str = "run"):
        self.label = label
        self.wall_seconds = 0.0
        self.queries: dict[str, int] = {}
        self.query_total = 0
        self.rss_start = 0.0
        self.rss_end = 0.0
        self.tracemalloc_top: list[tuple[str, float, int]] = []  # (location, kb_growth, count)
        self.cprofile_top: list[tuple[str, int, float, float]] = []  # (func, ncalls, tot, cum)

    def as_dict(self) -> dict:
        top_q = sorted(self.queries.items(), key=lambda kv: -kv[1])[:15]
        return {
            "label": self.label,
            "wall_seconds": round(self.wall_seconds, 3),
            "db": {
                "total_queries": self.query_total,
                "distinct_statements": len(self.queries),
                "by_statement": top_q,
            },
            "memory": {
                "rss_start_mb": round(self.rss_start, 1),
                "rss_end_mb": round(self.rss_end, 1),
                "rss_delta_mb": round(self.rss_end - self.rss_start, 1),
                "tracemalloc_top": self.tracemalloc_top,
            },
            "cprofile_top": self.cprofile_top,
        }

    def print(self) -> None:
        d = self.as_dict()
        print(f"\n=== diagnostics: {d['label']} ===")
        print(f"wall: {d['wall_seconds']}s  (includes profiler overhead)")
        db = d["db"]
        print(f"\nDB queries: {db['total_queries']} total, {db['distinct_statements']} distinct")
        for stmt, n in db["by_statement"]:
            print(f"  {n:>8}  {stmt}")
        m = d["memory"]
        print(f"\nRSS: {m['rss_start_mb']} -> {m['rss_end_mb']} MB  (delta {m['rss_delta_mb']:+} MB)")
        for loc, kb, cnt in m["tracemalloc_top"]:
            print(f"  +{kb:>9.1f} KB  ({cnt:+} objs)  {loc}")
        if d["cprofile_top"]:
            print("\ncProfile (top by cumulative time):")
            for func, ncalls, tot, cum in d["cprofile_top"]:
                print(f"  cum={cum:7.3f}s  tot={tot:7.3f}s  calls={ncalls:>9}  {func}")
        print()


@contextmanager
def profile(driver, label: str = "run", memory: bool = False, cprofile: bool = True, top: int = 15):
    """Profile the workload run inside the ``with`` block. Yields a Report.

    memory=True adds tracemalloc top-allocator tracking (heavier; great for leaks).
    cprofile=False skips the function profiler (lower overhead, keeps query counts).
    """
    rep = Report(label)

    # 1) Exact DB query counting via the sqlite trace callback on the live connection.
    conn = None
    try:
        conn = driver.services.db._get_connection()
    except Exception:
        conn = None

    def _trace(sql):
        key = _normalize(sql)
        rep.queries[key] = rep.queries.get(key, 0) + 1
        rep.query_total += 1

    if conn is not None:
        try:
            conn.set_trace_callback(_trace)
        except Exception:
            conn = None

    # 2) Memory baselines (after a gc so the delta reflects retained, not churn).
    gc.collect()
    rep.rss_start = _rss_mb()
    snap0 = None
    if memory:
        tracemalloc.start(20)
        snap0 = tracemalloc.take_snapshot()

    pr = cProfile.Profile() if cprofile else None
    t0 = time.perf_counter()
    if pr:
        pr.enable()
    try:
        yield rep
    finally:
        if pr:
            pr.disable()
        rep.wall_seconds = time.perf_counter() - t0

        if memory and snap0 is not None:
            snap1 = tracemalloc.take_snapshot()
            for st in snap1.compare_to(snap0, "lineno")[:top]:
                rep.tracemalloc_top.append((str(st.traceback), st.size_diff / 1024.0, st.count_diff))
            tracemalloc.stop()
        gc.collect()
        rep.rss_end = _rss_mb()

        if conn is not None:
            try:
                conn.set_trace_callback(None)
            except Exception:
                pass

        if pr:
            ps = pstats.Stats(pr, stream=io.StringIO())
            rows = [
                (f"{os.path.basename(fn[0])}:{fn[1]}({fn[2]})", nc, tt, ct)
                for fn, (cc, nc, tt, ct, callers) in ps.stats.items()
            ]
            rows.sort(key=lambda r: -r[3])  # by cumulative time
            rep.cprofile_top = rows[:top]
