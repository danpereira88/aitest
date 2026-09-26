---
description: Analyze a folder of call transcripts by fanning out the call-extractor subagent, then aggregate.
argument-hint: [path-to-transcripts-folder]
---

You are the **orchestrator**. Your job is to coordinate extraction across many calls — not to extract them yourself. The actual per-call reasoning is delegated to the `call-extractor` subagent so each call runs in its own isolated context.

Folder to process: **$1** (default: `test-data/transcripts`)

Do this:

1. List the transcript JSON files in the folder.
2. For each file, invoke the **call-extractor** subagent, handing it that one file path and nothing else. Run them in parallel batches (e.g. up to 5–10 at a time) so many calls extract concurrently. Each subagent returns one JSON record.
3. Collect every returned record into an array. Do not re-extract or second-guess a subagent's record; you only assemble.
4. Write the combined `skyloom_calls_master.json`:
   ```json
   { "generated_at","total_calls","total_external","total_internal","date_range":{"earliest","latest"},"records":[...] }
   ```
5. Report a one-line summary: calls processed, external vs internal, and how many were low-confidence (<0.3).

Keep your own context lean: you hold only the list of files and the returned records, never the raw transcripts. That separation is the point — the transcripts live in the subagents' contexts, so this scales to thousands of calls without overflowing yours.

After the master file exists, offer to generate the HTML report (report mode of the call-intel-analyst skill).
