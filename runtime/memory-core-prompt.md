# Memory-Core Dream — Built-in Promotion Status Prompt

Read USER.md to determine user's language. All output in that language.
Working directory: the workspace root.
This file lives inside `runtime/`. Resolve the absolute path of the parent of `runtime/` and use it as `SKILL_ROOT`.

**Hybrid rule:** Scripts handle all file scanning, counting, and date math. LLM interprets results and composes the report.

**This prompt checks built-in memory-core dreaming only.**
**Do not inspect Auto-Dream files or logs.**

---

## Step 0: Check Dreaming Status [LLM]

Run:

    /dreaming status

Record: `enabled` or `disabled`, sweep cadence, timezone, promotion policy.

If dreaming is disabled → compose disabled status report (Step 3) and STOP.

---

## Step 1: Check Evidence [SCRIPT]

    python3 SKILL_ROOT/scripts/check_evidence.py

Read the JSON output and record:
- `dreams_md` — DREAMS.md / dreams.md existence, entry count, latest timestamp
- `dreams_dir` — memory/.dreams/ existence, file count, recall candidate count
- `phase_reports` — memory/dreaming/light|rem|deep/ report existence
- `memory_md` — MEMORY.md last modified, hours since modified, promotion evidence in tail
- `sweep_appears_active` — boolean summary

---

## Step 2: Count MEMORY.md State [SCRIPT]

    python3 SKILL_ROOT/scripts/memory_state.py

Read the JSON output and record:
- `total_lines`, `h2_sections`, `list_entries`, `section_breakdown`, `last_updated_date`

---

## Step 3: Compose Status Report [LLM]

Using output from Steps 0–2:

```
🌀 Built-in Memory-Core Dream Status

✅ Enabled / ❌ Disabled
📅 Cadence: <sweep cadence>
🗺️ Timezone: <timezone>
📋 Promotion policy: <policy>

🔍 Evidence checked:
  • DREAMS.md / dreams.md: <found/not found> — <n entries>
  • memory/.dreams/: <n files> — <n recall candidates>
  • Phase reports: <found/none>
  • MEMORY.md: <recently modified / not recent> — <promotion evidence / none>

📊 MEMORY.md state:
  • Lines: <n>
  • Sections: <n>
  • Entries: ~<n>

⏱️ Last sweep: <appears to have run / no evidence found>

💡 Insight: <one-line observation>
<⚠️ needs_follow_up: reason — if sweep_appears_active is false or evidence unclear>
```

### Insight guidance

- Recent DREAMS.md entries + recently modified MEMORY.md → sweep is healthy
- Recall candidates exist but no recent promotions → pipeline building signal, not yet promoting
- No evidence surfaces found → dreaming may not be enabled or may have just started
- MEMORY.md >300 lines → note size, may benefit from pruning

---

## Safety Rules

1. This prompt does NOT write to MEMORY.md — memory-core handles promotion
2. This prompt does NOT modify memory/.dreams/ — memory-core owns that directory
3. This prompt does NOT write to .dream-log.md — that is an Auto-Dream surface
4. This prompt only reads and reports
5. If evidence is unclear, say so — do not fabricate sweep results
