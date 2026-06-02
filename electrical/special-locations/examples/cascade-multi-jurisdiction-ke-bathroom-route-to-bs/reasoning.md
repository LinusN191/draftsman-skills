# Reasoning — cascade-multi-jurisdiction-ke-bathroom-route-to-bs

## Cascade context

KE jurisdiction cascade — same bathroom geometry, anchors, zones,
constraints, and fixtures as cascade #9 (`cascade-lighting-layout-uk-bathroom`),
but **every regulatory citation** in `zones[]._clause_citation`,
`zones[].derivation_clause`, and `electrical_constraints[]._clause_citation`
routes through **KS 1700:2018 §313** to **BS 7671:2018+A2:2022**.

This is the **Africa-first** jurisdiction per CLAUDE.md build strategy.

## Step 0 — Cascade prereq check

- `_special_locations_cascade_source.upstream_consumer_intent_location` set
  → `full_analysis` mode.
- `jurisdiction: "KE"` triggers KS 1700:2018 §313 routing for all
  clause citations.
- `existing_fixtures[]` carry `_consumed_from` markers identifying the
  KE-jurisdiction synthetic upstream lighting-layout intent.

## Step 1 — Room classification

Identical to cascade #9: bathroom; 2 700 × 2 100 mm; ceiling 2 400 mm.

## Step 2 — Anchor inventory

Identical to cascade #9: `bath_1` + `shower_1`. Both
`_extraction_source: architectural_drawing_extraction`.

## Step 3 — Zone derivation

Same 5 zones as cascade #9, with `derivation_clause` and
`_clause_citation` routed via KS 1700:2018 §313.

### Citation routing form per CLAUDE.md

CLAUDE.md specifies the KE citation form:

> `KS 1700:2018 § 313 (route to BS 7671)` (cite the local norm and the
> British route it references).

In this cascade:

| field                       | form |
|-----------------------------|------|
| `zone.derivation_clause`    | `"KS 1700:2018 §313 (route to BS 7671:2018+A2:2022 §701)"` |
| Zone 0 `_clause_citation`   | `"KS 1700:2018 §313 (route to BS 7671:2018+A2:2022 §701.414.4.5 (SELV ≤12 V in Zone 0) + §701.411.3.3 (30 mA RCD blanket))"` |
| Zone 1 `_clause_citation`   | `"KS 1700:2018 §313 (route to BS 7671:2018+A2:2022 §701 + §701.411.3.3 (30 mA RCD))"` |
| Zone 2 `_clause_citation`   | `"KS 1700:2018 §313 (route to BS 7671:2018+A2:2022 §701 + §701.512.3 (socket ≥3 m from Zone 1))"` |
| `rcd_blanket_by_room._clause_citation` | `"KS 1700:2018 §313 (route to BS 7671:2018+A2:2022 §701.411.3.3)"` |

## Step 4 — Per-zone safety properties

Identical numbers/values to cascade #9: Zone 0 IPx7+SELV; Zones 1 & 2
IPx4 + 30 mA RCD; Zone 2 3 m socket-distance. KE local enforcement of
all values via the §313 routing to BS 7671:2018+A2:2022 §701.

## Step 5 — Electrical constraint derivation

Single constraint: `rcd_blanket_by_room`. Cited via KS 1700:2018 §313
routing to BS 7671:2018+A2:2022 §701.411.3.3.

## Step 6 — Consume lighting-layout intent

Same 3 fixtures as cascade #9 (2 luminaires + 1 shaver socket). All
compliant against §701 zones (the §701 mathematics is unchanged because
KS 1700:2018 §313 routes BS 7671 in directly — the local clauses ARE the
British clauses).

## Step 7 — INV-08 sub-rule walk-through

Identical mathematics to cascade #9. 12 sub-rule evaluations (3
fixtures × 4 sub-rules) all PASS.

The INV evidence prose narrates the underlying rule reasoning and
remains in BS 7671 form internally — the **jurisdiction routing applies
to the recorded `_clause_citation` fields in the IR**, not the prose
narration of how the rules are applied. (Citations are the
auditable-evidence record; prose is the reasoning.)

For example, INV-04's evidence reads:

> "...rcd_blanket_by_room constraint present with rcd_rating_ma=30 and
> sauna_heater_excluded=false per KS 1700:2018 §313 (route to
> BS 7671:2018+A2:2022 §701.411.3.3)..."

— the citation here is in the KE-routed form because INV-04 explicitly
narrates the citation as evidence.

## Step 8 — Invariants

All 10 INVs PASS:

- **INV-01** zone catalogue: 2 anchors → 5 zones; overlaps declared.
  PASS.
- **INV-02** audit ↔ flags 1:1. PASS.
- **INV-03** medical IT N/A. PASS vacuously.
- **INV-04** rcd_blanket_by_room PRESENT, with KE-routed citation.
  PASS.
- **INV-05** main equipotential bonding N/A. PASS vacuously.
- **INV-06** whirlpool pump N/A. PASS vacuously.
- **INV-07** ELV separation N/A. PASS vacuously.
- **INV-08** 12/12 sub-rule evaluations PASS.
- **INV-09** anchor provenance strongest tier. PASS.
- **INV-10** rollup self-consistency holds. PASS.

## Step 9 — Consumer-side hand-off expectations

### lighting-layout v1.6 INV-12 (cross-check)

Operates identically to cascade #9 — the cascade compliance verdict and
empty `non_compliance_flags[]` propagate. The downstream
lighting-layout output IR's own `_clause_citation` fields must also
follow KE jurisdiction routing form. The special-locations intent
payload propagates `jurisdiction: KE` (via the upstream lighting-layout
intent linkage); consumers must mirror.

### db-layout v1.5 INV-16 sub-check 3 (RCD enforcement)

Operates identically to cascade #15 — every bathroom-serving circuit
must route through a 30 mA RCD. The db-layout side's clause citations
for this circuit's protective device must follow `KS 1700:2018 §313
(route to BS 7671:2018+A2:2022 §701.411.3.3)`.

## Step 10 — KE jurisdiction notes

- **KS 1700:2018** is Kenya's primary electrical installation standard;
  §313 is the jurisdiction-routing clause that explicitly references
  BS 7671 for special-location detail not bespoke to KS.
- **Africa-first build strategy.** Per CLAUDE.md, KE is the
  jurisdiction we lead with for African markets — the routing chain
  models the engineering reality (KE local statute + BS 7671 detail).
- **BS EN 61558-2-5** (shaver socket isolating transformer derogation)
  applies internationally via the IEC mirror; the KE installation can
  directly reference the BS EN. The §701 zone-table derogation for
  shaver sockets carries unchanged.

## Step 11 — Honest disclosures

- **Synthetic upstream lighting-layout intent.** lighting-layout v1.6
  hand-off not yet shipped; cascade contract integrity verified via
  golden CI Pass 4.
- **Citation discipline.** This cascade is the canonical demonstration
  of the CLAUDE.md KE citation form across every IR clause site.
  Reviewer audit-pass: every citation containing `BS 7671` MUST be
  wrapped in `KS 1700:2018 §313 (route to …)` form when
  `jurisdiction=KE`.
- **Engineering math is identical.** The KE installation follows
  BS 7671 §701 mathematics; nothing about the zoning or RCD
  requirements changes — only the citation form.

## Step 12 — Failure modes considered

If a `_clause_citation` field omitted the `KS 1700:2018 §313 (route to
…)` wrapper and cited `BS 7671:2018+A2:2022 §701` directly with
`jurisdiction=KE`, this would be a CITATION DISCIPLINE failure caught
by a reviewer C-check (not by INVs directly — the INVs verify
engineering substance, not citation form). For C-check completeness,
this cascade demonstrates the discipline at every clause site.

## Cross-references

- C.1 source: `electrical/special-locations/examples/uk-bathroom-standard-bath-and-shower/`
- Spec §9.2 cascade row 17: PASS case (KS 1700 §313 routing)
- CLAUDE.md "Citation form per jurisdiction" — KE section
- Plan portion 3 Task C.2 Step 7
