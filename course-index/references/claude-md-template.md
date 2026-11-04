# CLAUDE.md template

CLAUDE.md is loaded into every session in this folder, so each line costs tokens every time. Aim for 40–80 lines. Fill in the placeholders, drop lines that do not apply, and keep the answering and sync sections almost word for word: they are what keeps answers cheap and accurate.

Use the absolute course path in the commands, so they work from any working directory.

If the folder already has a CLAUDE.md, keep everything outside the markers and replace only what is between them.

```markdown
<!-- course-index:start (managed by the course-index skill; text outside this block stays untouched) -->
# <Course name> (<code>, <school>, <term>)

<One sentence on what the course is about.>
Lecturer: <name> · Language: <language> · Syllabus digest: `_text/SYLLABUS.md`
Grading: <exam 50 % (written, closed book, 18 Dec)> · <group project 30 %> · <participation 20 %>
<AI policy, only if it restricts something: "Graded assignments: no AI-written work. Explain and guide only.">

## Where things are
- `Slides/`: lecture slides, one deck per session (`Session N …`)
- `Readings/`: articles and cases
- `Exercises/`, `Solutions/`: problem sets and their solutions
- `<other folders>`: <one line each>
- `_text/`: text copies of every file (same path + `.md`, sections `## Page N`). `_text/INDEX.md` maps topics → files → pages.

## Schedule
| # | Date | Topic | Material |
|---|---|---|---|
| 1 | 09 Sep | <topic> | Slides/Session 1.pdf |

## Answering questions about this course
1. Find the place in `_text/INDEX.md` (topics → file → pages), or grep `_text/`.
2. Read only those `## Page N` sections of the text copy, never the whole original PDF.
3. Look at the original page when it matters: the page is flagged `[visual …]` and the question touches it; charts, diagrams, graphs, tables or screenshots; formulas whose symbols may be lost (≤ shown as <, x1 for x₁); `_(no text)_` or garbled pages. Render only those pages:
   `python3 "<abs course path>/_text/_tools/course_sync.py" render "<file>" <pages> --out "<scratch dir>"` and read the PNG.
4. After looking at a page image, add `> Note (from page image): …` (1–4 lines) under that page in the text copy, so next time the text is enough.
5. Use the course's definitions and notation, cite file and page, and say when something is not in the material. Do not reveal exercise solutions unless asked.
More detail: the course-index skill's `references/answering.md`.

## New material
Before course work, run `python3 "<abs course path>/_text/_tools/course_sync.py" status`. If it lists new, changed, removed or not-indexed files: run `sync`, update `_text/INDEX.md` and the schedule above, then `mark-indexed <paths>`.

## Course notes
- <YYYY-MM-DD>: <what the lecturer or the user said, e.g. "Chapter 6 not on the exam">
<!-- course-index:end -->
```

With the auto-sync hook installed, replace the first sentence of **New material** with: "A SessionStart hook runs `sync` and reports changes. When it does:" and keep the rest.
