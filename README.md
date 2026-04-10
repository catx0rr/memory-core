# Memory-Core Status — Built-in Dreaming Observer

A read-only observer skill that checks what OpenClaw's built-in memory-core dreaming did and reports status. It does not perform promotion — memory-core handles that automatically. This skill inspects evidence surfaces and composes a structured status report.

---

## What this skill does

After memory-core's nightly sweep (3:00 AM), this skill:

1. Reads `/dreaming status` for current config
2. Scans evidence surfaces for signs the sweep ran
3. Counts MEMORY.md structure and content
4. Composes a status report with an insight

It answers: **did the built-in dreaming sweep run, and what did it do?**

---

## What this skill does NOT do

- Does not write to MEMORY.md — memory-core owns that
- Does not modify `memory/.dreams/` — memory-core owns that
- Does not write to `.dream-log.md` — Auto-Dream owns that
- Does not perform promotion, scoring, or gating
- Does not inspect Auto-Dream files or logs

---

## Architecture role

```
memory-core dreaming (3:00 AM)
  │
  ├── tracks recall candidates in memory/.dreams/
  ├── scores and gates candidates internally
  ├── promotes qualified entries into MEMORY.md
  └── writes human-readable output to DREAMS.md
        │
        ▼
  memory-core status skill (this skill)
  │
  ├── reads /dreaming status
  ├── scans evidence: DREAMS.md, memory/.dreams/, MEMORY.md
  └── composes read-only status report
        │
        ▼
  Auto-Dream (4:30 AM) — separate system, not checked here
```

---

## Directory layout

```
memory-core/                        # Skill root (install location varies)
├── SKILL.md                        # Runtime contract
├── INSTALL.md                      # Operator installation guide
├── SETUP.md                        # Agent first-time setup guide
├── README.md                       # This file
├── LICENSE
├── runtime/
│   ├── create-cron-prompt.md       # One-time baseline check + cron creation
│   └── memory-core-prompt.md       # Recurring monitor (runs via cron)
└── scripts/
    ├── check_evidence.py           # Scan dreaming evidence surfaces
    └── memory_state.py             # Count MEMORY.md metrics
```

> **Note:** The skill can be installed anywhere under the workspace skill tree. All prompts resolve their own location at runtime. No hardcoded skill path is assumed.

---

## Scripts

All file scanning, counting, and date math is handled by deterministic Python scripts. The LLM interprets results and composes the report.

| Script | Purpose | Output |
|--------|---------|--------|
| `check_evidence.py` | Scan DREAMS.md, `memory/.dreams/`, phase reports, MEMORY.md tail | JSON: what evidence exists, `sweep_appears_active` boolean |
| `memory_state.py` | Count MEMORY.md lines, sections, entries, section breakdown | JSON: structural metrics |

### What stays LLM-driven

| Operation | Why |
|-----------|-----|
| Read `/dreaming status` | Chat command output |
| Interpret evidence | Decide if sweep ran vs partially ran vs did not run |
| Compose status report | Natural language composition |
| Generate insight | Pattern recognition across evidence signals |

---

## Evidence surfaces checked

| Surface | What memory-core writes there |
|---------|-------------------------------|
| DREAMS.md / dreams.md | Human-readable dream reports |
| `memory/.dreams/` | Machine state, short-term recall tracking |
| `memory/dreaming/<phase>/` | Optional per-phase reports (light, rem, deep) |
| MEMORY.md | Promoted durable entries (tail checked for recent additions) |

---

## Usage

**First-time setup:**

Tell the agent: *"Read `SETUP.md` in the memory-core skill directory and follow every step."*

This runs the baseline check and creates the recurring `memory-core-status` cron (daily at 3:30 AM, 30 minutes after the built-in sweep). The cron payload uses the resolved absolute path — no hardcoded skill path.

**Manual check:**

Tell the agent: *"Read `runtime/memory-core-prompt.md` in the memory-core skill and follow every step."*

---

## Status report format

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
  • MEMORY.md: <recently modified / not recent> — <evidence / none>

📊 MEMORY.md state:
  • Lines: <n>
  • Sections: <n>
  • Entries: ~<n>

⏱️ Last sweep: <appears to have run / no evidence found>

💡 Insight: <one-line observation>
```
