# Exhibits: how to show data and information

The exhibit is the proof of the title. Choose it after the title, never before. The question to ask is: what does the audience need to see to believe this sentence?

## The message decides the exhibit

| What the title claims | Exhibit | Spec |
|---|---|---|
| A ranking, or one item stands out from others | Horizontal bar, sorted, the item in question highlighted | `chart` with `bar` |
| A change over time, with few points (≤ 8) | Columns, the relevant years highlighted | `chart` with `column` |
| A trend over time, with many points or several lines | Line, with the important line in the accent colour and the others grey | `chart` with `line` |
| Shares of a whole, or a mix that changes | 100% stacked bar or column (values in %) | `chart` with `stacked_bar` or `stacked_column` |
| How we get from A to B (profit bridge, cost build-up) | Waterfall | `chart` with `waterfall` |
| Players compared on several criteria | Competitor benchmark with Harvey balls | `library`: `competitor-benchmark` |
| Where players stand, or where a gap in the market is | Positioning matrix (2 × 2) | `library`: `positioning-matrix` |
| How big the market is and what is reachable | TAM, SAM, SOM | `library`: `market-sizing` |
| How fast a market grows and why | Column chart with growth rate, drivers and takeaway | `library`: `market-growth` |
| What a company is, in facts and recent moves | Company profile | `library`: `company-profile` |
| The overall position of a company | SWOT | `library`: `swot` |
| Why an industry is or is not profitable | Porter's Five Forces | `library`: `five-forces` |
| Which outside trends matter | PESTEL | `library`: `pestel` |
| Where a company creates value or differs | Value chain | `library`: `value-chain` |
| Which driver or lever matters most | Issue tree | `library`: `issue-tree` |
| Which option is best | Scoring model | `library`: `scoring-model` |
| What speaks for and against one option | Pro and contra | `library`: `pros-cons` |
| Which risks matter and how to handle them | Risk matrix with mitigation | `library`: `risk-matrix` |
| Why a decision is needed now | Situation, complication, resolution | `library`: `scr` |
| What interviewees said, as counts | Interview findings | `library`: `interview-findings` |
| One number carries the whole slide | Hero number, with one large number and its explanation | `kpis` with 1 number (at most one big-number slide per deck) |
| A number plus the trend or comparison behind it | Chart with a key number above the takeaways | `chart` with `key_number` |
| Two to four numbers about the same thing that make the point together | Number row with context | `kpis` with 2 to 4 numbers (at most one big-number slide per deck) |
| A comparison that fits none of the library patterns | Table, with the key row highlighted | `table` |
| Parallel qualitative points that fit no framework | Columns | `columns` |
| What interviewees or customers say | Quotes | `quotes` |
| A process, timeline, roadmap or next steps | Steps | `steps` |

The `library` patterns are complete consulting exhibits with previews (`exhibit-library.md`). Prefer them over a plain table or columns whenever the title compares players, options, forces, risks or drivers.

Pie charts are not offered. A stacked bar with labels shows shares more precisely. Scatter plots and images are not supported yet. Use a table or describe the relationship in a chart that is supported.

## Variety

An audience notices a repeated layout immediately. Three slides in the same look make a deck feel generated, even if every slide is correct on its own.

1. **Big numbers once.** A big number on its own says little and quickly reads like advertising. Use **at most one big-number slide per deck** (`kpis`, as a hero number or a number row), and at most one `key_number` on a chart. Everything else shows the number in context: in a chart, a table or a library exhibit.
2. **No two consecutive slides with the same text exhibit.** This covers kpis, quotes, columns, steps, table and the library patterns. Charts may follow charts, but vary the chart type when the message type changes.
3. **No exhibit type on more than a third of the content slides**, except charts.
4. **Check the plan as a sequence.** Before building, list the exhibit of every slide in one line, for example `chart, kpis, chart, table, quotes, chart, steps`. If a pattern repeats, change the exhibit, not the message.

### When you want a big number

| Situation | Better exhibit |
|---|---|
| Two numbers compared with each other, for example 34M Xbox against 95M PS5 | Bar chart with two bars and the subject highlighted |
| One striking number, for example "6 of the 10 top-selling games" | Bar chart of the top 10 with the six highlighted, or the one hero number of the deck |
| Numbers about several competitors | `competitor-benchmark` or a bar chart |
| A number and how it developed | Column or line chart with `key_number` above the takeaways |
| Numbers about different things on one slide | Split the slide, or use a table with the key row highlighted |
| A number someone said, for example a figure from a CEO memo | Quote slide with the number inside the quote |
| Numbers that describe a profile (size, staff, markets) | Table with two columns (metric, value) |

## Rules for charts

1. **One message per chart.** If the chart shows two things, the title can only claim one of them. Remove the rest or make a second slide.
2. **Highlight what the title talks about.** That item gets the accent colour and everything else is grey. With no highlight, every bar is in the accent colour, which says "all equal".
3. **Label the data directly.** Values sit on or next to the bars. The value axis is hidden for bar and column charts. A legend appears only for multi-series bar and column charts.
4. **Sort bars** by value unless the categories have a natural order (time, age groups, size classes).
5. **Bars start at zero.** Never cut the value axis of a bar chart.
6. **The exhibit header** says what is shown, the unit and the period, for example "Revenue by segment, 2020–2024, €M" or "Share of respondents, n=212, %". The unit lives in the header and in `suffix`/`prefix`, never only in the footnote.
7. **Round sensibly.** Use `decimals` so that the chart shows no more precision than the data supports, usually 0 for percentages and 1 for millions.
8. **Few categories.** Use at most 10 bars or 12 columns. Group the rest as "Other".
9. **Comparable numbers only.** Use the same year, definition and currency for every bar. Otherwise footnote the difference.

## Rules for text exhibits

- **Takeaways** (next to a chart) are at most three short sentences that add something the chart cannot show, such as a reason, an example or a consequence. They never repeat the title.
- **Columns** need parallel headings (all nouns, or all short sentences) and parallel content.
- **Tables** have at most 6 columns and 8 rows. The first column is the item, the others are the criteria. Highlight the row the title is about.
- **Quotes** are exact words from the material with a description of the speaker ("Store manager, Lisbon"). Do not paraphrase inside quotation marks and do not use real names unless the material does.
- **KPIs** always have context: compared to what, and in which period. "€2.1M" alone means nothing. "€2.1M lost revenue from churn in 2024" does.
- **Key number** (`key_number` on a chart) is the one figure the audience should remember from the chart, such as the growth rate or the gap. It must come from the chart's data or the ledger, and it replaces one takeaway.

## Callout and team input

- **Callout** (optional) is one sentence that draws the conclusion from the exhibit, when the title alone cannot carry it. Use it rarely.
- **Team input** (`team_input`) is a dashed box with a prompt for the team, for example "Which of the two options fits your case discussion? Add your reasoning." Use it where the material leaves a judgement open. It is visible on purpose, so the team cannot forget it.
- **Inline markers.** `[TEAM: ...]` and `[DATA MISSING: ...]` can be placed inside any text and are shown in colour.

## Sources and footnotes

- Every data slide has `sources`. Own data counts too, for example "Team survey, n=48, March 2026" or "Team calculation based on S2".
- Use footnotes for definitions, derivations and exceptions, at most three per slide.
- The last slide of the deck is a `sources` slide that lists every source in full.
