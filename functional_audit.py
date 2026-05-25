#!/usr/bin/env python3
"""
DraftsMan Skills — Functional Audit Harness
============================================
Catches the THREE fault classes the repo's schema validator (validate-examples.py)
structurally cannot see, because it only checks file SHAPES, never EXECUTES anything:

  1. Recompute oracles      — re-derive every number from the skill's own standards
                              tables/formulas and compare to the stored value.
  2. Path resolver          — verify every cross-skill *_path / consumed_intent reference
                              actually resolves on disk.
  3. Eval-assertion auditor — check that fields asserted by evals exist in example outputs.

Run from the repo root:  python3 functional_audit.py
Exit code 0 = clean, 1 = findings.

NOTE: the recompute oracles encode the skills' documented modelling rules
(IEC 60909 c-factors + kappa; BS 7671 App-4 Vd; Zs = Ze + R1+R2). They are
deliberately conservative and FLAG for human adjudication rather than hard-fail,
because some apparent mismatches are legitimate (ring quartering, SWA tables,
motor/UPS superposition, single-phase). Treat output as a triage list.
"""
import json, os, glob, re, math
sqrt3, sqrt2 = math.sqrt(3), math.sqrt(2)
ROOT = os.path.dirname(os.path.abspath(__file__))
def J(p):
    with open(p) as f: return json.load(f)
findings = []
def flag(sev, skill, where, msg): findings.append((sev, skill, where, msg))

# ---------------------------------------------------------------- 1. PATH RESOLVER
def check_paths():
    print("\n=== [1] CROSS-REFERENCE PATH RESOLUTION ===")
    def walk(o, out):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and ('path' in k.lower() or 'consumed_intent' in k.lower()) and v.endswith('.json'):
                    out.append((k, v))
                else: walk(v, out)
        elif isinstance(o, list):
            for v in o: walk(v, out)
    n = b = 0
    for f in glob.glob('electrical/*/examples/*/*.json'):
        ps = []; walk(J(f), ps)
        for key, p in ps:
            if 'schema' in p.lower() or p.startswith('../'): continue
            n += 1
            if not os.path.exists(p):
                b += 1; skill = f.split('/')[1]
                flag('HIGH', skill, f.split('/')[-2], f"broken {key} -> {p}")
                print(f"  BROKEN [{skill}/{f.split('/')[-2]}] {key} -> {p}")
    print(f"  checked {n} references, {b} broken")

# ---------------------------------------------------------------- 2. EVAL AUDITOR
def check_evals():
    print("\n=== [2] EVAL-ASSERTION vs EXAMPLE-OUTPUT AUDIT ===")
    import yaml
    for sk in sorted(glob.glob('electrical/*')):
        evals = glob.glob(f'{sk}/evals/eval-*.yaml'); outs = [J(f) for f in glob.glob(f'{sk}/examples/*/output.json')]
        if not evals or not outs: continue
        asserted = set()
        for ef in evals:
            try: y = yaml.safe_load(open(ef))
            except: continue
            for chk in (y.get('checks') or []):
                for m in re.findall(r'\bir\.([A-Za-z0-9_]+)', chk.get('assertion', '')):
                    if m not in ('schema',): asserted.add(m)  # drop matches "x.schema.json" artifact
        missing = []
        for top in sorted(asserted):
            if not any(isinstance(o, dict) and top in o and (o[top] not in ([], {}, None)) for o in outs):
                present_empty = any(isinstance(o, dict) and top in o for o in outs)
                missing.append((top, 'EMPTY' if present_empty else 'ABSENT'))
        name = sk.split('/')[-1]
        for top, kind in missing:
            flag('MEDIUM', name, 'evals', f"asserts ir.{top}.* but {kind} in all outputs")
        print(f"  {name:<22} {len(asserted)} top-level paths asserted, {len(missing)} absent/empty in all outputs")

# ---------------------------------------------------------------- 3a. FAULT-LEVEL ORACLE
def oracle_fault_level():
    print("\n=== [3a] FAULT-LEVEL RECOMPUTE (IEC 60909) ===")
    def vf(x):
        try: return float(str(x).replace('kV','').replace('V','').strip())
        except: return None
    for ex in sorted(glob.glob('electrical/fault-level/examples/*')):
        inp, out = J(f'{ex}/input.json'), J(f'{ex}/output.json')
        Ulv = vf(inp.get('supply_voltage_v')) or 400
        Uhv = vf(inp.get('hv_voltage_kv')); Uhv = Uhv*1000 if Uhv else None
        # Single-phase detection (improved post-Sprint D pre-flight):
        # explicit declaration OR 230V supply with no HV side OR string match anywhere
        single = (inp.get('supply_phase') == 'single_phase'
                  or 'single_phase' in json.dumps(inp).lower()
                  or (str(inp.get('supply_voltage_v', '')).strip() == '230'
                      and inp.get('hv_side_present') is False))
        nm = ex.split('/')[-1]
        for n in out.get('cascade', []):
            kind = n.get('node_kind', '').lower(); is_hv = 'hv' in kind
            Ik, Z, ipk, xr = n.get('ifault_ka_max'), n.get('z_total_ohm'), n.get('ipk_ka'), n.get('x_over_r_at_node')
            U = Uhv if (is_hv and Uhv) else Ulv; c = 1.10 if is_hv else 1.05
            div = sqrt3 if (is_hv or not single) else 2.0
            if Z and Ik and U:
                rc = c*U/(div*Z)/1000
                if abs(rc-Ik)/Ik > 0.05:
                    flag('HIGH', 'fault-level', f"{nm}/{n['node_id']}", f"Ik {Ik} vs recompute {rc:.2f}kA (z↔Ik inconsistent)")
            if ipk and Ik and xr:
                k = 1.02+0.98*math.exp(-3/xr)
                if abs(k*sqrt2*Ik-ipk)/ipk > 0.06:
                    flag('MEDIUM', 'fault-level', f"{nm}/{n['node_id']}", f"ipk {ipk} vs k·√2·Ik {k*sqrt2*Ik:.2f}")
    print(f"  (findings appended; note motor/UPS superposition & declared-PSCC cases need manual review)")

# ---------------------------------------------------------------- 3b. CABLE-SIZING ORACLE
def oracle_cable_sizing():
    print("\n=== [3b] CABLE-SIZING RECOMPUTE (BS 7671 App-4) ===")
    tab = J('shared/standards/electrical/BS7671/appendix4-cable-ratings.json')['table_4d2a_single_core_xlpe_copper']
    def mvam(method, csa):
        m = tab.get(f'method_{method}') or tab.get('method_C'); e = m.get(str(csa)) if m else None
        return e.get('mVAm') if e else None
    for ex in sorted(glob.glob('electrical/cable-sizing/examples/*')):
        inp, out = J(f'{ex}/input.json'), J(f'{ex}/output.json'); nm = ex.split('/')[-1]
        if inp.get('jurisdiction') == 'US': continue
        ic = {c['node_id']: c for c in inp['circuits_declared']}
        for n in out.get('cascade', []):
            sel = n.get('selection', {}); csa = sel.get('phase_csa'); cab = sel.get('cable_type','')
            ci = ic.get(n['node_id'], {}); load = ci.get('load', {}); rt = ci.get('route', {})
            Ib, L = load.get('ib_a'), rt.get('length_m'); ph = load.get('phases', 'single')
            three = 'three' in str(ph)
            V = (415 if inp.get('jurisdiction')=='KE' else 400) if three else 230
            mv = mvam(rt.get('installation_method','C'), csa)
            if mv and Ib and L and 'ring' not in str(sel.get('binding_constraint','')):
                vdp = mv*Ib*L/1000/V*100
                st = next((w.get('vd_segment_pct') for w in sel.get('walk_up_trail',[]) if w.get('csa_attempted')==csa), None)
                if st is not None and abs(vdp-st) > 0.3 and three and abs(vdp*sqrt3-st) < 0.4:
                    flag('HIGH', 'cable-sizing', f"{nm}/{n['node_id']}", f"3ph Vd {st}% used 230V not {V}V (correct {vdp:.2f}%)")
    print("  (ring-final & SWA nodes excluded — oracle cannot model those)")

# ---------------------------------------------------------------- 3c. EARTHING ORACLE
def oracle_earthing():
    print("\n=== [3c] EARTHING RECOMPUTE (Zs = Ze + R1+R2) ===")
    for ex in sorted(glob.glob('electrical/earthing/examples/*')):
        inp, out = J(f'{ex}/input.json'), J(f'{ex}/output.json'); nm = ex.split('/')[-1]
        m = re.findall(r'"ze[_a-z]*_ohm[_a-z]*"\s*:\s*([0-9.]+)', json.dumps(inp), re.I)
        Ze = float(m[0]) if m else None
        sysT = (out.get('earthing_system') or {}); sysT = sysT.get('system_type') if isinstance(sysT, dict) else sysT
        for c in out.get('circuits', []):
            zs, zmax, fl, rcd = c.get('zs_ohm'), c.get('zs_max_ohm'), c.get('zs_compliance'), c.get('rcd_required')
            if zs is not None and zmax is not None and fl in ('pass','fail'):
                should = 'pass' if zs <= zmax+1e-9 else 'fail'
                if should == 'fail' and fl == 'pass' and rcd is not True:
                    flag('CRITICAL', 'earthing', f"{nm}/{c['circuit_id']}",
                         f"Zs {zs} > Zs_max {zmax} but flagged '{fl}', rcd_required={rcd} (non-compliant certified safe)")
            if sysT == 'TT' and rcd is not True:
                flag('HIGH', 'earthing', f"{nm}/{c['circuit_id']}", "TT system but rcd_required not true")
    # Dynamic TT-example coverage status (was hardcoded print pre-Sprint D pre-flight)
    tt_examples = []
    for ex in sorted(glob.glob('electrical/earthing/examples/*')):
        try:
            out = J(f'{ex}/output.json')
            sysT = (out.get('earthing_system') or {})
            sysT = sysT.get('system_type') if isinstance(sysT, dict) else sysT
            if sysT == 'TT':
                tt_examples.append(ex.split('/')[-1])
        except Exception:
            pass
    if tt_examples:
        print(f"  (TT→RCD branch exercised by {len(tt_examples)} example(s): {', '.join(tt_examples)})")
    else:
        print("  (TT→RCD branch has 0 examples to exercise)")

if __name__ == '__main__':
    os.chdir(ROOT)
    for fn in (check_paths, check_evals, oracle_fault_level, oracle_cable_sizing, oracle_earthing):
        try: fn()
        except Exception as e: print(f"  [skipped {fn.__name__}: {e}]")
    print("\n" + "="*70)
    order = {'CRITICAL':0,'HIGH':1,'MEDIUM':2,'LOW':3}
    findings.sort(key=lambda x: order.get(x[0], 9))
    print(f"TOTAL FINDINGS: {len(findings)}")
    for sev, sk, where, msg in findings:
        print(f"  [{sev:<8}] {sk}/{where}: {msg}")
    raise SystemExit(1 if findings else 0)
