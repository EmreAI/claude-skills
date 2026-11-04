# Claude Skills

Skills to help you work more effectively with AI.

| Skill | What it does | Download |
|---|---|---|
| [Business Research](business-research/) | Source-first business research, with guidance for Nova SBE library databases. | [ZIP](https://github.com/EmreAI/claude-skills/raw/main/dist/business-research.zip) |
| [Business Presentation](business-presentation/) | Finished slide decks for group projects, built strictly from your material, with real action titles and room for the team's ideas. | [ZIP](https://github.com/EmreAI/claude-skills/raw/main/dist/business-presentation.zip) |
| [Course Index](course-index/) | Converts a course folder (slides, readings, exercises, Excel, notebooks) once into an indexed text base with a syllabus digest and CLAUDE.md, keeps it in sync each week, and cuts the tokens per question without losing charts or formulas. | [ZIP](https://github.com/EmreAI/claude-skills/raw/main/dist/course-index.zip) |
| [Debate Arena](debate-arena/) | A live debate that stress-tests your argument, with two opponents, an ally and an interactive stage. | [ZIP](https://github.com/EmreAI/claude-skills/raw/main/dist/debate-arena.zip) |

## Install

**Claude app**

1. Download the skill's ZIP from the table above. Keep it zipped.
2. In Claude, open **Settings → Capabilities** and enable **Code execution and file creation**.
3. Under **Skills**, select **Upload skill** and choose the ZIP.
4. Start a new chat and describe your project.

**Claude Code**

```bash
unzip ~/Downloads/business-research.zip -d ~/.claude/skills/
```

Restart Claude Code and type `/skills` to check that it is listed.
