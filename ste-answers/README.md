# STE Answers

A Claude skill that makes answers short, direct and easy to read. It uses the rules of **ASD-STE100 Simplified Technical English**, the controlled language that aircraft maintenance manuals have used since the 1980s.

## Why

Long AI answers cause reading fatigue. After the tenth answer with three headings, a summary and a list of offers, you stop reading closely. You skim. Then you accept what Claude says without checking it, or you lose the energy to keep working. The problem is not the content. It is the effort the text costs you.

Aviation solved this decades ago. A mechanic who misreads a manual can cause an accident, so the manuals follow strict rules: short sentences, one instruction per sentence, one word for one meaning. This skill gives Claude the same rules.

## Install

1. Download **[ste-answers.zip](https://github.com/EmreAI/claude-skills/raw/main/dist/ste-answers.zip)**. Don't unzip it.
2. In Claude, open **Settings → Capabilities** and turn on **Code execution and file creation**.
3. Under **Skills**, click **Upload skill** and choose the ZIP.
4. Start a new chat and say *"Use STE"* or *"Answer in plain STE from now on."*

Claude Code: `unzip ~/Downloads/ste-answers.zip -d ~/.claude/skills/`

**Always on:** a skill loads only when your request matches. To get STE answers in every chat, add one line to your Claude preferences (or to `CLAUDE.md` in Claude Code): `Answer in ASD-STE100 Simplified Technical English. Use the ste-answers skill.`

## What it does

1. **Answer first.** The first sentence contains the answer. No "Great question", no plan of what follows.
2. **Short sentences.** 20 words or fewer for steps, 25 for explanations. One instruction or one fact per sentence.
3. **Active voice.** Every sentence says who does what.
4. **One word, one meaning.** If it is a "folder", it stays a "folder".
5. **Warnings before the step.** You read the risk before you run the command.
6. **No filler.** No closing summary, no "I hope this helps", no marketing words.
7. **Nothing becomes false.** Real uncertainty stays in the text. Code, numbers and quotes stay untouched.

It works in German and other languages too, with the same rules. It stays off for creative writing and texts in your own voice.

## Credits

Inspired by Ruben Hassid's "Use ASD-STE100" prompt tip and by the open skills [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) and [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill). The rules are restated in my own words. ASD-STE100 is a standard of ASD (Aerospace, Security and Defence Industries Association of Europe), free at [asd-ste100.org](https://www.asd-ste100.org). This skill is not affiliated with ASD.
