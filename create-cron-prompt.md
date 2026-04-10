# Memory-Core Dream — First-Run Baseline & Cron Setup

Read USER.md to determine user's language. All output in that language.
Working directory: the workspace root.
Resolve the absolute path of this prompt's parent directory and use it as `SKILL_ROOT`.

**Run once after enabling built-in memory-core dreaming.**
**This prompt verifies the baseline, then creates the recurring monitoring cron.**
**It does NOT perform dreaming, consolidation, or promotion.**
**It does NOT inspect Auto-Dream files or logs.**

---

## Step 0: Confirm Dreaming Is Enabled [LLM]

Run:

    /dreaming status

Record: `enabled` or `disabled`, sweep cadence, timezone, promotion policy.

If dreaming is **disabled** → report disabled status and STOP.

---

## Step 1: Scan Pre-existing Artifacts [SCRIPT]

    python3 SKILL_ROOT/scripts/check_evidence.py

Record whether any dream artifacts already exist.

---

## Step 2: Check MEMORY.md Baseline [SCRIPT]

    python3 SKILL_ROOT/scripts/memory_state.py

Record current MEMORY.md size and structure as the baseline.

---

## Step 3: Create the Recurring Monitoring Cron [LLM]

Create a cron with the following parameters:

| Field | Value |
|-------|-------|
| name | `memory-core-status` |
| schedule | `30 3 * * *` (uses timezone from Step 0) |
| sessionTarget | `isolated` |
| delivery | `announce` |
| timeoutSeconds | `120` |

The cron payload message must be:

    Run memory-core dream status check.
    Read SKILL_ROOT/memory-core-prompt.md and follow every step strictly.
    Working directory: the workspace root

Replace `SKILL_ROOT` in the payload with the actual absolute path resolved at the top of this prompt.

---

## Step 4: Report [LLM]

Compose a short confirmation:

- Dreaming status and config from Step 0
- Whether pre-existing artifacts were found (Step 1)
- MEMORY.md baseline metrics (Step 2)
- Cron name, schedule, and resolved prompt path (Step 3)

## Step 5: Cleanup [LLM]

Remove the files that are not needed anymore

- [ ] README.md
- [ ] create-cron-prompt.md
