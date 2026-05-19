# ISO 7200 — Title Block Field Definitions

**Source:** ISO 7200:2004 §4 (Data fields). Narrative purpose of each mandatory + optional field.

## Mandatory fields (4)

These MUST appear in the identification zone of every technical drawing title block.

### identification_number

The unique drawing identifier within the project. Typically follows ISO 19650 / BS 1192 naming convention: `Project-Originator-Volume-Level-Type-Role-Number`.

**Example:** `ABC-XYZ-Z1-04-DR-E-0001`

### title_subtitle

The drawing title — what the drawing depicts. Optionally followed by a subtitle clarifying the drawing's purpose or scope.

**Examples:**
- `Single Line Diagram — Main Switchboard`
- `Ground Floor Lighting Layout`
- `Riser Diagram — Power Distribution`

### issuing_organization

The producing organization — the firm or consultant releasing the drawing. May include logo + address.

**Examples:**
- `ABC Consulting Engineers Ltd.`
- `XYZ Architects`

### approval_date

The date the drawing was approved (suitable for use). Format: ISO 8601 (YYYY-MM-DD).

**Example:** `2026-05-19`

## Optional fields (12 recommended)

These MAY appear adjacent to the identification zone if relevant.

### scale

The drawing scale per ISO 5455. Use `NTS` for not-to-scale (SLDs, schematics, risers).

**Examples:** `1:100`, `1:50`, `NTS`

### sheet_number

Sheet N of M for multi-sheet drawings. Format: `N/M`.

**Example:** `1/3` (sheet 1 of 3)

### paper_size

The sheet size per ISO 5457 (`A0`-`A4`) or ANSI (`Arch_A`-`Arch_E`).

**Examples:** `A1`, `Arch_D`

### language

The drawing language per ISO 639-1 two-letter code.

**Examples:** `en` (English), `fr` (French), `de` (German)

### designer / drawer / checker / approver

Persons responsible for each step of the drawing lifecycle. Designer = whose design the drawing depicts; drawer = who drafted; checker = who reviewed; approver = who signed off.

### revision

The current revision identifier per BS 1192 / ISO 19650.

**Examples:** `P03` (preliminary rev 3), `C01` (contract rev 1)

### revision_history

A table of past revisions: revision | date | description | author.

### project_reference

A cross-reference to the project name or code.

### copyright_notice

A copyright statement. Often required for archival + IP protection.

## Cross-references

- `title-block-fields.json` — engine-lookupable field list
- `layout-conventions.json` — identification zone dimensions per sheet size
- `../ISO5457/sheet-sizes.json` — sheet dimensions (ISO 7200 identification zone fits within ISO 5457 title block region)
