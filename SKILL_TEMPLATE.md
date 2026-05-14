---
name: skill-name
description: "One sentence: what this skill does, what standard it applies, what it outputs. Used as the trigger description for skill discovery."
version: 1.0.0
discipline: electrical | mechanical | both
standards:
  - Standard name and year
output_format: json | markdown | xlsx | docx
tags:
  - drawings | calculations | documents
  - discipline tag
---

# Skill Name — DraftsMan MEP Engineering Skill

## Role

One paragraph. Who is the agent when this skill is active? What is their
level of experience? What market do they work in? What are they producing?

The agent must have a clear professional identity — not "an AI assistant"
but "a senior electrical engineer with 20 years of UK commercial experience."

## Standards You Apply

Table of every standard referenced in this skill, with the specific clause
or table numbers used. Engineers reviewing this skill need to verify every
reference.

| Standard | Clause / Table | Application |
|---|---|---|
| Standard name:year | Clause X.X | What it governs in this skill |

## Inputs Required

List every input the skill needs before it can produce output. Separate
required inputs from optional ones. State what happens when an optional
input is missing (default value or assumption).

### Required
- Input name — description, units, valid range

### Optional (with defaults)
- Input name — description, default value when not provided

## How You Think Before Acting

Numbered steps. Every step must be shown in the chat response before
the JSON output is emitted. Engineers review the reasoning, not just
the output.

Each step must include:
- What is calculated or decided
- The formula or rule applied
- The standard reference
- The default assumption if data is missing (flagged with [ASSUMPTION: ...])

### Step 1 — [Step name]
...

### Step 2 — [Step name]
...

## What You Never Do

Bullet list of hard constraints. Things that would produce incorrect,
unsafe, or non-compliant outputs. Be specific.

- Never [specific action] because [consequence]
- Never guess [specific data type] — always flag as [SPECIFY] or ask

## Output Format

The exact JSON structure the skill produces. Every field documented.
This JSON is passed directly to the ezdxf renderer or the export engine.

```json
{
  "field_name": "description of value and units"
}
```

## Compliance Flags

How the skill signals non-compliance, assumptions, or missing data in its
output. Must include:

- `[ASSUMPTION: ...]` — for every assumed value not confirmed by the engineer
- `[NON-COMPLIANCE RISK: ...]` — when a client requirement conflicts with a standard
- `[SPECIFY: ...]` — for required data the skill cannot assume

---

*Version history in CHANGELOG.md. Evaluation criteria in EVALS.md.
Worked examples in EXAMPLES.md.*
