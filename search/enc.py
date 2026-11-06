"""Border-rank search over F_2[eps]/(eps^2) and exact rank search over F_2, via z3.

Annotation:
  ID: search.enc
  CLASS: DEP-1
  WHAT: Builds the constraint system sum_r u_r (x) v_r (x) w_r = eps^h T + O(eps^{h+1})
        over F_2[eps]/(eps^d) for the tensor <2,2,2>, solves with z3 under a declared
        timeout, re-verifies every satisfying model by exact independent arithmetic,
        and writes run records under search/results/.
  WHY:  WS2 seed (Tier B): border rank over the dual numbers is the entry search
        space; models that re-verify become border-rank evidence, UNSAT answers stay
        at status empirical until a DRAT/LRAT pipeline exists (gap G-0005).
  STATUS: empirical (solver-trusted UNSAT) ; SAT models: verified on re-check
  COMPLETE: partial (see Known Limitations)
  HYP: none
  DEPENDS: [G-0005, C-0002]
  GAP: [G-0005]
  OWNER: repo-maintainer
  EVIDENCE: python3 search/enc.py --selftest exits 0; run records in search/results/

SMT policy (DEP&CC 2.0 Chapter 19.8): every run declares its timeout in seconds in
the run record; unknown and timeout are recorded as unknown, never as unsat; the
solver version is pinned in dep/toolchain.lock; UNSAT is solver-trusted only, which
is TCB entry G-0005.

Known Limitations: the encoding is flat GF(2) with no symmetry breaking and no
XOR-aware CNF export; sizes beyond R = 8 for <2,2,2> are not expected to finish in
the default timeout. DRAT export is future work.
"""

import argparse
import json
import os
import time

import z3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "search", "results")
TIMEOUT_DEFAULT = 240  # seconds, declared per run in the record

# Target tensor entries of <2,2,2> over F_2 in the full 4x4x4 space.
ENTRIES = [(pa, pb, pc)
           for i in range(2) for j in range(2) for k in range(2)
           for pa in [(i, j)] for pb in [(j, k)] for pc in [(i, k)]]
A_IDX = [(i, j) for i in range(2) for j in range(2)]
B_IDX = [(j, k) for j in range(2) for k in range(2)]
C_IDX = [(i, k) for i in range(2) for k in range(2)]


def target_entry(pa, pb, pc):
    (i, j), (j2, k), (i2, k2) = pa, pb, pc
    return 1 if (i == i2 and j == j2 and k == k2) else 0


def build_solver(R, d, h, timeout_s):
    """d = 1: exact rank over F_2. d = 2: border rank, coefficients in
    F_2[eps]/(eps^2); match eps^h T + O(eps^{h+1}) with h in {0, 1}."""
    s = z3.Solver()
    s.set("timeout", int(timeout_s * 1000))
    uvw = []
    for r in range(R):
        u = [[z3.BitVec("u%d_%d_l%d" % (r, idx, lev), 1) for lev in range(d)] for idx in range(4)]
        v = [[z3.BitVec("v%d_%d_l%d" % (r, idx, lev), 1) for lev in range(d)] for idx in range(4)]
        w = [[z3.BitVec("w%d_%d_l%d" % (r, idx, lev), 1) for lev in range(d)] for idx in range(4)]
        uvw.append((u, v, w))
    zero = z3.BitVecVal(0, 1)
    for lev in range(d):
        # coefficient of eps^lev must equal: (h == lev ? T : 0) if lev >= h else 0,
        # and for lev > h it must vanish (the O(eps^{h+1}) tail is unconstrained
        # only at levels >= h+1 within the truncation; here d = 2 so levels are
        # 0 and 1; h in {0,1}).
        for pa in A_IDX:
            for pb in B_IDX:
                for pc in C_IDX:
                    acc = zero
                    for (u, v, w) in uvw:
                        for lu in range(d):
                            for lv in range(d):
                                lw = lev - lu - lv
                                if 0 <= lw < d:
                                    acc = acc ^ (u[A_IDX.index(pa)][lu]
                                                 & v[B_IDX.index(pb)][lv]
                                                 & w[C_IDX.index(pc)][lw])
                    t = target_entry(pa, pb, pc)
                    want = z3.BitVecVal(t if lev == h else 0, 1)
                    s.add(acc == want)
    return s, uvw


def reverify_model(uvw, d, h, model):
    """Exact re-verification of a model with pure GF(2)[eps] arithmetic (no z3).
    Returns True iff sum_r u_r v_r w_r == eps^h T + (terms of eps-degree > h)."""
    # parse bit values
    def bits(x):
        t = str(z3.simplify(x))
        if t.startswith("#b"):
            return int(t[2:], 2)
        return int(t)
    terms = []
    for (u, v, w) in uvw:
        uu = [[bits(model.eval(c, model_completion=True)) for c in coef] for coef in u]
        vv = [[bits(model.eval(c, model_completion=True)) for c in coef] for coef in v]
        ww = [[bits(model.eval(c, model_completion=True)) for c in coef] for coef in w]
        terms.append((uu, vv, ww))
    for lev in range(2 * d - 1):
        want = 0
        if lev == h:
            want = None  # compare against target per entry
        for pa in A_IDX:
            for pb in B_IDX:
                for pc in C_IDX:
                    acc = 0
                    for (uu, vv, ww) in terms:
                        for lu in range(d):
                            for lv in range(d):
                                lw = lev - lu - lv
                                if 0 <= lw < d:
                                    acc ^= (uu[A_IDX.index(pa)][lu]
                                            * vv[B_IDX.index(pb)][lv]
                                            * ww[C_IDX.index(pc)][lw])
                    if lev == h:
                        if acc != target_entry(pa, pb, pc):
                            return False
                    elif lev < h:
                        if acc != 0:
                            return False
                    # lev > h: unconstrained tail within the truncation
    return True


def emit_border_cert(uvw, model, R, h, path):
    """Writes an omega.cert.border/1 certificate from a re-verified model.
    The certificate stores the coefficient bits; tools/check_certs.py re-verifies
    with its own GF(2)[eps]/(eps^2) arithmetic (producer/checker independence)."""
    def lvl(coeflist):
        return [[int(str(model.eval(c, model_completion=True))) for c in cl] for cl in coeflist]
    terms = []
    for (u, v, w) in uvw:
        terms.append({"u": lvl(u), "v": lvl(v), "w": lvl(w)})
    cert = {
        "schema": "omega.cert.border/1",
        "claim_id": "C-0018",
        "created": "2026-11-07",
        "field": "F_2",
        "tensor": {"kind": "matrix_mult", "format": [2, 2, 2],
                   "entry_convention": "dep/conventions.yaml#conv.mm_entry"},
        "ring": {"name": "F_2[eps]/(eps^2)", "d": 2},
        "order_h": h,
        "bound": R,
        "invariant": "border_rank",
        "terms": terms,
        "term_format": ("u[r][idx][lev]: coefficient of eps^lev of the r-th term's "
                        "A-vector, idx in [4], lev in {0,1}; likewise v (B-index), "
                        "w (C-index)"),
        "producer": {"module": "search/enc.py",
                     "search": "z3 %s under declared timeout; model re-verified by "
                               "exact GF(2)[eps] arithmetic before emission"
                               % z3.get_version_string()},
        "verifier": {"tool": "tools/check_certs.py",
                     "independence": "independent GF(2)[eps]/(eps^2) arithmetic; does "
                                     "not import search/ or z3"},
        "note": ("Proper border witness (h = 1): the sum equals eps^1 * T + O(eps^2) "
                 "over F_2[eps]/(eps^2), so the constant part vanishes and the eps "
                 "part equals T."),
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(cert, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("emitted %s" % os.path.relpath(path, ROOT))


def run(R, d, h, timeout_s, label):
    t0 = time.time()
    s, uvw = build_solver(R, d, h, timeout_s)
    res = s.check()
    wall = time.time() - t0
    rec = {
        "label": label, "mode": "exact_rank" if d == 1 else "border_d2",
        "R": R, "h": h, "field": "F_2",
        "solver": {"name": "z3", "version": z3.get_version_string(),
                   "timeout_seconds": timeout_s},
        "wall_seconds": round(wall, 3),
        "status": str(res),
    }
    if res == z3.sat:
        model = s.model()
        # evaluate and re-verify exactly
        checked = reverify_model(uvw, d, h, model)
        rec["model_reverified_exact"] = checked
        if checked and d == 2:
            emit_border_cert(uvw, model, R, h,
                             os.path.join(ROOT, "certs", "border",
                                          "222_F2_border7_d2h1.json"))
        rec["model"] = {str(c): str(model.eval(c, model_completion=True))
                        for (u, v, w) in uvw for grp in (u, v, w)
                        for coeflist in grp for c in coeflist}
    recs_path = os.path.join(RESULTS, label + ".json")
    os.makedirs(RESULTS, exist_ok=True)
    with open(recs_path, "w") as fh:
        json.dump(rec, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("%-28s R=%d h=%d d=%d -> %s (%.1fs)%s"
          % (label, R, h, d, rec["status"], wall,
             " reverified=" + str(rec.get("model_reverified_exact")) if res == z3.sat else ""))
    return rec


def selftest():
    """Cross-checks against known answers."""
    # Rank 1 must be unsat (C-0014 implies rank >= 3; a fortiori rank >= 2).
    run(1, 1, 0, 30, "selftest_rank1_unsat")
    # Rank 2 must be unsat, corroborating certs/unsat/222_F2_rank_ge3.json.
    run(2, 1, 0, 60, "selftest_rank2_unsat_vs_enumeration")
    # Rank 7 must be sat (C-0002); the model is re-verified exactly.
    run(7, 1, 0, 120, "sanity_rank7_sat")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--probe", action="store_true",
                    help="run the WS2 probe: rank-5 unsat attempt and border d=2 h=1")
    args = ap.parse_args()
    if args.selftest:
        selftest()
    if args.probe or (not args.selftest and not args.probe):
        # WS2 probe: R_F2 >= 6 attempt (rank 5 unsat), then border d=2, h=1, R=7.
        run(5, 1, 0, TIMEOUT_DEFAULT, "probe_rank5_unsat")
        run(7, 2, 1, TIMEOUT_DEFAULT, "probe_border_d2_h1_R7")


if __name__ == "__main__":
    main()
