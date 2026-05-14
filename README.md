# draftsman-skills

Open source MEP engineering skills for AI agents. Built for [DraftsMan](https://draftsman.io) and compatible with Claude Code, Cursor, and any agent that reads markdown skill files.

These skills encode professional building services engineering knowledge — the reasoning, standards, calculation methods, and output formats that a senior MEP engineer applies to every design task. Load them into your AI agent and it thinks like an engineer, not a chatbot.

## What's inside

```
drawings/
  lighting-layout/     BS EN 12464-1 lighting design → DXF-ready JSON
  sld/                 Single line diagrams → DXF-ready JSON
  db-layout/           Distribution board layouts → DXF-ready JSON
  cable-containment/   Cable tray and trunking routing → DXF-ready JSON
  riser/               LV riser diagrams → DXF-ready JSON
  schematic/           Schematic diagrams → DXF-ready JSON
  small-power/         Socket outlet layouts → DXF-ready JSON
  earthing/            Earthing layouts → DXF-ready JSON

calculations/
  cable-sizing/        BS 7671 Appendix 4 cable sizing
  lux/                 Room cavity ratio lux calculation
  load-schedule/       Demand load and diversity calculations
  voltage-drop/        BS 7671 voltage drop verification
  generator-sizing/    Generator kVA sizing
  fault-level/         Short circuit fault level (basic)
  power-factor/        PF correction capacitor sizing

documents/
  tender-report/       Full tender report drafting
  bq/                  Bill of quantities (NRM2 method)
  method-statement/    Method statement drafting
  cable-schedule/      Cable schedule document
  specification/       Technical specification writing
  om-manual/           O&M manual skeleton
  design-statement/    Design and access statement
```

## How to use

### In DraftsMan (native)
Skills are loaded automatically from `backend/app/skills/`. Say "load lighting-layout-skill" in chat.

### In Claude Code
```bash
# Add to your project
git clone https://github.com/LinusN191/draftsman-skills .draftsman-skills

# Reference in CLAUDE.md
echo "Skills: .draftsman-skills/drawings/lighting-layout/SKILL.md" >> CLAUDE.md
```

### In any agent
Copy the `SKILL.md` content into your system prompt. Each skill is self-contained.

## Skill structure

Each skill folder contains:

```
skill-name/
├── SKILL.md       ← the skill (load this into your agent)
├── EXAMPLES.md    ← 3–5 worked examples with full inputs and outputs
├── EVALS.md       ← evaluation criteria for testing the skill
└── assets/        ← reference tables, standard values, photometric data
```

## Standards covered

- **BS EN 12464-1:2021** — Lighting of indoor work places
- **BS 7671:2018** — IET Wiring Regulations 18th Edition
- **BS EN 60617** — Graphical symbols for electrical diagrams
- **BS 1192 / ISO 19650** — Layer naming and drawing management
- **BS 8888** — Technical product documentation
- **BS EN 1838:2013** — Emergency lighting
- **CIBSE SLL Code for Lighting**
- **CIBSE Guides A, B, F**
- **CDM Regulations 2015**
- **IEC 60364 series**

## Contributing

Contributions from MEP engineers, electrical engineers, and mechanical engineers are welcome and needed. See [CONTRIBUTING.md](CONTRIBUTING.md).

The most valuable contributions are corrections to engineering content — standards references, calculation methods, typical values. You don't need to be a developer to contribute. If you're a chartered engineer and you see something wrong, open an issue or submit a PR.

## Licence

MIT — use freely in commercial and open source projects.
