# Answering course questions with few tokens, without losing quality

## Lookup ladder

Go down only as far as the question needs.

1. **CLAUDE.md** (already loaded) tells you which session, file or folder is likely.
2. **`_text/INDEX.md`** gives files and page ranges per topic. It is small, so reading it in full is fine. For a single term, grep it.
3. **Grep the text copies** for the term, its synonyms and the course's own wording:
   `grep -rn -i "shadow price" _text --include=*.md`
4. **Read only the needed sections.** Find the line numbers of the `## Page N` headers (`grep -n "^## Page" "<copy>"`) and read that range with offset and limit. Three to ten pages is normal. Read a whole deck only when the user asks about the whole session.
5. **Look at the original page** when one of the cases below applies.
6. **Answer.**

Do not re-read what is already in this conversation. Do not open an original PDF in full when its text copy exists.

## When to look at the original page

The text copy loses layout, images and some symbols. Look at the page itself when any of these is true:

- The page is flagged `[visual …]` and the question touches what is on that page.
- The question is about a graph, chart, plot, curve, axis, figure, diagram, tree, network, matrix, timeline, framework drawing, screenshot or Excel screen, or it says "on slide 12" or "what does this show".
- A formula matters and the text may have lost symbols: `≤` shown as `<`, subscripts flattened (`x1` for x₁), exponents on their own line, fractions split over two lines, math italic letters (`𝐴𝑣𝑎𝑖𝑙`) or empty gaps where an equation was.
- Numbers for a calculation come from a table whose rows or columns look jumbled in the text.
- The page says `_(no text)_`, or the file header says it looks scanned.
- The text contradicts itself, reads garbled, or the answer would rest on a single unclear line.
- The user asks you to check the slide, or the question is about an exact exam definition that is cheap to verify.

How:

```bash
python3 "<course>/_text/_tools/course_sync.py" render "<original file>" 12,14 --out "<scratch dir>"
```

Then read the PNG(s). Render only the pages you need. If rendering fails, use the Read tool on the PDF with its pages option. For PowerPoint files without LibreOffice, `render` extracts the slide's pictures instead. For images (`.png`, `.jpg`), view the file directly.

## Save what you saw

After looking at a page image, write one to four lines under that page's section in the text copy, before the next `## ` header:

```
> Note (from page image): Graphical LP. Feasible region bounded by 4x1+5x2≤20 (green) and 10x1+7x2≤35 (blue); optimum at x1=1.59, x2=2.73; dashed red = objective line.
```

Write what the visual adds: what is plotted, axes, key values, the takeaway, corrected formulas. Skip logos, photos of people and decorative images. `sync` keeps every line starting with `>` when it re-converts a file. Next time, the note answers the question without the image. If the question needs more detail than the note gives, look again.

For a standalone image file, view it once and write the note under `## Image` in its stub.

## Answer

- Base the answer on the course material. Use the course's definitions, notation, model names and steps, even when a textbook would do it differently.
- Cite file and page: *(Session 7 slides, p. 4)*. Several sources are fine.
- If general knowledge adds something useful, mark it as going beyond the course.
- If the material does not cover the question, say so, then answer from general knowledge if that helps, clearly marked.
- Exercises: INDEX.md maps exercises to their solutions. When the user is practising, do not reveal a solution unless asked. Give hints first if they want to try.
- Excel models: the text copy has values, formulas and Solver settings. For formatting, colours or a chart's look, open the file or ask the user for a screenshot.
- Graded work: follow the AI policy noted in CLAUDE.md.

## Keep the base current

At the start of course work, if no hook did it, run `status`. If it lists anything new, changed, removed or not indexed, run the Sync steps from the skill first. It costs one command and keeps the index honest.
