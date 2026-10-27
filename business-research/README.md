# Business Research

A Claude skill for source-first business research. It prioritises publicly accessible primary sources, traces findings to their sources and checks key claims. Built with Nova SBE students in mind, it also helps you identify relevant library databases and what to look up there, including sources such as Statista where appropriate.

## Install

1. Download **[business-research.zip](https://github.com/EmreAI/claude-skills/raw/main/dist/business-research.zip)**. Don't unzip it.
2. In Claude, open **Settings → Capabilities** and turn on **Code execution and file creation**.
3. Under **Skills**, click **Upload skill** and choose the ZIP.
4. Start a new chat, for example: *"Research the European e-bike market for my strategy class."*

Claude Code: `unzip ~/Downloads/business-research.zip -d ~/.claude/skills/`

## Workflow

1. **Describe your project.** Share your research question, purpose, geography, timeframe, requirements and any sources or findings you already have. The more relevant context, the better.
2. **Choose the approach.** Claude asks about source types, research depth and library access, then plans the research.
3. **Research and check.** It searches accessible sources, prioritises primary material and checks key claims against the sources.
4. **Review the output.** You receive findings with citations, confidence levels, gaps and a source list. When licensed sources could help, you also get a short list of databases, search terms and suggested exports.
5. **Add library material.** If you upload relevant exports, Claude can incorporate them and update the findings.

Access to library databases depends on your institution and its current licences. The skill does not bypass paywalls or log in for you.

## How it's built

```
business-research/
├── SKILL.md                    the workflow Claude follows
└── references/
    ├── frameworks.md           sub-questions for each research type
    ├── open-sources.md         where to look, ranked by reliability
    └── nova-sources.md         Nova SBE library database guidance
```

Anyone can use the skill. The Nova SBE reference is used when you have Nova SBE library access.
