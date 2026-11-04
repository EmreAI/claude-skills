# Format of `_text/INDEX.md`

INDEX.md is the map Claude reads before opening any text copy. It must be small enough to read in full (as a guide: about 8 lines per file) and precise enough to jump to the right pages.

Build each entry from the text copy (`_text/<path>.<ext>.md`). The flags in the `## Page N [visual …]` headers tell you where the visuals are. Use the exact terms from the material so grep finds them.

## Template

```markdown
# <Course name>: index

Updated <YYYY-MM-DD>. Pages are the `## Page N` / `## Slide N` sections of the text copies in `_text/`.
Visual pages are flagged in the copies; look at the original when a question depends on them.

## Sessions

| # | Date | Topic | Files |
|---|---|---|---|
| 1–2 | 09 Sep | Course overview, intro to optimization | Slides/Session 1 and 2 …pdf |
| 3–4 | 16 Sep | Linear programming | Slides/Session 3 and 4 …pdf · Excel Templates/S34_* |

## Assignments and exams

| What | Due / date | Files | Solution |
|---|---|---|---|
| Assignment 1 (group, 20 %) | 14 Oct | Exercises/Assignment 1.pdf | none |
| Exercise on online solver | in class S2 | Exercises/Exercise on online solver.pdf | Solutions/… |

## Files

### Slides/Session 7 Integer Programming.pdf
Text: `_text/Slides/Session 7 Integer Programming.pdf.md` · 57 pages · session 7
What: integer and binary (0–1) models in Excel Solver, from graphical solution to fixed-cost and capital budgeting models.
- p. 2–3 0–1 variables, IP vs LP, why Solver is slower on IP
- p. 4–10 graphical IP solution, rounding vs true integer optimum
- p. 13–16 branch and bound
- p. 40–54 fixed cost model (Great Threads): binary logic, effective capacity, Solver setup, sensitivity
- p. 55–57 why IF functions fail in Solver
Visuals: p. 4–10 feasible regions · p. 13–16 branch-and-bound tree · p. 54 sensitivity chart
Practice: Great Threads → `Excel Templates/S7_Fixed_Cost_Manufacturing.xlsx`

### Excel Templates/S7_Fixed_Cost_Manufacturing.xlsx
Text: `_text/Excel Templates/S7_Fixed_Cost_Manufacturing.xlsx.md` · 2 sheets · session 7
What: Great Threads fixed-cost model template; inputs, binary rent variables, Solver settings in "Defined names".

## Topic finder

Alphabetical. Term → where it is explained (file short name, pages).

- binary variable / 0–1 variable → S7 p. 2–3, 41–47
- branch and bound → S7 p. 13–16
- effective capacity → S7 p. 46
- shadow price → S3-4 p. 30–33; S12 template
```

## Rules

- One `### <relative path>` entry per converted file, in folder order. Group exam papers, readings and notebooks the same way.
- **What** is one sentence in plain words. Then the topics as page ranges, at the level of a question a student would ask (not every slide title, not one line for the whole deck).
- **Visuals** lists only the visuals that carry content (charts, diagrams, model screenshots, frameworks), not logos or photos.
- **Practice / Solution** links exercises, templates, solutions and notebooks that belong together. Matching names (`S34_*` ↔ sessions 3–4) and the syllabus help.
- Readings and cases: authors, year, the core argument in one line, the sections with page ranges.
- Notebooks and code: what each section does and which data files it needs.
- **Topic finder:** concepts, formulas, models, frameworks, cases, companies, authors, functions (`SUMPRODUCT`, `pd.merge`). Include the synonyms students use and both languages when the course mixes them.
- Do not copy content into the index. It points; the text copies hold the content.
- When a file changes, replace its whole entry and its topic-finder lines. When a file is removed, delete them.
- If a file failed to convert, list it under **Files** with `Not converted: <reason>`, so Claude knows to open the original.
