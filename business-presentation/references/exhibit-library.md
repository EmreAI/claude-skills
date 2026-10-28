# Exhibit library

Fifteen ready-made consulting exhibits for business group projects. Each one is a complete content slide in the Claude Slides format, with the frame from `design.md` (tracker, team label, action title, top rule, exhibit header, bottom rule, footer with source and page number). They use the Clean colours and only simple shapes and our own line icons, so there are no licence issues.

- **Template:** `assets/exhibits/<name>.html` is one `<section>` that can be copied into the deck.
- **Preview:** `assets/exhibits/previews/<name>.png` shows what the slide looks like. Open it when choosing an exhibit.
- **Placeholder content:** All text and numbers in the templates are fictional examples. Replace every word and every number with the deck's own content. Nothing from a template may stay on a slide.

## When to use which

| Pattern | Use it when the title says... | It needs |
|---|---|---|
| `competitor-benchmark` | how players compare across several criteria | 3 to 5 players, 4 to 6 criteria, a rating per cell (Harvey balls 0 to 4) |
| `positioning-matrix` | where players stand on two dimensions, or where a gap is | 2 axes with clear low and high ends, 3 to 6 players, 2 to 3 explanations |
| `market-sizing` | how big the market is and what share is reachable | TAM, SAM and SOM values with a definition of each |
| `market-growth` | how fast the market grows and why | 5 to 8 yearly values (forecast marked F), the growth rate, 3 drivers, 1 takeaway |
| `company-profile` | what a company is, in numbers and recent moves | 4 to 6 facts, a revenue split, 2 to 4 dated developments |
| `swot` | what the company's position is overall | 2 to 4 points for each of strengths, weaknesses, opportunities and threats |
| `five-forces` | why the industry is (not) profitable | a rating (high, medium, low) for each force, 2 to 3 implications |
| `pestel` | which outside trends matter most | 1 to 3 points and an impact rating for each factor |
| `value-chain` | where a company creates value or differs | the activity where it differs, examples per activity |
| `issue-tree` | which driver or lever matters most | a value broken into 2 levels of drivers, 1 lever per leaf |
| `scoring-model` | which option is best on weighted criteria | 3 options, 4 to 6 criteria with weights, a score of 1 to 5 per cell |
| `pros-cons` | what speaks for and against one option | 2 to 4 criteria with pro and contra points each |
| `risk-matrix` | which risks matter and how to handle them | 3 to 6 risks with likelihood, impact and a mitigation |
| `scr` | why a decision is needed now (often slide 2 or 3) | situation, complication and resolution in 1 to 2 points each |
| `interview-findings` | what interviewees or survey respondents said | 1 or 2 questions, n, counts per answer, 1 headline result per question |

Examples from a strategy case such as "Xbox 2020 to 2026":

- A comparison of Xbox, Sony and Nintendo on model, exclusives, subscription and profit becomes `competitor-benchmark`.
- The roles Xbox tries to play at once (platform, publisher, subscription) become `positioning-matrix`, with the business-model dimensions as axes.
- The strategic options Xbox did not take become `scoring-model` or `pros-cons`.
- "What worked and what did not" becomes `swot` or `pros-cons`.

## How to adapt a template

1. **Copy the whole `<section>`** into the deck and give it the slide's own `id`.
2. **Replace the text.** The tracker, action title, exhibit header, every label, every number, the team label, the source line and the page number all come from the deck plan. Keep the template's structure: the same zones, the same element types and the same sizes.
3. **Change the number of rows or items** by copying or deleting a repeated block (a grid row, a card, a list item). Stay inside the limits in the table above. If content does not fit, split the slide. Never shrink fonts below 24 px.
4. **Ratings.** Harvey balls are small inline SVGs. A quarter is `q` from 0 (empty) to 4 (full). Copy the ball with the right `q` from the template. Always keep the legend, and add a footnote on how the ratings were made (for example "team assessment based on S2 and S4").
5. **Theme colours.** The templates use the Clean tokens. For another theme, replace them everywhere in the copied section, including inside SVGs.

| Clean token | Used for | Replace with (`themes.md`) |
|---|---|---|
| `#2B59C3` | accent: highlighted column, bars, badges, tracker | the theme's accent on light slides |
| `#A8BCEB` | light accent: second series, forecast, mid ratings | the theme's light accent tint |
| `#E9EEF9` | tint: highlighted column background, takeaway boxes | the accent mixed 90% with white |
| `#6F8FD8` | middle step in the risk heat grid | between accent and light accent |
| `#1B1F24` | ink, and the start of the top rule gradient | the theme's title colour |

   Grey tokens (`#4A5462`, `#5F6773`, `#C3C8D0`, `#E1E4E8`, `#F4F5F7`) stay the same in every theme. In Classic, also set the `<h2>` title to the serif font.
6. **Logo.** If the deck has a logo in the header band, add it at the top right as `design.md` describes, and keep the title within 1404 px.
7. **Highlight one thing.** Every template highlights exactly one element (the company's column, the recommended option, the biggest lever). Move the highlight to whatever the action title talks about.

## Rules

- Use a library exhibit when the title compares players, options, forces, risks or drivers. Do not fall back to a plain table or a number row when one of these patterns fits.
- Use each pattern at most once per deck. It is fine to use several different patterns.
- Frameworks (SWOT, PESTEL, Five Forces, value chain) carry the team's assessment. The source line says so, and an open judgement gets a `[TEAM: ...]` marker.
- Do not add decorative icons. The templates only use icons where they help reading (the SCR markers). If more icons are needed in Claude Slides, use the built-in `<x-icon>` set.
