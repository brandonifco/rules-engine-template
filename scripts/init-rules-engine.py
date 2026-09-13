#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

p = argparse.ArgumentParser()
p.add_argument("--project-id", required=True)
p.add_argument("--project-name", required=True)
p.add_argument("--project-prefix", required=True)
p.add_argument("--repo", required=True)
a = p.parse_args()

if not re.fullmatch(r"[a-z][a-z0-9-]*", a.project_id):
    raise SystemExit("--project-id must match [a-z][a-z0-9-]*")
if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", a.project_prefix):
    raise SystemExit("--project-prefix must be an identifier-like name with no punctuation or spaces")
if not re.fullmatch(r"[^/\s]+/[^/\s]+", a.repo):
    raise SystemExit("--repo must be OWNER/REPOSITORY")

expected = {
    "src/DeckardII.Core",
    "tests/DeckardII.Core.Tests",
    "tests/DeckardII.Testing",
}
missing = [x for x in expected if not (ROOT / x).is_dir()]
if missing:
    raise SystemExit("template baseline not present or already initialized: " + ", ".join(missing))

replacements = (
    ("brandonifco/deckardII", a.repo),
    ("Deckard II", a.project_name),
    ("DeckardII", a.project_prefix),
    ("deckardii", a.project_id),
)

skip = {".git"}
for path in sorted(ROOT.rglob("*")):
    if path == Path(__file__).resolve():
        continue
    if not path.is_file() or any(part in skip for part in path.parts):
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    new = text
    for old, value in replacements:
        new = new.replace(old, value)
    if new != text:
        path.write_text(new, encoding="utf-8")

moves = (
    (
        ROOT / f"src/{a.project_prefix}.Core/DeckardII.Core.csproj",
        ROOT / f"src/{a.project_prefix}.Core/{a.project_prefix}.Core.csproj",
    ),
    (
        ROOT / f"tests/{a.project_prefix}.Core.Tests/DeckardII.Core.Tests.csproj",
        ROOT / f"tests/{a.project_prefix}.Core.Tests/{a.project_prefix}.Core.Tests.csproj",
    ),
    (
        ROOT / f"tests/{a.project_prefix}.Testing/DeckardII.Testing.csproj",
        ROOT / f"tests/{a.project_prefix}.Testing/{a.project_prefix}.Testing.csproj",
    ),
)

(ROOT / "src/DeckardII.Core").rename(ROOT / f"src/{a.project_prefix}.Core")
(ROOT / "tests/DeckardII.Core.Tests").rename(ROOT / f"tests/{a.project_prefix}.Core.Tests")
(ROOT / "tests/DeckardII.Testing").rename(ROOT / f"tests/{a.project_prefix}.Testing")

for old, new in moves:
    old.rename(new)

framework = {
    "schemaVersion": 1,
    "framework": {
        "id": a.project_id,
        "name": a.project_name,
        "prefix": a.project_prefix,
    },
}
(ROOT / "framework.json").write_text(json.dumps(framework, indent=2) + "\n", encoding="utf-8")

subprocess.run(
    [
        "dotnet",
        "restore",
        str(ROOT / f"tests/{a.project_prefix}.Core.Tests/{a.project_prefix}.Core.Tests.csproj"),
        "--force-evaluate",
    ],
    cwd=ROOT,
    check=True,
)

print(f"Initialized {a.project_name}")
print(f"Prefix: {a.project_prefix}")
print(f"Repository: {a.repo}")
