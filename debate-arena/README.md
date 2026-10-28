# Debate Arena

A Claude skill that stress-tests your argument in a live debate. Two opponents attack your thesis, you defend it, and an ally backs you up when you get stuck. It runs round after round on an interactive stage in the chat until you say stop, then gives you an honest evaluation.

## Install

1. Download **[debate-arena.zip](https://github.com/EmreAI/claude-skills/raw/main/dist/debate-arena.zip)**. Don't unzip it.
2. In Claude, open **Settings → Capabilities** and turn on **Code execution and file creation**. Web search should be on too.
3. Under **Skills**, click **Upload skill** and choose the ZIP.
4. Start a new chat, for example: *"Debate me: remote work makes teams more productive."*

Claude Code: `unzip ~/Downloads/debate-arena.zip -d ~/.claude/skills/`

## How it works

| Who | Side | What they do |
|---|---|---|
| Opponent A, the Empiricist | Against you | Counterexamples, data and studies from the web |
| Opponent B, the Logician | Against you | Gaps, hidden assumptions, fallacies |
| Ally | With you | Steps in when you struggle or ask: a hint, or full backup with facts |
| Moderator | Neutral | Tracks open attacks, decides when the ally enters |

- **You always answer first.** The ally only joins after your reply, when you ask or when your answer leaves the main attack open.
- **No difficulty setting.** The opponents match your evidence. Argue with reasoning and they argue with reasoning. Bring numbers or sources and they bring theirs. The stage shows the current level.
- **No round limit.** Click *Stop and evaluate*, or type "stop".
- **Language.** English by default, German when you write in German.

## The stage

Each round appears as a widget in the chat with the speeches, the evidence level and the list of open attacks, followed by "What will you reply?". You reply in the normal chat box. Three buttons on the stage ask for a hint, call in the ally or end the debate.

## The evaluation

A verdict on how your thesis held up, your strongest moments, the attacks you left open, what the ally gave you, an evidence profile, a stronger version of your thesis, what to prepare before defending it for real, and all sources.

## How it's built

```
debate-arena/
├── SKILL.md                    the debate flow Claude follows
├── assets/
│   └── stage.html              the stage widget, filled with data each round
└── references/
    ├── roles.md                voices and rules for each speaker
    ├── evidence-levels.md      how opponents match your evidence
    └── evaluation.md           structure of the final evaluation
```
