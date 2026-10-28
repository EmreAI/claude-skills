---
name: business-presentation
description: Builds finished English slide decks for university group projects in business, data and management (case analyses, market entry, company analysis, survey or data findings, pitches) strictly from the material the user provides or from a business-research report. Writes the storyline as action titles first, puts one message and one exhibit on each slide, traces every number to a source and leaves marked space for the team's own ideas. Offers a clean look or professional themes, with the company's logo on the cover. Delivers the deck as a Claude Slides artifact that the team edits in Claude and downloads as PowerPoint or PDF. Triggers on "presentation", "slides", "deck", "pitch deck", "turn this report into slides", "make a presentation for my group project".
---

# Business Presentation

Builds a finished slide deck for a university group project from the material the user gives: notes, data, articles, reports, survey results or a report from the business-research skill. Every slide states one conclusion as an action title and proves it with one exhibit. Nothing goes on a slide that is not in the material.

## Core rules

1. **Material only.** Every number, name, quote and claim on a slide comes from the user's material or a business-research ledger. Nothing comes from memory: no typical industry values, no invented examples, no "well-known" facts. If something is missing, the slide shows `[DATA MISSING: what is needed]`.
2. **One slide, one message.** The action title states the message and the exhibit proves it. Read `references/action-titles.md` before writing any title. Titles matter more than anything else in this skill.
3. **Plan first, then build right away.** Claude plans the storyline and checks it, then builds the slides without waiting for approval. The team reviews the finished deck and the deck plan, and asks for changes afterwards. The only time Claude waits for the user is the one round of questions in Step 1.
4. **Leave room for the team.** This is a group project, so the deck is a strong first version that the team owns. Wherever the material does not settle a judgement (a recommendation, a priority, what interviews "mean"), mark it as `[TEAM: ...]` or give it a team-input box. Claude may draft a suggestion when the material supports one, but it is labelled as a draft. Never present Claude's opinion as the team's finding.
5. **Human, not consulting, and no slop.** Use plain words, short titles, few slides and plenty of white space. The deck should sound like smart students who know their material. Follow `references/writing-style.md` for every piece of slide text: no em dashes, no colon constructions, no "it's not X, it's Y", no buzzwords and no advertising language.
6. **Slides are always in English.** Chat with the user in their language.
7. **No speaker notes.**

## Step 1. Intake (one round)

Read the request and look through the attached material. Then ask **one round** of questions with the AskUserQuestion tool. If that tool is not available, ask the same thing as a short plain-text checklist. Skip any question the user has already answered. Ask at most three questions. After this round, Claude does not stop again until the deck is finished.

Do not ask about the format. The deck is always a Claude Slides artifact, which the team edits in Claude and downloads as PowerPoint or PDF from the deck's menu.

1. **Theme** (always ask). Describe each theme in one line and let the user decide (details in `references/themes.md`).
   - *Clean.* Light and simple with one accent colour. The safe choice.
   - *Midnight.* Deep navy cover and dividers with fine line waves. Content slides stay light.
   - *Classic.* Navy and white with serif titles, for a formal look.
   - *[Company] colours.* Offer this only if the deck is about one company. It uses the brand colour and the logo.
2. **What the deck has to do** (ask unless the assignment makes it clear).
   - Recommend a decision
   - Present findings of an analysis
   - Pitch an idea or business
   - Explain a topic
3. **Length** (ask unless known). About 10 minutes means 6 to 8 content slides, 15 minutes means 9 to 12, and 20 minutes or more means 13 to 18. Plan roughly one content slide per 1 to 1.5 minutes.

Two questions replace question 2 when they apply. Then infer the purpose from the material.
- **Logo**, if the deck is about one company. *Get the official logo from Wikimedia Commons (recommended)*, *I'll upload it* or *No logo*. The answer is the user's permission to download the file.
- **Thin material**, if the material cannot carry the deck. *Run business-research first*, *Build with placeholders* or *I'll add material*.

If the user says "just build it", use the Clean theme, infer the purpose, plan 10 content slides and leave a logo placeholder.

## Step 2. Plan the deck in one pass

Read the material once, then plan the storyline and its numbers together. **Do not build a separate table of every fact in the material.** Only the numbers that go on a slide matter, and they live in `deck.json` with their sources. This step should be quick.

1. Choose the storyline in `references/storylines.md` that fits what the deck has to do, and adapt it to the material.
2. Write the **core message** first: one sentence that answers the project question. It becomes the title of the summary slide. If the material does not support a single answer, the core message states what the analysis shows and the decision becomes a `[TEAM]` item.
3. Write `deck.json` as described in `references/deck-spec.md`: every slide's action title, exhibit, numbers and sources. Choose exhibits with `references/exhibits.md`. Whenever a slide compares players, options, forces, risks or drivers, use a consulting exhibit from `references/exhibit-library.md` (competitor benchmark, positioning matrix, SWOT, Five Forces, scoring model and more) and the theme, logo and cover image with `references/themes.md`. `assets/example-deck.json` shows a complete plan. `deck.json` is an internal working file for the checker and the deck plan. Keep it next to the deck for later rounds, but never show it to the user, paste it into the chat or mention it in the delivery message.
4. Rules for numbers.
   - Copy numbers exactly from the material, with their unit and period. Round only as the chart's `decimals` says.
   - **Derived numbers** (growth rates, shares, differences) are allowed if Claude computes them from numbers in the material. The slide gets a footnote, for example "Team calculation based on S2."
   - Never combine numbers with different definitions, years or currencies without a footnote.
   - If the material contradicts itself, use the more primary or more recent source, footnote the other value and list the conflict as an open item. Do not stop to ask.
   - **Business-research reports.** Use the report's evidence ledger, sources and confidence tags directly. A fact tagged *Low* never carries a title on its own. The report's *Gaps* become `[DATA MISSING]` items.
5. Run the **horizontal test**. Read only the titles from top to bottom. They have to tell the whole story, and each one has to follow from the one before.
6. Run the **variety test** (`references/exhibits.md`, Variety). There is at most one big-number slide and one key number in the whole deck, and no text exhibit or library pattern appears on two consecutive slides.

## Step 3. Check and write the deck plan

Run the checker from the skill folder. It also writes the deck plan document.

```bash
python3 scripts/check_deck.py deck.json --plan deck-plan.md
```

Fix every **error** and run it again. Go through every **warning** and either fix it or keep it deliberately. Then review each title against the checklist at the end of `references/action-titles.md`, because the script catches patterns but cannot judge meaning. If Python is not available, go through the checklists in `action-titles.md` and `writing-style.md` by hand and write the deck plan yourself, with the same sections: storyline table, open items, slide by slide with numbers and sources, and the source list.

## Step 4. Logo

Only for decks about one company, and only if the user chose Wikimedia Commons in Step 1.

1. Search Wikimedia Commons for the company's current logo (for example `site:commons.wikimedia.org "<Company> logo"`) and open the file page.
2. Take the original file (SVG or PNG) linked from that page on `upload.wikimedia.org`. Prefer the current logo over historical versions, and a version for dark backgrounds if the theme has a dark cover.
3. Upload the file to the deck as an asset, as the Slides type describes. SVG works as it is. Only for the .pptx fallback, convert an SVG to PNG at about 600 px wide.
4. Add the file page to the sources as "Logo: Wikimedia Commons, File:<name>".
5. If no suitable file is found, use a placeholder and name it as an open item. Never draw the logo yourself.

The rules for where the logo goes are in `references/themes.md`, Logo.

## Step 5. Build

Build the slides right away from the checked plan, with the tools Claude already has. Follow the slide grid in `references/design.md` exactly, so every content slide has the same frame and the titles never jump. Build the cover, agenda, dividers and closing slide in the chosen theme from `references/themes.md`, with its decorative graphic, the logo (or its placeholder) and a cover photo only if one is available under the image rules there.

Create the deck from the **Slides** artifact type (find it with the Artifact tool's `quickstart`, intent "slides") and follow that type's instructions for the file format and for publishing. This skill's content rules come before the type's design advice. Its advice that "titles introduce the topic" does not apply here, because slides carry action titles. No speaker notes.

Only if the Slides type is not available, build a .pptx with the pptx skill instead, with native PowerPoint charts and the same grid, and say so in the delivery message.

For `library` slides, open the template in `assets/exhibits/<pattern>.html` (and its preview in `assets/exhibits/previews/`), copy the section and adapt it as `references/exhibit-library.md` describes. Replace every placeholder word and number.

Copy text and numbers exactly from the plan. Do not add, round or reword anything while building. If text does not fit, shorten it in the plan, run the checker again and then rebuild that slide. Never shrink fonts below the sizes in `design.md`.

## Step 6. Show the deck plan

After the slides are built, publish `deck-plan.md` as a document artifact, so it opens next to the chat and the team can read the structure, every number and its source. In Claude Code, publish it as an artifact page with the Artifact tool. If no artifacts are available, attach the file. Do not paste the plan into the chat.

## Step 7. Deliver

The chat message is short and follows this pattern. Do not repeat the storyline or the plan in the chat.

> Your deck is ready: [deck link or file]. The slide structure is set, and on the right you can see the deck plan with every slide, its numbers and its sources.
>
> Open for your team:
> - Slide 10: decide whether the 15% revenue share fits your margin target
> - Slide 1: add your names
>
> You can edit the slides directly, and download them as PowerPoint or PDF from the deck's menu. Want changes? Just tell me, for example "slide 5: split by region".

List at most five open items (`[TEAM]`, `[DATA MISSING]`, logo or image placeholders). If there are more, write "and N more in the deck plan".

## Step 8. Further rounds

When feedback or new material comes in, update `deck.json`, run the checker with `--plan` again, change only the affected slides and republish the deck plan. Say in one or two lines which slides changed. Edit the current slides in the artifact, so changes the team made in the editor are kept. Keep the slide numbering stable where possible.

## Working with business-research

- If the user brings a research question but no material, offer to run the business-research skill first and then build the deck from its report, both in the same chat.
- This skill never searches the web to fill a content gap. If the user explicitly asks for missing data, switch to the business-research workflow for that gap and return with the new number and its source.
- Looking up a company's brand colours for the design is not content research and is allowed (see `references/design.md`).
