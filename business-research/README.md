# Business Research

A Claude skill for research a demanding professor or consulting partner would accept: market sizing, market entry, company and competitor analysis, industry overviews, literature reviews. Open, primary sources first, every number with a source and a date, key claims checked a second time.

## Install

1. Download **[business-research.zip](https://github.com/EmreAI/claude-skills/raw/main/dist/business-research.zip)**. Don't unzip it.
2. In Claude, open **Settings → Capabilities** and turn on **Code execution and file creation**.
3. Under **Skills**, click **Upload skill** and choose the ZIP.
4. Start a new chat, for example: *"Research the European e-bike market for my strategy class."*

Claude Code: `unzip ~/Downloads/business-research.zip -d ~/.claude/skills/`

## What it does

1. **Asks once.** Which sources (data, company reports, papers, press), how deep and which library access you have.
2. **Plans.** Breaks the question into 4–7 sub-questions using a matching framework.
3. **Searches open sources.** Official statistics, filings and annual reports before articles about them. Reads the page before using a number.
4. **Hands you the paywalled part.** Licensed databases become a short task list: which database, the exact link, the search terms and the file to export.
5. **Checks itself.** A separate agent re-opens the sources behind the 5–10 key claims.
6. **Delivers.** Bottom line, findings with confidence levels, gaps, and a full source list.

It never guesses links, never logs in for you and never works around paywalls.

## How it's built

```
business-research/
├── SKILL.md                    the workflow Claude follows
└── references/
    ├── frameworks.md           sub-questions for each research type
    ├── open-sources.md         where to look, ranked by reliability
    └── nova-sources.md         Nova SBE library databases (only used if you study there)
```

Works for anyone. The Nova SBE file is only read when you say you have Nova SBE library access.
