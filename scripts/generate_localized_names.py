"""Generate localized move name + description lookups from the PokeAPI CSV dump.

Why this exists: translating text word-for-word is wrong -- "Struggle Bug" is
not a literal rendering in Japanese or Spanish, the games ship their own
official names ("むしのていこう", "Estoicismo") and in-game move descriptions.
PokeAPI publishes every language's official strings as flat CSVs, so we pull
those once instead of hand-translating ~950 moves.

Outputs (written into src/Ankimon/data_files/):
    move_names_jp.json / move_names_sp.json / move_names_es_latam.json
    move_desc_jp.json  / move_desc_sp.json  / move_desc_es_latam.json

Spanish (LatAm) and Spanish (Spain) share one Nintendo localization, so the
es_latam files reuse the id-7 data.

Usage:
    python scripts/generate_localized_names.py                 # fetch from GitHub
    python scripts/generate_localized_names.py /path/to/csvdir # use local CSVs

Keys match the existing move_names.json convention: the English name lowercased
with every non-alphanumeric character removed ("Struggle Bug" -> "strugglebug").

Pre-existing entries the fresh pull doesn't cover (a few Z-Moves / G-Max moves)
are preserved from the shipped file.
"""
from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "src" / "Ankimon" / "data_files"

CSV_BASE = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/"

LANG_EN = 9
LANG_JA = 1
LANG_ES = 7

# (japanese output, spanish outputs) per data set
NAME_SPANISH_OUTPUTS = ("move_names_sp.json", "move_names_es_latam.json")
DESC_SPANISH_OUTPUTS = ("move_desc_sp.json", "move_desc_es_latam.json")


def normalize_key(name: str) -> str:
    return "".join(c for c in name.lower() if c.isalnum())


def load_csv(name: str, csvdir: Path | None) -> list[dict]:
    if csvdir is not None:
        text = (csvdir / name).read_text(encoding="utf-8")
    else:
        url = CSV_BASE + name
        print(f"  fetching {url}")
        with urllib.request.urlopen(url, timeout=60) as resp:
            text = resp.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def move_id_to_english(name_rows: list[dict]) -> dict[int, str]:
    return {
        int(r["move_id"]): r["name"]
        for r in name_rows
        if int(r["local_language_id"]) == LANG_EN
    }


def names_for_language(name_rows: list[dict], lang_id: int) -> dict[int, str]:
    return {
        int(r["move_id"]): r["name"]
        for r in name_rows
        if int(r["local_language_id"]) == lang_id
    }


_WS = re.compile(r"\s+")


def clean_flavor(text: str) -> str:
    # PokeAPI flavor text carries hard line breaks, soft hyphens and narrow
    # no-break spaces from the game text boxes; flatten to one clean line.
    text = text.replace("\u00ad", "")       # soft hyphen
    text = text.replace("\u202f", " ")      # narrow no-break space
    text = text.replace("\u3000", " ")      # ideographic space
    text = text.replace("\x0c", " ").replace("\n", " ").replace("\r", " ")
    return _WS.sub(" ", text).strip()


def descriptions_for_language(flavor_rows: list[dict], lang_id: int) -> dict[int, str]:
    # Keep the newest version group's text for each move (highest id wins).
    best: dict[int, tuple[int, str]] = {}
    for r in flavor_rows:
        if int(r["language_id"]) != lang_id:
            continue
        move_id = int(r["move_id"])
        vg = int(r["version_group_id"])
        if move_id not in best or vg > best[move_id][0]:
            best[move_id] = (vg, r["flavor_text"])
    return {mid: clean_flavor(txt) for mid, (_, txt) in best.items()}


def keyed_by_english(
    english: dict[int, str], localized: dict[int, str]
) -> dict[str, str]:
    out: dict[str, str] = {}
    for move_id, en_name in english.items():
        val = localized.get(move_id)
        if val:
            out[normalize_key(en_name)] = val
    return dict(sorted(out.items()))


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


def emit(jp_name: str, spanish_names: tuple[str, ...], english, ja_map, es_map, merge):
    jp_path = DATA_DIR / jp_name
    ja_data = keyed_by_english(english, ja_map)
    write_json(jp_path, merge_with_existing(jp_path, ja_data) if merge else ja_data)
    es_data = keyed_by_english(english, es_map)
    for fname in spanish_names:
        path = DATA_DIR / fname
        write_json(path, merge_with_existing(path, es_data) if merge else es_data)


def main() -> None:
    csvdir = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    print("Loading CSV data" + (f" from {csvdir}" if csvdir else " from PokeAPI"))
    name_rows = load_csv("move_names.csv", csvdir)
    flavor_rows = load_csv("move_flavor_text.csv", csvdir)

    english = move_id_to_english(name_rows)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Move names:")
    emit(
        "move_names_jp.json",
        NAME_SPANISH_OUTPUTS,
        english,
        names_for_language(name_rows, LANG_JA),
        names_for_language(name_rows, LANG_ES),
        merge=True,
    )

    print("Move descriptions:")
    emit(
        "move_desc_jp.json",
        DESC_SPANISH_OUTPUTS,
        english,
        descriptions_for_language(flavor_rows, LANG_JA),
        descriptions_for_language(flavor_rows, LANG_ES),
        merge=False,
    )
    print("Done.")


if __name__ == "__main__":
    main()
