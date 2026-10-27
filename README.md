# Claude Skills

Skills that teach Claude a complete workflow. Free to download and use.
Made by [Emre Ayalp](https://emreayalp.com).

| Skill | What it does | Download |
|---|---|---|
| [Business Research](business-research/) | Source-first research for business school projects, reports and cases. Every number traced to its source. | [ZIP](https://github.com/EmreAI/claude-skills/raw/main/dist/business-research.zip) |

## Install

**In the Claude app** (claude.ai, desktop or mobile)

1. Download the skill's ZIP file from the table above. Don't unzip it.
2. In Claude, open **Settings → Capabilities** and make sure **Code execution and file creation** is on.
3. Under **Skills**, click **Upload skill** and choose the ZIP.
4. Start a new chat and ask as usual. Claude picks up the skill on its own when it fits.

**In Claude Code**

```bash
unzip ~/Downloads/business-research.zip -d ~/.claude/skills/
```

Restart Claude Code. Type `/skills` to check that it's there.

## What a skill is

A skill is a folder with a `SKILL.md` file (the instructions) and optional reference files. Claude reads the short description at all times and loads the rest only when your request matches, so skills cost nothing while unused.

```
claude-skills/
├── business-research/   one folder per skill, each with its own README
├── dist/                ready-to-upload ZIP files
└── pack.sh              rebuilds the ZIPs after a change
```
