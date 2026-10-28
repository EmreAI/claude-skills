# Deck spec (`deck.json`)

Claude writes one JSON file per deck before building anything. It is the plan that the checker tests and that Claude builds the slides from, following the grid in `design.md`. `assets/example-deck.json` is a complete example that uses every slide type.

## Top level

```json
{
  "meta": {"title": "Volta Bikes: Expanding to Porto", "subtitle": "Strategy group project", "team": "Team 4", "course": "Strategy, Nova SBE", "date": "November 2026",
           "logo": "placeholder", "cover_image": ""},
  "theme": {"name": "clean"},
  "sources": [
    {"id": "S1", "org": "Volta Bikes", "doc": "Ride data 2022–2025", "date": "2026", "url": ""}
  ],
  "slides": [ ... ]
}
```

- `meta.footer` (optional) replaces the team label at the top right of content slides. The default is "team · course".
- `theme.name` is `clean` (default), `midnight`, `classic` or `company`, as described in `themes.md`. `company` also needs `accent` (the brand colour as hex) and optionally `accent2`.
- `meta.logo` is the logo file the user gave or that was downloaded with the user's OK, or `"placeholder"` to leave an empty logo frame. Leave it out for decks without a main company.
- `meta.cover_image` (optional) is an image file or a photo library id for the cover. Leave it empty for the decorative graphic only.
- `sources` lists every source once. Slides refer to them by `id`. A slide can also name a source in plain text, for example `"Team survey, n=212"`.

## Fields every content slide can have

| Field | What it is |
|---|---|
| `id` | Optional stable id (letters, digits, `-`, `_`). Keep ids stable across rounds. |
| `type` | The slide type (below). |
| `tracker` | Small label above the title, usually the section name (max 40 characters). Slides with the same tracker form a section. |
| `title` | The action title (see `action-titles.md`). |
| `header` | The exhibit header, which says what is shown, the unit and the period (max 110 characters). |
| `callout` | Optional one-sentence conclusion box under the exhibit. |
| `team_input` | Optional dashed box with a prompt for the team. |
| `footnotes` | Up to 3 short notes, numbered automatically. |
| `sources` | List of source ids or plain-text sources. Required on chart, kpis and table slides. |

Inline markers `[TEAM: ...]` and `[DATA MISSING: ...]` can go into any text and are shown in colour.

## Slide types

### `title`
The cover. It uses `meta`, so it takes no further fields.

### `summary`
```json
{"type": "summary", "tracker": "Summary", "title": "<core message of the deck>",
 "points": ["<finding or argument 1>", "<2>", "<3>"]}
```
3 to 6 points. Each point is the compressed action title of its section.

### `agenda`
```json
{"type": "agenda", "title": "Agenda", "items": ["Where we stand", "Why Porto", "How to enter"], "active": 1}
```
`active` (optional, 0-based) highlights one item, so the agenda can repeat as a section divider.

### `section`
```json
{"type": "section", "number": 2, "title": "How to enter Porto"}
```

### `chart`
```json
{"type": "chart", "tracker": "Lisbon today",
 "title": "Lisbon rides tripled since 2022, but growth slowed to 12% in 2025",
 "header": "Rides per year, Lisbon, thousands",
 "chart": {"type": "column", "categories": ["2022", "2023", "2024", "2025"],
           "series": [{"name": "Rides", "values": [140, 260, 390, 437]}],
           "highlight": [3], "decimals": 0, "prefix": "", "suffix": ""},
 "takeaways": ["Optional, up to 3 short sentences next to the chart"],
 "key_number": {"value": "+12%", "label": "Growth in 2025"},
 "sources": ["S1"]}
```
- `key_number` (optional) shows one large figure at the top of the takeaways column. With a key number, use at most 2 takeaways.
- `chart.type` is one of `bar` (horizontal), `column`, `stacked_bar`, `stacked_column`, `line` or `waterfall`.
- `series` holds up to 4 series (5 for line). Every series has as many `values` as there are `categories`. `color` per series is optional and takes `accent`, `accent2`, `grey`, `dark` or a hex value.
- `highlight` lists the category indices to show in the accent colour. Use it on single-series bar and column charts, where all other bars turn grey.
- `waterfall` takes one series of changes. `totals` lists the indices that are absolute totals (usually the first and the last). Example: `"values": [1450, -380, -120, -220, -310, 420], "totals": [0, 5]`.
- `line` shows the value at the end of each line. The first series uses the accent colour. Give context series `"color": "grey"`.
- Stacked charts expect values that add up to the total (for 100% charts, to 100).
- Negative values only work in waterfalls.
- `takeaways` puts the chart on the left and up to 3 short points on the right.

### `kpis`
```json
{"type": "kpis", "title": "...", "kpis": [
  {"value": "€4.1M", "label": "Yearly revenue potential", "context": "At Lisbon's ride price and 60% of Lisbon's usage per resident"}],
 "sources": ["S2"]}
```
1 to 4 numbers. With 1 number the slide uses the hero layout, and with 2 to 4 the number row. `value` holds at most 8 characters, and `context` is required in practice. Use at most one `kpis` slide per deck, as a hero number or a number row (`exhibits.md`, Variety).

### `library`
```json
{"type": "library", "pattern": "competitor-benchmark", "tracker": "Competition",
 "title": "Sony and Nintendo profit from own hardware and exclusives, while Xbox spreads across three roles",
 "header": "Business model comparison of the three console makers, team assessment based on S3 to S7",
 "content": {
   "players": ["Microsoft Xbox", "Sony PlayStation", "Nintendo"],
   "criteria": ["Own hardware", "Exclusive games", "Subscription", "Games on rival consoles", "Operating profit reported"],
   "ratings": [[2, 4, 4], [1, 4, 4], [4, 3, 1], [4, 1, 0], [0, 4, 4]],
   "highlight": 0, "legend": "Harvey balls from 0 (none) to 4 (very strong)"},
 "footnotes": ["Ratings are a team assessment based on the sources listed."],
 "sources": ["S3", "S5", "S7"]}
```
- `pattern` is one of the fifteen names in `exhibit-library.md`.
- `content` holds everything that goes on the slide, in whatever structure suits the pattern: labels, numbers, ratings, points and the item to highlight. The checker reads every text and number in it for the wording rules and for the numbers in the title.
- Each pattern is used at most once per deck.

### `table`
```json
{"type": "table", "title": "...", "header": "...",
 "table": {"columns": ["Option", "Time to launch", "Upfront cost"],
           "rows": [["Organic", "12 months", "€2.4M"], ["Partnership", "6 months", "€0.9M"]],
           "highlight_rows": [1], "widths": [40, 30, 30]},
 "sources": ["S2"]}
```
At most 6 columns and 8 rows. `widths` (optional) are percentages.

### `columns`
```json
{"type": "columns", "title": "...", "columns": [
  {"tag": "Risk 1", "heading": "Hills", "body": "Short paragraph", "bullets": ["or bullets", "max 5"]}],
 "highlight": 0}
```
1 to 4 columns. Use `body`, `bullets` or both. `highlight` (optional) tints one column.

### `quotes`
```json
{"type": "quotes", "title": "...", "quotes": [{"text": "Exact words", "who": "Commuter, 34, Porto"}], "sources": ["S4"]}
```
1 to 4 quotes.

### `steps`
```json
{"type": "steps", "title": "...", "steps": [{"label": "Dec 2026", "heading": "Sign partner", "body": "Short description"}]}
```
3 to 5 steps.

### `sources`
```json
{"type": "sources", "title": "Sources"}
```
Lists every entry of the top-level `sources`. Put it after the closing slide, as an appendix.

### `closing`
```json
{"type": "closing", "title": "Questions?"}
```
Same look as the cover (`themes.md`), with the team names from `meta.team`. It carries no content.

## Limits

The checker enforces the limits. The most important ones are a title of at most 120 characters (aim for 95), at most 3 takeaways, 10 bars or 12 columns, and a table of at most 6 × 8 cells. If something does not fit, shorten it or split the slide.
