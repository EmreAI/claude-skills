---
name: business-research
description: Source-first business research for market, company and industry analysis or literature reviews. Prioritises accessible primary sources, checks key claims, and identifies useful licensed databases, including Nova SBE resources.
---

# Business Research

Source-first business research that prioritises accessible primary sources, traces findings to evidence and helps users identify relevant licensed databases, including Nova SBE library resources.

## Core rules

1. **Open sources first.** Everything Claude can reach itself (tier A) is searched before anything is handed to the user. Licensed databases (tier B) come last, as a short task list.
2. **Primary over secondary.** An annual report beats an article about the annual report. An official statistic beats a blog quoting it. Statista and Wikipedia are signposts to the original, never the final citation.
3. **Every number has a source, a date and a unit.** Estimates are marked [E]. A number Claude could not trace to a source does not go in the output.
4. **Never guess a URL or a DOI.** Links come from search or fetch results only.
5. **Never bypass access.** No passwords, no logging in for the user, no paywall workarounds, no mirrors of blocked pages. If a page is unreachable, say so and offer the next best source.
6. **No filler.** No generic intros, no "in today's fast-paced world", no restating the question. Findings first.

## Step 1. Understand, then ask once

Read the request and infer three things. The research type (see `references/frameworks.md`), the purpose (assignment, report, case, thesis, personal question) and the geography and time frame.

Then ask **one round** of questions with the AskUserQuestion tool. If that tool is not available, ask the same thing as a short plain-text checklist. Never ask a second round unless an answer contradicts the request.

Question 1, multi-select, always asked. "Which kinds of sources do you want?"
- Data and statistics (official statistics, market data)
- Company sources (annual reports, investor presentations, filings)
- Academic papers
- News and business press

Industry and consulting reports are included automatically when data or company sources are chosen.

Question 2, single-select, always asked. "How deep should this go?"
- Project (recommended). Full sub-question breakdown, 25 to 40 searches, independent check of key numbers.
- Quick scan. Main question only, about 10 searches, no separate check.
- Deep dive. Everything in Project plus more sources per sub-question and an outline you approve first.

Question 3, single-select, only if the user has not said it already. "Which library access do you have?"
- Nova SBE
- Another university
- None

If the user says "just go" or skips the questions, use all four source types, Project depth and no library access.

## Step 2. Plan

1. Pick the matching framework in `references/frameworks.md`. Frameworks are guidelines. Drop sub-questions that do not matter for this request and add ones that do.
2. Write 4 to 7 sub-questions. For each, note which source types answer it best.
3. Show the plan to the user in at most six lines, then start. Only in Deep dive mode wait for approval.

## Step 3. Search tier A

Use `references/open-sources.md` for where to look. For each sub-question, in this order.

1. Official and primary sources (statistics offices, regulators, company filings and investor relations pages).
2. Academic sources, if selected. Use a connected scholarly connector (Consensus, Scite, Elicit, SciSpace) when one is available, otherwise the open scholarly indexes listed in open-sources.md.
3. Reputable press and institutional research, if selected.

Working rules.
- Short, specific queries. Use `site:` filters for known high-quality domains. Each query must differ meaningfully from the last.
- Fetch the actual page or PDF before using a number. Search snippets are not evidence.
- Keep an evidence ledger while working. One line per claim with the claim, value, source, publication date, URL, tier and whether the page was actually read.
- When two sources disagree, keep both, note the difference and prefer the more primary one.
- Market research press releases that announce a market "will reach $X billion by 2032" (typical of paid report vendors) are low reliability. Use them only if nothing better exists and label them as such.

### Dead or blocked pages

If a fetch fails, try once to find the same document on the publisher's own site or as a PDF from the original organisation. If that fails too, record it as unreachable and move on. Do not retry the same URL, do not use caches or mirrors.

### Stop rule

A sub-question is done when two independent good sources support the answer, or when three consecutive searches add nothing new. Stop the whole search when every sub-question is done or the budget is reached.

| Depth | Search budget | Sources per sub-question |
|---|---|---|
| Quick scan | about 10 | 1 to 2 |
| Project | 25 to 40 | 2 to 3 |
| Deep dive | up to 60 | 3 to 5 |

## Step 4. Tier B handoff

If the user has library access, read `references/nova-sources.md` (Nova SBE) or use general knowledge of common university databases. Pick only the databases that would clearly improve a sub-question tier A could not answer well.

Each handoff task contains the database, the direct library link, the exact search terms, which file to export and why it matters. Maximum five tasks, ranked by value. If tier A already answered everything well, say so and give no tasks.

### Browser use

Only if the user explicitly asks Claude to look inside a licensed database with the browser and has logged in themselves.
- One specific lookup per task, never bulk extraction. University licenses usually forbid automated extraction.
- Stop after about five minutes or ten actions per site, or immediately if the page does not load. Report what was found and hand the rest to the user.
- Never type credentials. Never accept terms on the user's behalf.

## Step 5. Independent check

In Project and Deep dive mode, if the Agent tool is available, start one verification subagent. Give it only the 5 to 10 load-bearing claims from the ledger (claim, value, cited URL), not the draft and not the reasoning. Its job is to open each source and return for every claim one of supported, partly supported, not supported or source unreachable, with the exact passage.

Fix or remove anything not supported. Without the Agent tool, re-open the top five sources yourself before writing.

## Step 6. Output

Prepare a well-structured written report. When file creation is available, deliver it as an editable Word document (.docx) by default and provide a short summary in the chat. Respect a different format or chat-only delivery if the user requests it. If document creation is unavailable, deliver the full report in the chat and explain that no file could be created. Place citations immediately after each source-dependent claim or paragraph, so readers can trace the evidence; clearly distinguish analysis and assumptions from sourced facts.

1. **Bottom line.** Three to five sentences answering the main question.
2. **Findings by sub-question.** Each with the key facts, inline citations and a confidence tag. High means two or more independent primary sources. Medium means one primary or several secondary sources. Low means a single secondary source or an estimate.
3. **Gaps.** What could not be answered with open sources and why.
4. **Your part.** The tier B tasks from Step 4.
5. **Papers to read.** Title, authors, year, DOI link and a free legal version if one exists. Only if academic sources were selected.
6. **Sources.** Grouped by tier, every entry with organisation, document, date and link.

Citation format in the text is [Organisation, Document, Date], for example [Eurostat, Household consumption by purpose, 2025].

## Step 7. Round two

When the user uploads exports from tier B databases, read them, add the new facts to the ledger, recheck any finding they contradict and deliver an updated version that marks what changed.
