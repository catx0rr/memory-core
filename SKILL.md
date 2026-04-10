---
name: memory-core
description: "Read-only Layer 1 observer for OpenClaw's built-in memory-core dreaming. Use when: checking dream status, verifying MEMORY.md promotions, confirming the nightly sweep ran. Does not write to MEMORY.md or perform promotion."
---

# Memory-Core Status — Built-in Dreaming Observer

A read-only observer that checks what memory-core's built-in dreaming did and reports status.
It does not perform promotion — memory-core handles that automatically.

---

## What this skill is for

Use this skill when:

- Checking if the nightly dream sweep ran
- Verifying MEMORY.md received promotions
- Inspecting dream evidence surfaces
- Getting a structured status report on built-in dreaming

---

## Do NOT use this skill for

- Writing to MEMORY.md — memory-core owns that
- Modifying `memory/.dreams/` — memory-core owns that
- Checking Auto-Dream logs — Auto-Dream is a separate system
- Performing promotion, scoring, or gating

---

## Wrapper scripts

Memory-core status is accessed only through these governed wrappers:

- `check_evidence.py` — scan dreaming evidence surfaces (DREAMS.md, `memory/.dreams/`, phase reports, MEMORY.md tail)
- `memory_state.py` — count MEMORY.md structural metrics (lines, sections, entries, breakdown)

Both scripts return JSON with a top-level `ok` boolean.

---

## Evidence surfaces checked

| Surface | What memory-core writes there |
|---------|-------------------------------|
| DREAMS.md / dreams.md | Human-readable dream reports |
| `memory/.dreams/` | Machine state, short-term recall tracking |
| `memory/dreaming/<phase>/` | Optional per-phase reports (light, rem, deep) |
| MEMORY.md | Promoted durable entries (tail checked for recent additions) |

---

## Operational cadence

Scheduled monitoring is deterministic and delegated to
`runtime/memory-core-prompt.md`. That prompt checks dreaming status,
scans evidence surfaces, counts MEMORY.md state, and composes a
structured status report.

One-time cron setup is handled by `runtime/create-cron-prompt.md`.

Schedule: `30 3 * * *` (30 minutes after memory-core's 3:00 AM sweep).

---

## Safety rules

1. This skill is read-only
2. It does NOT write to MEMORY.md — memory-core handles promotion
3. It does NOT modify `memory/.dreams/` — memory-core owns that directory
4. It does NOT write to `.dream-log.md` — that is an Auto-Dream surface
5. It only reads and reports
6. If evidence is unclear, say so — do not fabricate sweep results
