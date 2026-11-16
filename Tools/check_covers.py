#!/usr/bin/env python3
"""Check what the lessons cover against bridge-common-conventions.

Tools/lesson-covers.toml says which conventions, natural methods and skills
each lesson practises, as IDs from bridge-craftwork/bridge-common-conventions.
This checks, against that repo's published snapshot (pack.json):

- every ID a lesson covers is defined there, and is not itself a set of
  lessons;
- every lesson in bridge-classroom/manifest.json has an entry, and every
  entry is a lesson that exists.

    python3 Tools/check_covers.py                # the published snapshot
    python3 Tools/check_covers.py --pack FILE    # a pack.json on disk

Exit status 1 on a problem. A lesson with an empty list is reported, not
refused: it is a lesson nobody has described yet.
"""

import argparse
import json
import os
import sys
import tomllib
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COVERS = os.path.join(ROOT, "Tools", "lesson-covers.toml")
MANIFEST = os.path.join(ROOT, "bridge-classroom", "manifest.json")
PACK_URL = "https://bridge-craftwork.github.io/bridge-common-conventions/pack.json"


def load_pack(path=None):
    if path:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    req = urllib.request.Request(PACK_URL, headers={"User-Agent": "baker-bridge-check-covers"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--pack", help="a pack.json on disk, instead of the published one")
    args = ap.parse_args()

    with open(COVERS, "rb") as fh:
        covers = {n: e.get("covers", []) for n, e in tomllib.load(fh).get("lessons", {}).items()}
    with open(MANIFEST, encoding="utf-8") as fh:
        lessons = json.load(fh)["lessons"]
    try:
        pack = load_pack(args.pack)
    except (OSError, ValueError) as e:
        sys.exit(f"could not read the snapshot ({args.pack or PACK_URL}): {e}")
    if pack.get("schema") != "pack/v1":
        sys.exit('not a pack snapshot: `schema` is not "pack/v1"')
    # Agreements are under `conventions`; skills and judgement under `skills`.
    defs = {**pack.get("conventions", {}), **pack.get("skills", {})}

    problems, empty = [], []
    for name in sorted(lessons):
        if name not in covers:
            problems.append(f"{name}: a lesson with no entry in Tools/lesson-covers.toml")
    for name in sorted(covers):
        if name not in lessons:
            problems.append(f"{name}: in Tools/lesson-covers.toml, but not a lesson in the manifest")
            continue
        if not covers[name]:
            empty.append(name)
        for i in covers[name]:
            if i not in defs:
                problems.append(f"{name}: covers `{i}`, which bridge-common-conventions does not define")
            elif defs[i].get("kind") == "lesson":
                problems.append(f"{name}: covers `{i}`, which is a set of lessons, not something a lesson covers")
        if lessons[name].get("covers") != covers[name]:
            problems.append(f"{name}: the manifest's `covers` is out of date (run Tools/generate_manifest.py)")

    ids = {i for c in covers.values() for i in c}
    print(f"{len(covers)} lessons cover {len(ids)} conventions, natural methods and skills")
    if empty:
        print(f"not described yet: {', '.join(empty)}")
    for p in problems:
        print(p, file=sys.stderr)
    if problems:
        sys.exit(1)
    print("every ID is defined")


if __name__ == "__main__":
    main()
