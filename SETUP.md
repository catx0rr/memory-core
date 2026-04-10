# Memory-Core Status — First-Time Setup

Agent-run first-time configuration for the memory-core status observer.
Follow every step in order.

**Prerequisites (must be complete before this runs):**
- OpenClaw installed with built-in memory-core dreaming
- The `memory-core` skill is installed somewhere in the agent's skill roots
- `MEMORY.md` exists in the workspace (at least a stub)

This setup must **not** assume the skill lives at a fixed path.
The skill may be loaded from any configured skill root or `skills.load.extraDirs`.

---

## Step 0: Discover the Skill Location

Before running setup, determine where the `memory-core` skill is installed.

### 0a. Try standard skill roots first

```bash
for root in \
  "$HOME/.openclaw/workspace/skills" \
  "$HOME/.openclaw/workspace/.agents/skills" \
  "$HOME/.agents/skills" \
  "$HOME/.openclaw/skills"
do
  if [ -f "$root/memory-core/SKILL.md" ]; then
    export SKILL_ROOT="$root/memory-core"
    break
  fi
done
```

### 0b. If not found, check configured `extraDirs`

```bash
if [ -z "${SKILL_ROOT:-}" ]; then
  # Check extraDirs for the skill
  for root in $(openclaw config get skills.load.extraDirs --json 2>/dev/null | python3 -c "import json,sys; [print(d) for d in json.load(sys.stdin)]" 2>/dev/null); do
    if [ -f "$root/memory-core/SKILL.md" ]; then
      export SKILL_ROOT="$root/memory-core"
      break
    fi
  done
fi
```

### 0c. Fail if still unresolved

```bash
if [ -z "${SKILL_ROOT:-}" ] || [ ! -f "$SKILL_ROOT/SKILL.md" ]; then
  echo "Could not locate memory-core skill directory."
  echo "Install the skill first or ensure skills.load.extraDirs includes its parent root."
  exit 1
fi

echo "Using SKILL_ROOT=$SKILL_ROOT"
```

---

## Step 1: Verify Dreaming Is Enabled

```
/dreaming status
```

Confirm built-in memory-core dreaming is active.
If dreaming is disabled, enable it first before proceeding.

---

## Step 2: Run Baseline Check and Create Cron

Resolve this skill directory as `SKILL_ROOT`, then read and execute:

```
$SKILL_ROOT/runtime/create-cron-prompt.md
```

This is a **one-time task** that:
- Verifies the dreaming baseline
- Scans pre-existing evidence surfaces
- Creates the recurring `memory-core-status` cron at `30 3 * * *`

---

## Post-Setup Checklist

- [ ] `SKILL_ROOT` was resolved correctly
- [ ] Dreaming is enabled
- [ ] Baseline check completed (evidence scan + MEMORY.md metrics)
- [ ] Cron `memory-core-status` is scheduled at `30 3 * * *`
- [ ] Cron payload references the absolute path to `runtime/memory-core-prompt.md`

---

## Cleanup

These are optional cleanup targets if the skill repo includes development-only files:

- [ ] `.git`
- [ ] `LICENSE`
- [ ] `README.md`
- [ ] `INSTALL.md`
- [ ] `SETUP.md`

Do not remove:
- `SKILL.md`
- `runtime/`
- `scripts/`
