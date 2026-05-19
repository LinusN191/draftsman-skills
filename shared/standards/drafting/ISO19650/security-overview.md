# ISO 19650-5 — Security-Minded Approach to Information Management

**Source:** ISO 19650-5:2020

## Why Part 5 exists

Building information shared through a CDE can be misused if it falls into the wrong hands. ISO 19650-5 establishes a **security-minded approach** that determines (a) whether security controls are needed for a given project and (b) what proportionate controls to apply.

## When Part 5 applies

A security-minded approach is required (not just recommended) when any of these trigger conditions apply:

1. **Critical national infrastructure** — energy, water, telecoms, transport, food, finance, defence, government, civil nuclear, emergency services
2. **Defence + security-related assets** — military, intelligence
3. **Public-facing buildings with high-occupancy or high-value contents** — stadiums, museums, transport hubs
4. **Information about people** — privacy considerations (data protection law)
5. **Commercially sensitive information** — competitive advantage, intellectual property

## The 5-step process

1. **Identify trigger** — Does any of the above apply?
2. **Sensitivity assessment** — What aspects are sensitive? What's the risk if disclosed?
3. **Define security strategy** — Cryptographic, access control, governance, technical controls
4. **Implement controls** — Apply ISO/IEC 27000 series technical controls + project-specific controls
5. **Audit + review** — Continuous review; controls adjust as project context changes

## What Part 5 is NOT

- NOT a cybersecurity standard — refers to **ISO/IEC 27000 series** for technical controls
- NOT a privacy/data-protection standard — refers to applicable law (GDPR in EU, etc.)
- NOT a security-classification scheme — uses project-specific or jurisdiction-specific classifications

## Cross-references

- `part5-security.json` — engine-lookupable assessment process + classification placeholders
- `cde-workflow.json` — CDE states subject to security controls
- `../BS1192/terminology.md` — BS 1192 terminology equivalents
