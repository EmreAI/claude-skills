# Optional: sync automatically at session start (Claude Code)

A SessionStart hook runs the converter whenever Claude Code opens the course folder. New, changed, renamed and removed files are converted before the first question, and Claude gets a short message listing what still needs an INDEX.md entry. When nothing changed, the hook prints nothing and costs nothing.

It only fires when the course folder itself is the project folder. It does not apply in the Claude app's chat or in Cowork; there, `status` in CLAUDE.md does the same job.

This writes a persistent setting, so ask the user first, in one line:

> Should I add a small hook so new files are converted automatically each time you open this folder in Claude Code?

On yes, create or merge `<course>/.claude/settings.json`. Keep any settings and hooks already there and add this entry to `hooks.SessionStart`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/_text/_tools/course_sync.py\" sync --hook",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

On Windows, use `python` instead of `python3`.

Test it once: `python3 "<course>/_text/_tools/course_sync.py" sync --hook` should print nothing when everything is up to date. Then update the **New material** section of CLAUDE.md as the template describes.
