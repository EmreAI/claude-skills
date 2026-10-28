# Design and slide grid

Claude builds the slides with its own tools: the Slides artifact type or the pptx skill. This file is the blueprint for content slides. Follow it exactly, so every deck has the same structure and the team recognises it. The colours below are those of the Clean theme. The other themes in `themes.md` swap the colour tokens and restyle the cover, agenda, dividers and closing slide, but they keep this grid.

## Canvas

- 16:9. The numbers below are in px on a 1920 × 1080 canvas. In PowerPoint, 1 px is 0.5 pt for font sizes and 13.333 in / 1920 for positions.
- Side margins are 128 px, so the content width is 1664 px.
- The background is off-white `#FDFDFC` and the text is ink `#1B1F24`.

## Content slide grid

Every content slide sits in a fixed frame. A **header band** holds the tracker, the team label at the top right, the action title and the optional logo, and ends with a **top rule**. A **bottom rule** sits above a slim **footer** with the source and the page number. The two rules span the content width, so the content never runs to the edges of the slide and every slide has the same structure.

The zones keep their position even when they are empty, so titles and exhibits never jump between slides.

| Zone | Top (px) | Height (px) | Content | Style |
|---|---|---|---|---|
| Tracker | 64 | 32 | Section name, for example "WHY PORTO", at the left | 24 px, semibold, uppercase, letter-spacing 2 px, accent colour |
| Team label | 64 | 32 | "Team · Course" at the right, right-aligned to x 1792, at most 600 px wide | 24 px, muted grey |
| Action title | 104 | 116 | One sentence, at most two lines | 48 px, bold, line-height 1.2, title colour of the theme. 1664 px wide, or 1404 px if a logo sits on the right |
| Logo (optional) | 112 | at most 56 | The company's logo, right-aligned at x 1792, below the team label | Height 48 to 56 px, width at most 220 px (`themes.md`, Logo) |
| **Top rule** | 244 | 3 | Full content width, x 128 to 1792 | A gradient from the theme's title colour to its accent (see `themes.md`) |
| Exhibit header | 268 | 44 | What is shown, the unit and the period | 26 px, semibold, muted grey `#5F6773`, no rule of its own |
| Exhibit | 340 | to about 840 | Chart, table, KPIs, columns, quotes or steps | See below |
| Callout or team input | above the notes | about 110 | Optional boxes, side by side if both are used | See below |
| Footnotes | bottom ends at 900 | 32 per line | "1. …" lines only | 24 px, muted grey |
| **Bottom rule** | 932 | 1 | Full content width, x 128 to 1792 | `#D5D9DE` |
| Footer | 952 | 32 (64 for a two-line source) | Left: "Source: …", always starting at y 952 and at most 1400 px wide, one or two lines. Right: page number | 24 px, muted grey |

Nothing in the content area goes below 900 px. Below the bottom rule there is only the footer, so the source always sits at the same height on every slide, whatever the slide holds. Slides without a source leave that space empty. Keep the source to one line where possible and never more than two.

In Claude Slides, draw the rules as pinned painted `<div>`s (3 px and 1 px high), and pin the team label, the source and the page number as text with a fixed `top`, so they never move. In PowerPoint, draw them as thin rectangles, not as text underlines. Put the frame on the slide master if the pptx skill supports it, so the team gets it on new slides too.

## Exhibit styles

- **Bar and column charts.** The bars the title talks about are in the accent colour and all others are grey `#C3C8D0`. Values sit directly on or above the bars (26 px, semibold). There is no value axis and there are no gridlines. Category labels are 24 px muted grey. A legend appears only with several series, at the top left.
- **Line charts.** The main line is in the accent colour and 5 px wide, and context lines are grey and 3 px wide. Each line has its name and last value at its right end, so no legend is needed. Gridlines are light grey with 4 to 5 ticks.
- **Stacked charts.** Segments are accent, a light accent tint and grey. Values sit inside the segments in white or ink. The legend is at the top.
- **Waterfall.** Totals are in the accent colour, increases in a light accent tint and decreases in muted red `#C36A58`. Changes are labelled with a sign (+120, −380).
- **KPIs, number row.** Two to four columns, each with a 6 px accent rule on top, the value in the accent colour (128 px for 2 KPIs, 112 px for 3, 92 px for 4), the label at 30 px bold and the context at 26 px muted. At most one big-number slide per deck (`exhibits.md`, Variety).
- **KPIs, hero number.** One number at 200 px bold in the accent colour on the left (about 45% of the width), vertically centred in the exhibit zone. On the right, the label at 36 px bold and the context at 28 px muted, separated from the number by a 4 px accent rule running vertically. This layout looks deliberately different from the number row. It counts as the deck's one big-number slide.
- **Key number on a chart.** At the top of the takeaways column, the value at 88 px bold in the accent colour with its label at 26 px muted underneath. Then up to two takeaways follow.
- **Table.** The header row is light grey `#F4F5F7` and bold, the body is 26 px and the highlighted row has a light accent tint with its first cell bold. There are thin horizontal rules only.
- **Columns.** Each column has a 4 px accent rule on top, an optional tag (24 px, uppercase, accent), a heading (32 px bold) and a body or bullets (26 px). A highlighted column gets a light accent tint as its background.
- **Quotes.** Cards on light grey with a 6 px accent bar on the left. The quote is 30 px in quotation marks and the speaker is 24 px muted.
- **Steps.** Numbered accent circles (64 px) joined by a grey line. Each step has a label (24 px uppercase accent), a heading (30 px bold) and a body (24 px muted).
- **Library exhibits.** Fifteen consulting exhibits (competitor benchmark, positioning matrix, SWOT, Five Forces and more) are ready as templates in `assets/exhibits/`, already built on this grid. See `exhibit-library.md`.
- **Takeaways next to a chart.** A 520 px column on the right with up to 3 points at 28 px, each with a small accent bar on its left. The chart takes the rest of the width.

## Boxes

- **Callout.** A light accent tint with a 6 px accent bar on the left. The label "SO WHAT" is 24 px uppercase in the accent colour, and the text is 28 px semibold.
- **Team input.** A dashed 2 px amber border `#D98A1E` on pale amber `#FFF7E8`. The label "TEAM INPUT" is 24 px uppercase in `#B45309`, and the text is 28 px. It must stay visible, so the team cannot miss it.
- **Inline markers.** `[TEAM: …]` is shown bold in `#B45309` and `[DATA MISSING: …]` bold in `#B42318`.

## Other slide types

- **Title slide.** Follows the cover layout of the chosen theme in `themes.md`, including logo, decorative graphic and optional photo. In Clean, it has a 28 px accent bar along the left edge and concentric accent arcs at the bottom right. The course is 24 px uppercase in the accent colour, the title 80 px bold, the subtitle 36 px muted, and team and date 28 px semibold.
- **Closing slide.** Same look as the cover (`themes.md`). One line ("Questions?" or "Thank you") at 80 px, then the team names at 28 px.
- **Summary, agenda and sources** use the same frame as content slides (header band with team label, both rules, footer with page number).
- **Summary.** The same top zones as a content slide, with the core message as the title. Below it come numbered rows (accent number, 30 px text) separated by thin rules.
- **Agenda.** The title is "Agenda". The items are 36 px and numbered 01, 02 … in the accent colour, separated by rules. If one item is active, the others turn grey.
- **Section divider.** In Clean, it has an accent background with the number at 120 px in white at 60% opacity and the title at 72 px bold in white. Midnight, Classic and Company colours use their dark background and decorative graphic (`themes.md`).
- **Sources.** The title is "Sources". The list shows ID, organisation, document, date and link at 24 px.

## Theme, logo and images

See `themes.md` for the four themes (Clean, Midnight, Classic, Company colours), their colour tokens and fonts, the decorative graphics, the company logo and the use of photos.

### Finding a company's brand colour (Company colours theme)

1. Use the company's brand guidelines or press kit if the material includes them. Otherwise use the colour you reliably know from its logo, or look it up on the company's own site. Looking up a colour is design work, not content research, so it is allowed.
2. The accent needs at least 3:1 contrast against white. Very light brand colours (yellow, light green) become the tint, and a darker shade becomes the accent.
3. If you are unsure about the brand colour, use Clean and say so.

## Fonts

The fonts depend on the theme (`themes.md`). Arial is used in PowerPoint, because it is available on every computer and in Google Slides. Never go below 24 px (12 pt). If text does not fit, shorten it.
