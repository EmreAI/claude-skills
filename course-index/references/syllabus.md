# Getting the syllabus

The syllabus tells Claude how the course works: what is covered when, how it is graded, what the exam looks like, and what is allowed. Every later answer is better with it.

## 1. Look for it

- In the folder, by name: `syllabus`, `course outline`, `course description`, `course guide`, `programme`, `program`, `Modulhandbuch`, `Modulbeschreibung`, `Kursbeschreibung`, `Kursinfo`, `Leistungsnachweis`, `ficha`, `programa`. Search the text copies: `grep -rli "syllabus\|assessment\|grading\|Prüfung\|Leistung" _text --include=*.md`.
- The first session's slides often contain the schedule and grading.
- If a connector for the user's learning platform is available (Moodle, Canvas, Blackboard, Ilias …), offer to fetch the syllabus from there. Ask before downloading anything.

## 2. Ask the user

If nothing is found, ask once, in one short message:

> I couldn't find a syllabus. Do you have one? Put the PDF into the course folder or paste the text here. If not, I'll take what I can from the first session's slides.

If the user pastes text, save it as `_text/SYLLABUS-source.md` so it is not lost.

If the syllabus leaves out something important (exam format, exam date, grading weights), ask for just those items, at most three, in one message. If the user does not know, write `unknown` and move on. Never invent dates, weights or rules.

## 3. Write `_text/SYLLABUS.md`

Short and factual, with the page of the syllabus a fact comes from where useful.

```markdown
# <Course name>: syllabus digest

Source: `General/Syllabus-2773.pdf` (or: pasted by the user on <date>, or: taken from Session 1 slides). Updated <date>.

## Course
Code · term · ECTS · lecturer(s) and contact · TA · language · class times and room

## Learning objectives
- three to six short lines

## Schedule
| # | Date | Topic | Readings / prep | Due |
|---|---|---|---|---|

## Assessment
| Component | Weight | Format | Date / due | Notes |
|---|---|---|---|---|
| Final exam | 50 % | written, closed book, 2 h, MCQ + problems | 18 Dec | formula sheet allowed |

Pass rules, minimum grades, retake, group work rules, participation.

## Readings
Required / optional, with the file in this folder where there is one.

## Policies
Attendance · late submissions · **AI use** (quote the rule) · academic integrity · materials allowed in the exam.

## Exam scope
What is in and out, if stated.
```

## 4. Carry the essentials into CLAUDE.md

One line each: exam format, date and weight; the other graded components; the AI policy if it restricts anything; the schedule table (compact). Everything else stays in SYLLABUS.md.
