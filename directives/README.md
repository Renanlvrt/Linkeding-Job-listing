# Directives

This folder contains Standard Operating Procedures (SOPs) written in Markdown.

## Purpose

Each directive defines a repeatable workflow with:
- **Goal** — What this workflow accomplishes
- **Required inputs** — What the agent needs to start
- **Script(s) to invoke** — Which `execution/` scripts to run
- **Expected outputs** — What success looks like
- **Edge cases + recovery** — How to handle failures

## Guidelines

1. Write directives for a capable mid-level employee who's never seen this before.
2. When logic changes materially, keep old versions (`v1`, `v2`) for fallback.
3. Update directives as you learn (API limits, timing, edge cases).
4. Never overwrite directives without asking first.

## Example Structure

```markdown
# Directive: [Workflow Name]

## Goal
[What this accomplishes]

## Required Inputs
- Input 1
- Input 2

## Scripts
- `execution/script_name.py`

## Expected Outputs
- Output description

## Edge Cases
- Case 1: [How to handle]
- Case 2: [How to handle]
```
