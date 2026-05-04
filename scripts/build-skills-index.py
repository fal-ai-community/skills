#!/usr/bin/env python3
"""
Builds skills/claude.ai/index.json by walking skills/claude.ai/<name>/ directories.

Each skill directory must contain a SKILL.md with YAML frontmatter
(`name` + `description`). All files in the directory are included in
the manifest with a sha256 hash so the CLI can verify integrity.

Run with --check to fail if the on-disk index is stale.
"""

import hashlib
import json
import os
import re
import sys

SKILLS_DIR = os.path.join("skills", "claude.ai")
INDEX_FILE = os.path.join(SKILLS_DIR, "index.json")


def sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def file_bytes(path: str) -> int:
    return os.path.getsize(path)


def walk_files(skill_dir: str) -> list[str]:
    out = []
    for root, dirs, files in os.walk(skill_dir):
        dirs.sort()
        for f in sorted(files):
            full = os.path.join(root, f)
            out.append(os.path.relpath(full, skill_dir))
    return out


def parse_frontmatter(source: str) -> dict:
    if not source.startswith("---\n"):
        return {}
    end = source.find("\n---", 4)
    if end == -1:
        return {}
    block = source[4:end]
    out = {}
    current_key = None
    folded_lines = []

    def flush():
        nonlocal current_key, folded_lines
        if current_key is not None:
            out[current_key] = " ".join(folded_lines).strip()
            current_key = None
            folded_lines = []

    for line in block.split("\n"):
        m = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', line)
        if m and not line.startswith(" "):
            flush()
            key, rest = m.group(1), m.group(2).strip()
            if rest in (">", ">-", "|"):
                current_key = key
                folded_lines = []
            else:
                out[key] = rest
        elif current_key is not None:
            folded_lines.append(line.strip())
    flush()
    return out


def build_index() -> dict:
    skills = []
    for entry in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = os.path.join(SKILLS_DIR, entry)
        if not os.path.isdir(skill_dir):
            continue
        skill_file = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(skill_file):
            raise SystemExit(f"Missing SKILL.md in {skill_dir}")
        with open(skill_file, "r", encoding="utf-8") as f:
            source = f.read()
        fm = parse_frontmatter(source)
        name = fm.get("name")
        description = fm.get("description")
        if not name:
            raise SystemExit(f"{skill_file}: frontmatter missing 'name'")
        if not description:
            raise SystemExit(f"{skill_file}: frontmatter missing 'description'")
        if name != entry:
            raise SystemExit(f"{skill_file}: frontmatter name '{name}' does not match directory '{entry}'")
        files = [
            {
                "path": rel,
                "sha256": sha256(os.path.join(skill_dir, rel)),
                "bytes": file_bytes(os.path.join(skill_dir, rel)),
            }
            for rel in walk_files(skill_dir)
        ]
        skills.append({"name": name, "description": description, "files": files})
    return {"version": 1, "skills": skills}


def main():
    check = "--check" in sys.argv
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    index = build_index()
    serialized = json.dumps(index, indent=2) + "\n"

    if check:
        if not os.path.exists(INDEX_FILE):
            print(f"{INDEX_FILE} is missing. Run: python3 scripts/build-skills-index.py", file=sys.stderr)
            sys.exit(1)
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            current = f.read()
        if current != serialized:
            print(f"{INDEX_FILE} is stale. Run: python3 scripts/build-skills-index.py", file=sys.stderr)
            sys.exit(1)
        print(f"{INDEX_FILE} is up to date.")
        return

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(serialized)
    print(f"Wrote {INDEX_FILE} — {len(index['skills'])} skills")


if __name__ == "__main__":
    main()
