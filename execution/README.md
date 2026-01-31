# Execution Scripts

This folder contains deterministic Python scripts. One script = one responsibility.

## Requirements

Every script must:
- Accept inputs via CLI arguments
- Read secrets from `.env` (never hardcode)
- Output via stdout (JSON preferred)
- Use exit codes: `0` success, `1+` categorized failures
- Validate its own outputs
- Fail loudly if something is wrong

## Guidelines

1. No reasoning or creativity — just reliable operations.
2. Scripts are composed by the orchestration layer (the agent).
3. Reuse existing scripts before writing new ones.

## Available Scripts

| Script | Purpose |
|--------|---------|
| `alert_user.py` | Emit audible alerts for task status |

## Adding New Scripts

1. Create a new `.py` file with a descriptive name.
2. Follow the requirements above.
3. Update this README with the new script.
4. Create or update the corresponding directive in `directives/`.
