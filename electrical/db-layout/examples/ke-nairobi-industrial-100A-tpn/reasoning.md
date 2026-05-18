# Reasoning — KE Nairobi Industrial 100A TPN Board

## Site context

Same as `electrical/earthing/examples/ke-nairobi-industrial-tn-s/reasoning.md` site context (KPLC supply, Nairobi industrial area, light-engineering workshop). This db-layout example is the **upstream** producer for that earthing example — they share circuit IDs C01-C08.

## Board selection — MSP-100

Peak design load: ~33 kW combined (lighting + sockets + 3 motors + submain). At 0.85 PF, that's ~46 kVA, drawing ~65A per phase on a 415V TPN supply. 100A TPN intake gives 35% headroom + accommodates future growth.

Type-Tested Assembly (TTA) per BS EN 61439-1 (adopted by KS 1700 §531) — IP55 enclosure for industrial environment.

## Type-D MCB selection for compressor (C07)

C07 is a 7.5kW 3-phase reciprocating compressor. Start-up inrush ~6× FLC for 200ms. Type B MCB (Ia = 5×In) would nuisance-trip. Type C (Ia = 10×In) marginal. Type D (Ia = 20×In) accommodates inrush comfortably.

Trade-off: Type D demands lower Zs_max (covered in earthing example reasoning). Downstream earthing skill verifies Zs compliance.

## Type-C MCB selection for machine tools (C05, C06)

C05 (lathe 5.5kW) + C06 (drill 2.2kW) are 3-phase induction motors with lower inrush profile than the compressor. Type C MCB (Ia = 10×In) accommodates ~5-7× FLC start-up for ~100ms.

## Type-B MCB selection for everything else

C01-C04 + C08 are general-purpose lighting + socket + submain circuits. Type B (Ia = 5×In) gives best fault clearance + Zs_max headroom. Standard choice per BS 7671 / KS 1700.

## Universal socket-RCD policy (KS §411.3.3)

KS 1700 §411.3.3 mandates 30mA RCD on all socket circuits regardless of Zs compliance. Applied to:
- C03 (socket ring main workshop)
- C04 (socket radials office)
- C08 (submain to gate house — sockets present at downstream DB)

C01, C02 are lighting (no sockets — RCD optional). C05, C06 are dedicated motor circuits (RCD nuisance-trip risk; omitted by engineering judgement). C07 has 100mA RCD (motor-leakage-tolerant) per BS 7671 Reg 411.4.5.

## Selectivity verdict

100A switch-fuse upstream selectively trips against all 40A and smaller MCBs downstream. Verified per BS EN 60898 / BS EN 60947-2 selectivity tables.

## Downstream consumer

This board's intent-out.json is consumed by:
- `electrical/earthing/examples/ke-nairobi-industrial-tn-s/` (CPC sizing + Zs verification + RCD specification per circuit)
- (Future) `electrical/cable-sizing/` per Kenya market expansion
- (Future) `electrical/fault-level/` per cascade verification

## Tool deferrals

`calc.iec60909_cascade` not yet runtime-shipped — fault-level cascade for this board is computed inline by LLM using KPLC declared PFC + IEC 60909 simplified method. `tool_call_pending_for_fault_cascade` flag would apply if this skill carried that field; deferred to fault-level v2.x integration.
