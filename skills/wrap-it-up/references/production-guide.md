Every wrap produces exactly two artifacts:

1. **A ZIP archive** of the chat's generations, organized into named folders by role — never a flat dump.
2. **A `PROGRESS.md`** at the archive root following the required skeleton below.

End the turn with a one-line confirmation of what shipped (folder tree + file count).

---

## Step 1 — Build the archive with `export_generations_zip`

Use the `export_generations_zip` tool as the mechanism. It already folders by batch slug and writes a `manifest.json` with prompt / model / request-id per file, so the archive is consistent every time. Do **not** hand-stitch the ZIP in the Python sandbox unless `export_generations_zip` genuinely can't express the structure you need (e.g. you must inject extra non-generation files) — and even then, prefer exporting first and only augmenting.

- Set `zipName` in kebab-case derived from the project or chat name (e.g. `amazon-back-to-school`).
- Filter with `batchSlugs` / `mediaTypes` only if the user asked for a subset. Default is everything.

### Group by role, and by axis when one exists

"All the files" must land in **named folders by role**, not a flat pile. Standard roles:

- `final/` — the finished, deliverable outputs
- `clips/` — intermediate per-scene or per-shot clips
- `keyframes/` — stills / scene frames feeding the clips
- `source/` — input references, uploads, brand assets, logos

**Split folders along whatever axis the project actually varies on.** This is the part that makes a wrap genuinely useful. If the work spans languages, split `clips_en/ clips_fr/ clips_de/` and `keyframes/ keyframes_de/` (only fork the folders that actually differ per axis). The same idea applies to any repeating axis: platform (`final_9x16/ final_16x9/`), variant (`variant_a/ variant_b/`), or client. Read the generation set, detect the axis, and mirror it in the folder tree.

---

## Step 2 — Write PROGRESS.md (required skeleton)

Write to the archive root. Every section is required; write "None" if empty rather than dropping the heading.

```
# <Project name> — Progress

## Summary
1-3 sentences: what this project is and where it stands.

## Decisions
Bullet list of choices locked in (models, aspect ratio, tone, style, casting).

## Asset inventory
Counts + the folder each role lives in. Note the varying axis (e.g. 3 languages).
e.g. Finals: 3 (final/) — EN, FR, DE · Clips: 9 (clips_*/) · Keyframes: 6 · Source: 1

## Pipeline
Ordered steps actually taken, with the model used at each step.

## Known gaps
Anything unfinished, rough, or deliberately skipped.

## Next steps
Concrete follow-ups someone could pick up.
```

Keep filenames traceable: PROGRESS.md should reference the `manifest.json` as the map from filename → prompt + model, so a bare name like `clip2.mp4` is always resolvable.

---

## Step 3 — Confirm

Close with one short line: the folder tree, total file count, and archive size. Example:
"Zipped 20 files (~59 MB): final/ (3 cuts EN/FR/DE), clips_en|fr|de/, keyframes/ + keyframes_de/, source/, plus PROGRESS.md and manifest.json."

---

## Conventions

- **Naming:** kebab-case for the zip and all folders; derive from the project name.
- **Two-part rule:** a wrap is never just a ZIP and never just a doc — always both.
- **Structure over dump:** fork folders on the project's varying axis; a flat pile of files is a failed wrap.
- **Manifest is the index:** rely on `export_generations_zip`'s `manifest.json` rather than re-deriving prompt/model metadata by hand.
