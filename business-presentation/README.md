# Business Presentation

A Claude skill that builds finished slide decks for university group projects in business, data and management. It works strictly with the material you give it, writes real action titles, keeps the text free of buzzwords and AI phrasing, and marks the places where your team should add its own ideas. Built with Nova SBE students in mind.

## Install

1. Download **[business-presentation.zip](https://github.com/EmreAI/claude-skills/raw/main/dist/business-presentation.zip)**. Don't unzip it.
2. In Claude, open **Settings → Capabilities** and turn on **Code execution and file creation**.
3. Under **Skills**, click **Upload skill** and choose the ZIP.
4. Start a new chat, for example: *"Make a 15-minute presentation for our strategy group project from these notes."*

Claude Code: `unzip ~/Downloads/business-presentation.zip -d ~/.claude/skills/`

## Workflow

1. **Share your material.** This can be notes, data, articles, a case or a report from the [Business Research](../business-research/) skill. The deck uses only what you give it.
2. **Answer one round of questions.** Claude asks about the theme (Clean, Midnight, Classic or the company's colours), what the deck has to do, how long it should be and, for company decks, whether to get the logo from Wikimedia Commons.
3. **Get the deck.** Claude plans the storyline and builds the slides right away as Claude Slides, which you can edit in Claude and download as PowerPoint or PDF. Every slide has one message, one exhibit and its source. Open items are marked as *Team input* or *Data missing*.
4. **Read the deck plan.** Next to the chat, a deck plan shows the slide structure, every number and its source, so the team can check the content quickly.
5. **Improve it together.** Ask for changes in plain words, for example "slide 5: split by region", or add your own ideas.

## Works with Business Research

If you have a question but no material yet, run the Business Research skill first. Its report, including the evidence ledger and the gaps, goes straight into the deck.

## How it's built

```
business-presentation/
├── SKILL.md                    the workflow Claude follows
├── references/
│   ├── action-titles.md        what an action title is, rules, weak and strong examples
│   ├── writing-style.md        no em dashes, no buzzwords, no ad talk, no "it's not X, it's Y"
│   ├── storylines.md           storylines for decisions, findings, company analyses, pitches
│   ├── exhibits.md             which chart or exhibit proves which kind of message
│   ├── exhibit-library.md      15 consulting exhibits: benchmark, 2×2 matrix, SWOT, Five Forces and more
│   ├── design.md               the slide grid for content slides
│   ├── themes.md               Clean, Midnight, Classic and company themes, logo and image rules
│   └── deck-spec.md            the deck plan format that the checker tests
├── scripts/
│   ├── check_deck.py           checks titles, wording, limits and sources, writes the deck plan
│   └── deckcore.py             the checker's rules
└── assets/
    ├── example-deck.json       a complete example plan (fictional data)
    └── exhibits/               the exhibit templates in Claude Slides format, with previews
```
