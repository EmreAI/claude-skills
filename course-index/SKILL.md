---
name: course-index
description: Turns a university course folder (slides, readings, exercises, solutions, notes, notebooks, Excel models) into a token-cheap study base once, then keeps it current as new weekly material arrives. Writes text copies with page markers, a course INDEX.md with topics and page pointers, a syllabus digest and a CLAUDE.md that tells Claude where everything is and how the course works. Later questions read the index and a few pages instead of whole PDFs, and Claude goes back to the original page whenever a chart, diagram, formula or table matters. Triggers on "set up this course", "index my course folder", "new slides are in", "update the course", "sync the course", "save tokens on my course", "Kurs einrichten", "Kursordner indexieren", "neue Folien sind drin", "Kurs aktualisieren", "Tokens sparen".
---

# Course Index

Make a course folder cheap to work with, without making answers worse.

**Principle:** convert every file once, find things through an index, read only the pages a question needs, and look at the original page whenever the text is not enough.

A 50-page slide deck costs roughly 75,000 tokens when Claude reads the PDF, and about 5,000 as text. A typical question then needs the index and three to ten pages, so a few thousand tokens.

## What the skill creates

Everything lives inside the course folder, so it keeps working in any later session, even without this skill.

| Path | What it is |
|---|---|
| `CLAUDE.md` | Loaded every session. Short: course facts, schedule, folder map, how to answer, how to sync. |
| `_text/INDEX.md` | The map: every file with its topics and page ranges, key visuals, exercises and their solutions, a topic finder. |
| `_text/SYLLABUS.md` | Digest of the syllabus: schedule, grading, exam format, policies. |
| `_text/<path>.<ext>.md` | Text copy of each file, e.g. `Slides/Week 3.pdf` → `_text/Slides/Week 3.pdf.md`, split into `## Page N` (or `## Slide N: Title`, `## Sheet N: Name`) sections. Visual pages carry a flag such as `[visual: chart or diagram]`. |
| `_text/_tools/course_sync.py` | The converter, copied from this skill. |
| `_text/.manifest.json` | What was converted when. Drives the incremental sync. |
| `_text/.ignore` | Glob patterns the converter skips, e.g. `Old semester/*`. |

Claude never changes, moves, renames or deletes the user's own files. It writes only to `_text/`, to `CLAUDE.md`, and, if the user agrees, to `.claude/settings.json`.

## The converter

`scripts/course_sync.py` (Python 3.8+, standard library for Office files):

| Command | Does |
|---|---|
| `doctor` | Shows the available PDF backends. |
| `install` | Copies the script to `<course>/_text/_tools/` and creates `_text/.ignore`. |
| `status` | Lists new, changed, removed and not-yet-indexed files, plus files it cannot convert. |
| `sync` | Converts what is new or changed, detects renames, deletes text copies of removed files, keeps Claude's notes. `--clean-legacy` removes old text copies from an earlier setup without a manifest. `--hook` prints only when something needs attention. |
| `render FILE PAGES` | Renders pages (`4` or `4,7-9`) to PNG for viewing. `--out DIR` sets the folder. |
| `mark-indexed PATHS` / `--all` | Records that INDEX.md covers these files. |
| `stats` | Token estimate, originals vs text copies. |

Run it as `python3 "<skill dir>/scripts/course_sync.py" --root "<course folder>" <command>` until it is installed, then as `python3 "<course folder>/_text/_tools/course_sync.py" <command>` (it finds the course folder from its own location). On Windows use `python`.

Supported: PDF, PPTX (slide titles, speaker notes, tables, chart data, SmartArt text), DOCX (headings, lists, tables, chart data), XLSX/XLSM (values, formulas, Solver settings, named ranges, chart data), IPYNB (markdown, code, short outputs), CSV/TSV, images (stub to annotate). DOC, RTF and ODT via macOS `textutil`; PPT, KEY, PAGES, XLS via LibreOffice if installed. Plain text and code files (`.md`, `.py`, `.R`, `.tex` …) are already cheap, so they are listed but not copied.

## Which mode

Look at the course folder first:

- No `_text/.manifest.json` → **Setup**. If `_text/` exists without a manifest, it is an earlier setup: run Setup and clean the legacy copies.
- Manifest exists and the user brings new material, a hook message reports changes, or `status` lists changes → **Sync**.
- Otherwise → **Answer** questions, following the rules in CLAUDE.md.

If the working folder holds several courses (one subfolder each with its own slides), ask which one to set up, or set them up one after another. Each course gets its own `CLAUDE.md` and `_text/`.

## Setup

1. **Check the tools.** Run `doctor`. With no PDF backend, ask the user to allow `pip install pymupdf` (best: text and page rendering). If they decline, try `pip install pypdf` (text only; rendering then falls back to poppler, macOS PDFKit, or the Read tool's PDF pages option). Without either, convert only the Office files and say so.
2. **Install and look.** Run `install`, then `status`. Tell the user in one line what is there, e.g. "8 slide decks, 5 readings, 12 Excel models, 2 notebooks, no syllabus found".
3. **Convert.** Run `sync` (add `--clean-legacy` when `status` lists old copies, and say that they were generated files). Conversion takes seconds.
4. **Syllabus.** Follow `references/syllabus.md`: search the folder, offer to fetch it if an LMS connector (Moodle, Canvas …) is available, otherwise ask the user for it. Write `_text/SYLLABUS.md`. While you wait for the user's answer, carry on with step 5.
5. **Index.** Build `_text/INDEX.md` by the format in `references/index-format.md`. Read the text copies, never the originals, for this. Work file by file. With more than about 10 files and subagents available, hand each subagent a group of files plus the format and merge their entries. Then run `mark-indexed --all`.
6. **CLAUDE.md.** Write it from `references/claude-md-template.md`. If a `CLAUDE.md` already exists, keep the user's content and put the managed part between the `course-index` markers. Keep it under about 80 lines: details belong in INDEX.md and SYLLABUS.md.
7. **Offer the auto-sync hook** (Claude Code only, optional), as described in `references/hook.md`. Write it only after the user says yes.
8. **Report** in a few lines: files converted, visual pages flagged, the `stats` estimate, anything that failed or could not be converted, what is still missing (syllabus, exam date). End with how to use it: "Ask questions from this folder. When new slides arrive, put them in the folder and say *sync*."

## Sync

1. Run `sync`.
2. For each new or changed file, read its text copy and add or replace its INDEX.md entry and its topic-finder lines. For renamed files, update the paths. For removed files, delete their entries.
3. If a new session or week arrived, update the schedule in CLAUDE.md and SYLLABUS.md (e.g. mark it as covered, add the file).
4. If the output shows a section "Notes from an earlier version", the source changed under Claude's notes. Check them against the new pages (render if needed), then move them under the right page or delete them.
5. Run `mark-indexed <paths>` for the files you indexed.
6. Tell the user in one to three lines what is new, e.g. "Week 5 slides indexed: queueing models, M/M/1 formulas on p. 8–11, charts on p. 12–14."

## Answer

`references/answering.md` has the full rules, and CLAUDE.md carries the short form. In brief:

1. Find the place via INDEX.md or grep in `_text/`.
2. Read only the `## Page N` sections needed.
3. **Look at the original** when the text is not enough: flagged visual pages the question touches, charts, diagrams, tables, screenshots, formulas whose symbols may be lost, empty or garbled pages. Render just those pages.
4. After looking, add a short `> Note (from page image): …` under that page in the text copy. The next question about it then needs no image. `sync` keeps these notes.
5. Answer from the course material in the course's own notation, cite file and page, and say when the material does not cover something.

## Course notes

When the user tells you something about the course that is not in the files ("the professor said chapter 6 is not on the exam", "the exam is open book", "the group project deadline moved to 12 Dec"), add it with the date under **Course notes** in CLAUDE.md. Remove entries once they are outdated.

## Rules

- The text copies are for finding and reading. When the exact content matters (a definition, a number, a formula, what a chart shows), read the page itself, never only the INDEX summary.
- Take page numbers from the `## Page N` headers. Never guess them.
- If the syllabus restricts AI use for graded work, follow it: for graded assignments, explain and guide instead of writing the submission, and say why once.
- Write CLAUDE.md, INDEX.md and SYLLABUS.md in the language the user writes in. Keep course terms exactly as they appear in the material, so grep finds them.
- Keep CLAUDE.md short. It is read in every session, so every line costs tokens each time.
