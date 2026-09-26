# call-extractor — a specialized subagent

**Module 3 — Build a Specialized Subagent**

A Claude Code subagent that extracts structured intelligence from a **single** sales-call transcript, in its own isolated context, and returns one JSON record. An orchestrator fans it out across a whole folder of calls and aggregates the results.

*All test data is synthetic — a fictional observability vendor, "Skyloom," and 50 generated transcripts. No real company, person, or conversation.*

---

## What it does

Given one transcript JSON (call metadata + `transcript_text`), `call-extractor` produces one record conforming to a fixed schema: account (segment, region), products discussed, use cases, the four JTBD switching forces (push / pull / anxiety / habit), pain points, competitors, deal signals, and a short summary — each grounded in verbatim quotes, with confidence scores. It handles edge cases (short voicemails, internal calls, non-English) per its rules.

## Why it needs to be a subagent (not a prompt or a skill)

In Module 2 the same extraction logic lived in a **skill** that runs in the main context. That works for a handful of calls and breaks at scale. Turning the per-call worker into a subagent is justified on all three grounds the assignment names:

- **Dedicated / bounded context.** You cannot fit thousands of transcripts into one context window. Each `call-extractor` instance sees exactly one transcript plus its own instructions — nothing else. Extractions can't bleed into each other, and the main context never fills with raw transcript text.
- **Independent reasoning.** Extracting one call is a self-contained inference task: infer who's the rep vs. the prospect, classify segment and region, pull the four forces with evidence, assign confidence. The subagent owns that reasoning loop end to end and returns only the result.
- **Independent / parallel operation.** The orchestrator dispatches many `call-extractor` instances concurrently and collects their records. A single in-context skill can't parallelize; a fleet of subagents can, which is what makes a 2,000-call corpus tractable.

Short version: *the Module 2 skill is the recipe; this subagent is an autonomous line cook you can run fifty of at once.*

## When it is called (calling conditions)

- Invoked by the orchestrator (`/analyze-calls`) **once per transcript file** when processing a folder.
- Or on demand for a single call ("extract this call").
- **Not** called for aggregation, reporting, or anything that needs to see more than one call — those stay with the main agent by design.

## What context it receives

Deliberately minimal: **one transcript's JSON** (inline or a file path) and its own system prompt (the schema + extraction rules + canonical vocabularies). It does **not** receive other calls, the master file, the report, or the wider project context. Its only tool is `Read`, so it can't reach beyond the file it was handed. Its output is the single JSON record — nothing else.

---

## Package contents

```
call-extractor-subagent/
├── .claude/
│   ├── agents/call-extractor.md      # the subagent definition (frontmatter + system prompt)
│   └── commands/analyze-calls.md     # orchestrator: fan out over a folder, aggregate
├── examples/                         # example input/output pairs (see below)
│   ├── call_003.input.json  / call_003.output.json   (rich call)
│   └── call_014.input.json  / call_014.output.json   (edge case: short/voicemail)
├── test-data/transcripts/            # 50 synthetic transcripts to test against
└── README.md
```

## Install & run (Claude Code)

1. Copy the `.claude/` folder into your project root (or into `~/.claude/` to make it global).
2. Confirm Claude Code sees it: run `/agents` — `call-extractor` should be listed.
3. Extract one call:
   > "Use the call-extractor subagent to extract `test-data/transcripts/call_003.json`."
4. Process the whole folder:
   > `/analyze-calls test-data/transcripts`

   The orchestrator lists the files, dispatches `call-extractor` per file (in parallel batches), and writes `skyloom_calls_master.json`.

Model is set to `sonnet` for balanced quality; drop it to `haiku` in the frontmatter for cheaper, faster fan-out over very large corpora.

## Testing / example I/O

The `examples/` folder shows the subagent's contract on two representative inputs:

- **call_003** (rich, 23-min media-company call): input transcript → a full record with 5 use cases, Datazen named as the incumbent on a cost pain, migration-bandwidth anxiety, and Discovery-stage signals. This validates the core extraction path.
- **call_014** (edge case, short call): input → a low-confidence record (`confidence_overall` < 0.3) with mostly null fields, confirming the short-call rule fires instead of hallucinating signal.

To reproduce: hand each `.input.json` to the subagent and compare its output to the corresponding `.output.json`. Because the test data is synthetic with known planted signals, these outputs double as an answer key.

## Portability

The concept isn't Claude-Code-specific. The same worker maps onto any subagent/agent framework: the `agents/call-extractor.md` body is the system prompt, `tools: Read` is the tool allow-list, the input schema is the message contract, and `analyze-calls.md` is the orchestration loop (list files → spawn workers in parallel → collect JSON → aggregate).

## Natural next subagent

The same pattern extends to a **deal-risk assessor** — one subagent per account that reads all of that account's calls in a dedicated context and returns a risk/next-best-action assessment. Same justification (dedicated context per account, independent judgment, parallel across accounts), different responsibility.
