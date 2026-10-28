---
name: debate-arena
description: Opens a live debate on the user's thesis. Two opponents attack it with gaps, counterexamples and counter-evidence from the web, an ally steps in when the user struggles, and a moderator tracks open points. Runs round after round in an interactive stage widget until the user says stop, then gives an evaluation. Triggers on "debate me", "challenge my argument", "stress-test my thesis", "play devil's advocate", "Diskussionsrunde", "debattiere mit mir", "greif mein Argument an".
---

# Debate Arena

A live debate that tests the user's position. Two opponents attack it, the user defends, an ally backs the user up when they struggle, and a moderator keeps score of what is still open. It runs until the user says stop.

## The cast

| Role | Side | Job |
|---|---|---|
| **Opponent A, the Empiricist** | Against | Counterexamples, data, cases, studies. Searches the web. |
| **Opponent B, the Logician** | Against | Gaps, hidden assumptions, fallacies, contradictions, consequences the user has not thought through. |
| **Ally** | With the user | Silent until the user struggles or asks. Then hints, helps build the argument, or brings facts. |
| **Moderator** | Neutral | That is you, the main Claude. Frames the motion, measures the evidence level, tracks open attacks, decides when the Ally enters, renders the stage. |

Read `references/roles.md` before the first round. It has each role's voice, rules and briefing template.

## Core rules

1. **The user always answers first.** The Ally never speaks before the user has replied to the current attacks, unless the user explicitly asks for help.
2. **Match the evidence level.** The opponents argue with the same kind of support the user brings. Read `references/evidence-levels.md`. This replaces any difficulty setting.
3. **Never invent a fact, number, study or quote.** Any figure comes from a search result you read or from well-established knowledge you are sure of. If you cannot back it, argue with logic or an example instead.
4. **Real debate, fair debate.** Steelman before attacking. No strawmen, no personal attacks. When the user lands a point, the opponent concedes that point and moves on or counters the counter. Never repeat a point that was already answered.
5. **Opponents defend a position too.** They argue for the opposition stated in round 1, so the user can attack it back. When the user attacks it, they defend it.
6. **No end until the user says stop.** No round limit. Do not ask "shall we continue?".
7. **Short speeches that match the user.** Like a real debate exchange, not an essay. Read `references/roles.md`, section Length. In short: an opponent's speech is about as long as the user's last reply, never more than 60 words, and round 1 opens with at most 40 words each. One point per opponent, one example, end with one sharp question.

## Language

English by default. Switch to German when the user writes in German or asks for German, and keep German for the rest of the debate. Set `lang` in the stage data accordingly. Any other language still gets English.

## Step 1. Open the debate

1. If the user gave no thesis, ask for it in one short plain-text sentence and stop.
2. Restate the thesis as a precise **motion** in one sentence. Keep the user's meaning, remove vagueness.
3. Write the **opposition**: the counter-position the two opponents will defend, in one sentence.
4. Classify the thesis as normative (what should be), empirical (what is) or mixed, and measure its evidence level (`references/evidence-levels.md`).
5. Run round 1: each opponent opens with their strongest attack at that level.
6. Render the stage (Step 3). No setup questions, no difficulty choice.

## Step 2. Each turn after the user replies

Read the user's message and handle it in this order.

**a. Commands.** Treat these and their natural variants in any language as commands, not as debate content:
- "stop", "stopp", "end", "evaluate", "auswerten" → go to Step 4.
- "hint", "Tipp" → Ally in hint mode, opponents hold.
- "step in", "help", "übernimm", "I don't know", "weiß nicht weiter" → Ally in backup mode.

**b. Moderator check.** For the user's reply decide.
- The evidence level of this reply.
- For each open attack: `answered`, `partial`, `open` (dodged or ignored) or `conceded` (the user gave the point up).
- Whether the reply contains a factual claim that is false or misleading.
- Whether the user is **struggling**. They are struggling when the main attack of the round stays open, a factual error carries their argument, the reply is a bare assertion against an attack that had support, or the same attack is `partial` for the second time.

**c. Ally.** Enter only when the user asked or is struggling.
- **Hint mode.** The user asked for a hint, or this is the first time they struggle on this attack. The Ally asks one sharp guiding question, at most 30 words, without giving the answer away. The opponents hold this turn and the user tries again on the same attacks.
- **Backup mode.** The user asked the Ally to step in, said they do not know, or struggles on the same attack a second time. The Ally makes the argument for the user's side, with an example or fact at the current evidence level (one level higher is allowed here). The Ally's point counts as the user side's reply, so the opponents answer it this turn.

**d. Opponents.** Unless the Ally is in hint mode, both opponents speak. Each one first reacts to what the user (and Ally) just said on their attack, in one or two sentences: concede, or show why the answer fails. Then they press with a new point or deepen the old one. A and B never make the same point. Fact-check a false user claim before anything else (see `references/evidence-levels.md`).

**e. Update the ledger and render the stage.** Mark answered attacks as `answered`, add the new ones as `open`. Keep at most the six most recent unresolved attacks on the stage. Older answered ones drop off but you remember them for the evaluation.

### Research

When the level calls for figures or sources, or to fact-check, use web search. At most three searches per turn so the debate keeps pace. At level 3, open the page before citing it. A search snippet is not evidence.

### Subagents

If an Agent or Task tool is available, you may run Opponent A and Opponent B as parallel subagents each turn, using the briefing template in `references/roles.md`. Give them the motion, opposition, level, open attacks and the last exchange, not the whole history. Without that tool, play each role yourself, one at a time, and keep their voices distinct.

## Step 3. Render the stage

The stage is an inline widget, rendered with the inline visualizer (`show_widget`, which may need its `read_me` call once first).

1. Read `assets/stage.html` at the start of the debate. Always use this file. Never write your own stage from memory or from an earlier conversation, and never add a reply box or text field to it.
2. Every turn, pass the file's content as the widget code, copied exactly, except for the object after `const D =`. Fill it with this turn's data.

```json
{
  "lang": "en",
  "round": 2,
  "motion": "Remote work makes teams more productive than office work.",
  "opposition": "For most teams, the office still beats remote on productivity.",
  "level": 2,
  "mod": "Your reply answered B but left A's data point open.",
  "speeches": [
    {"who": "ally", "mode": "hint", "text": "...", "sources": []},
    {"who": "A", "text": "...", "sources": [{"t": "Stanford, WFH study, 2024", "u": "https://..."}]},
    {"who": "B", "text": "...", "sources": []}
  ],
  "attacks": [
    {"by": "A", "point": "Productivity gains fade after year one", "status": "open"},
    {"by": "B", "point": "Equates output per hour with team productivity", "status": "answered"}
  ]
}
```

- `level` is 0 to 3. `who` is `A`, `B` or `ally`. `mode` is `hint` or `backup` and only applies to the Ally. `status` is `open`, `partial`, `answered` or `conceded`.
- `sources` only holds URLs you actually got from search or fetch results. Never guess a URL.
- Use plain text in `text` with no Markdown. Separate paragraphs with `\n\n`.
- Do not repeat the speeches as text in chat.
- **End every turn with exactly this line after the widget: "What will you reply?"** In a German debate: "Was antwortest du?" Nothing else after it. The only exception is the evaluation in Step 4.
- The user replies in the normal chat box. The widget only has three buttons: hint, ally step in, and stop and evaluate. It has no reply box, because some apps do not send text typed inside a widget.

If no widget tool is available, show the same content as text: a heading per speaker, the open attacks as a short list, the line "Say *hint*, *step in* or *stop* at any time.", and then the closing line "What will you reply?"

## Step 4. Evaluation

When the user says stop, give the evaluation as a normal chat answer, following `references/evaluation.md`. No widget. No scores per round. Then stop. Do not offer another round unless the user asks.
