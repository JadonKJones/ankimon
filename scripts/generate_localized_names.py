"""Generate localized move-name lookups from the PokeAPI CSV data dump.

Why this exists: translating move names word-for-word is wrong -- "Struggle Bug"
is not a literal rendering in Japanese or Spanish, the games ship their own
official names ("むしのていこう", "Estoicismo"). PokeAPI publishes every language's
official names as flat CSVs, so we pull those once instead of hand-translating
~950 moves.

Outputs (written into src/Ankimon/data_files/):
    move_names_jp.json        - Japanese  (local_language_id 1)
    move_names_sp.json        - Spanish   (local_language_id 7)
    move_names_es_latam.json  - refreshed from the same Spanish data

Spanish (LatAm) and Spanish (Spain) share one Nintendo localization for move
names, so es_latam reuses the id-7 data.

Usage:
    python scripts/generate_localized_names.py                 # fetch from GitHub
    python scripts/generate_localized_names.py /path/to/csvdir # use local CSVs

Keys match the existing move_names.json convention: the English name lowercased
with every non-alphanumeric character removed ("Struggle Bug" -> "strugglebug").

Any pre-existing entries the fresh pull doesn't cover (a few Z-Moves / G-Max
moves lack ja/es names in the dump) are preserved from the shipped file.
"""
from __future__ import annotations

import csv
import io
import json
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "Ankimon" / "data_files"

CSV_URL = (
    "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/move_names.csv"
)

LANG_EN = 9
LANG_JA = 1
LANG_ES = 7

SPANISH_OUTPUTS = ("move_names_sp.json", "move_names_es_latam.json")


def normalize_key(name: str) -> str:
    return "".join(c for c in name.lower() if c.isalnum())


def load_move_name_rows(csvdir: Path | None) -> list[dict]:
    if csvdir is not None:
        text = (csvdir / "move_names.csv").read_text(encoding="utf-8")
    else:
        print(f"  fetching {CSV_URL}")
        with urllib.request.urlopen(CSV_URL, timeout=60) as resp:
            text = resp.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def lookup_for_language(rows: list[dict], lang_id: int) -> dict[str, str]:
    by_move: dict[int, dict[int, str]] = {}
    for r in rows:
        by_move.setdefault(int(r["move_id"]), {})[int(r["local_language_id"])] = r["name"]

    out: dict[str, str] = {}
    for names in by_move.values():
        english = names.get(LANG_EN)
        localized = names.get(lang_id)
        if english and localized:
            out[normalize_key(english)] = localized
    return out


def merge_with_existing(path: Path, fresh: dict[str, str]) -> dict[str, str]:
    merged: dict[str, str] = {}
    if path.exists():
        merged.update(json.loads(path.read_text(encoding="utf-8")))
    merged.update(fresh)
    return dict(sorted(merged.items()))


def write_json(path: Path, data: dict[str, str]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"  wrote {path.relative_to(REPO_ROOT)}  ({len(data)} entries)")


def main() -> None:
    csvdir = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    print("Loading move names" + (f" from {csvdir}" if csvdir else " from PokeAPI"))
    rows = load_move_name_rows(csvdir)

    ja = lookup_for_language(rows, LANG_JA)
    es = lookup_for_language(rows, LANG_ES)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    jp_path = DATA_DIR / "move_names_jp.json"
    write_json(jp_path, merge_with_existing(jp_path, ja))
    for fname in SPANISH_OUTPUTS:
        path = DATA_DIR / fname
        write_json(path, merge_with_existing(path, es))
    print("Done.")


if __name__ == "__main__":
    main()
