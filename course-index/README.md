# Course Index

A Claude skill that makes a university course folder cheap to work with. It converts your slides, readings, exercises, solutions, notebooks and Excel models into text once, builds an index of what is where, reads your syllabus, and writes a `CLAUDE.md` so Claude knows how the course works. When new slides arrive later in the semester, it converts and indexes only those.

Later questions cost a fraction of the tokens: Claude reads the index and the three to ten pages it needs instead of whole PDFs. When a chart, diagram, formula or table matters, it still looks at the original page.

## Install

1. Download **[course-index.zip](https://github.com/EmreAI/claude-skills/raw/main/dist/course-index.zip)**. Don't unzip it.
2. In Claude, open **Settings → Capabilities** and turn on **Code execution and file creation**.
3. Under **Skills**, click **Upload skill** and choose the ZIP.

Claude Code: `unzip ~/Downloads/course-index.zip -d ~/.claude/skills/`

The skill works where Claude can open a folder on your computer: Claude Code, or the Claude desktop app with a folder attached. It needs Python 3. For PDFs it asks to install [PyMuPDF](https://pymupdf.readthedocs.io) (`pip install pymupdf`) if neither PyMuPDF nor pypdf is there.

## Use

Open your course folder and say:

> Set up this course.

Claude converts everything, asks for the syllabus if it cannot find one, builds the index and writes `CLAUDE.md`. After that, just ask questions about the course.

When new material comes in, drop it into the folder and say:

> New slides are in, sync the course.

In Claude Code you can let it do this automatically every time you open the folder (Claude offers a small hook during setup).

Tell Claude what the lecturer said ("chapter 6 is not on the exam") and it keeps that in the course notes.

## What it creates

All inside the course folder. Your own files are never changed, moved or deleted.

```
My Course/
├── CLAUDE.md                  course facts, schedule, folder map, how to answer
├── Slides/ Readings/ …        your files, untouched
└── _text/
    ├── INDEX.md               every file: topics with page ranges, key visuals, exercises ↔ solutions, topic finder
    ├── SYLLABUS.md            schedule, grading, exam format, AI policy
    ├── Slides/Week 3.pdf.md   text copy, one "## Page N" section per page, visual pages flagged
    ├── _tools/course_sync.py  the converter
    ├── .manifest.json         what was converted when
    └── .ignore                folders or files to skip
```

## How it keeps quality up

- **Visual pages are flagged.** The converter counts images and vector drawings per page and marks pages like `## Page 4 [visual: chart or diagram]`. Logos and backgrounds that repeat on every page are ignored.
- **Claude looks at the original when it matters:** charts, diagrams, tables, screenshots, formulas whose symbols may be lost in text (≤ becomes <, x₁ becomes x1), empty or garbled pages. It renders just those pages.
- **What it sees once, it writes down.** After looking at a page image, Claude adds a short note under that page in the text copy. The next question about it needs no image. Re-syncs keep these notes.
- **Answers cite file and page** and use the course's own definitions and notation.

## Supported files

| Type | What is extracted |
|---|---|
| PDF | Text per page, image and drawing counts, repeated headers and footers removed |
| PowerPoint (.pptx) | Slide titles, text, tables, speaker notes, chart data, SmartArt text, hidden slides |
| Word (.docx) | Headings as sections, lists, tables, chart data |
| Excel (.xlsx, .xlsm) | Values and formulas per cell, Solver settings, named ranges, chart data |
| Jupyter (.ipynb) | Markdown, code and short outputs |
| CSV / TSV | Header and first rows |
| Images | A stub that Claude fills with a description after viewing |
| .doc, .rtf, .odt | Via macOS `textutil` |
| .ppt, .key, .pages, .xls | Via LibreOffice, if installed |

Plain text and code files are already cheap to read, so they are left as they are.

## Token savings

Measured on two real course folders:

| Course | Files | PDF pages | Read as PDF (≈1,500 tokens/page) | As text |
|---|---|---|---|---|
| Optimization (slides, Excel models) | 29 | 310 | ≈465,000 | ≈50,000 (11 %) |
| Technology Strategy (slides, readings) | 13 | 178 | ≈267,000 | ≈72,000 (27 %) |

A single question usually touches the index plus a few pages, so it costs a few thousand tokens. `course_sync.py stats` shows the numbers for your folder.

## How it's built

```
course-index/
├── SKILL.md                         setup, sync and answer workflows
├── scripts/course_sync.py           converter, incremental sync, page renderer
└── references/
    ├── answering.md                 lookup ladder, when to look at the original, page notes
    ├── index-format.md              format of INDEX.md
    ├── syllabus.md                  finding, requesting and digesting the syllabus
    ├── claude-md-template.md        the CLAUDE.md written into the course folder
    └── hook.md                      optional auto-sync at session start
```
