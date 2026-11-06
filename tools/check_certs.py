"""Independent re-verifier for every certificate under certs/.

Annotation:
  ID: tools.check_certs
  CLASS: DEP-0
  WHAT: Re-verifies each certificate (decomposition, border, analysis, flattening,
        unsat) with its own exact arithmetic, cross-references the claims ledger,
        and exits nonzero on any failure.
  WHY:  Producer/checker independence (standards.md section 5.3): this module shares
        no code with analysis/ or search/ and imports no solver.
  STATUS: verified-numeric (self-verified by construction: it is the checker)
  COMPLETE: complete
  HYP: none
  DEPENDS: [dep/claims-ledger.yaml, certs/]
  GAP: none
  OWNER: repo-maintainer
  EVIDENCE: python3 tools/check_certs.py (CI gate; zero findings at seed commit)

Arithmetic: rationals via fractions.Fraction; F_p via residues; GF(2)[eps]/(eps^2)
via (const, eps) coefficient pairs. No floating point anywhere in this module
(Dep&CC 2.0 Chapter 18.1 classes exact and certified only); the one certified-numeric
comparison (mpmath enclosures) uses mpmath with declared precision.
"""

import json
import os
import sys
import time
from fractions import Fraction

from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING
import mpmath as mp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mp.mp.dps = 80

FAILURES = []
CHECKED = 0


def fail(msg):
    FAILURES.append(msg)
    print("  FAIL: %s" % msg)


def ok(msg):
    global CHECKED
    CHECKED += 1
    print("  ok: %s" % msg)


# ---------------------------------------------------------------------------
# Exact tensor arithmetic, independent re-implementation.

def field_of(name):
    if name == "Q":
        return ("Q", None)
    if name == "F_2":
        return ("Fp", 2)
    if name.startswith("F_"):
        return ("Fp", int(name[2:]))
    raise ValueError("unsupported field %r" % name)


def coeff(field, n):
    kind, p = field
    if kind == "Q":
        return Fraction(int(n))
    return int(n) % p


def entry_index_ok(pa, pb, pc, blocks):
    (s, (i, j)), (s2, (j2, k)), (s3, (i2, k2)) = pa, pb, pc
    if not (s == s2 == s3):
        return False
    a, b, c = blocks[s]
    return 0 <= i < a and 0 <= j < b and 0 <= k < c and j == j2 and i == i2 and k == k2


def mm_target(field, blocks):
    """Full dense representation as dict {index_triple: coeff} over all 64..n^3 entries."""
    out = {}
    for s, (a, b, c) in enumerate(blocks):
        for i in range(a):
            for j in range(b):
                for k in range(c):
                    out[((s, (i, j)), (s, (j, k)), (s, (i, k)))] = coeff(field, 1)
    return out


def vec_from_json(lst, field):
    return {(s, (i, j)): coeff(field, v) for (s, i, j, v) in lst}


def check_decomposition(cert, path):
    field = field_of(cert["field"])
    blocks = [tuple(b) for b in cert["tensor"]["blocks"]]
    target = mm_target(field, blocks)
    acc = {}
    for r, term in enumerate(cert["terms"]):
        u = vec_from_json(term["u"], field)
        v = vec_from_json(term["v"], field)
        w = vec_from_json(term["w"], field)
        # accumulate u (x) v (x) w over the full index space
        for (sA, (iA, jA)), uval in u.items():
            if uval == 0:
                continue
            for (sB, (jB, kB)), vval in v.items():
                if vval == 0:
                    continue
                for (sC, (iC, kC)), wval in w.items():
                    if wval == 0:
                        continue
                    key = ((sA, (iA, jA)), (sB, (jB, kB)), (sC, (iC, kC)))
                    acc[key] = acc.get(key, 0) + uval * vval * wval
    bad = []
    kind, pmod = field
    keys = set(acc) | set(target)
    for key in keys:
        lhs = acc.get(key, 0)
        rhs = target.get(key, 0)
        if kind == "Fp":
            eq = (lhs - rhs) % pmod == 0
        else:
            eq = lhs == rhs
        if not eq:
            bad.append(key)
    if bad:
        fail("%s: decomposition mismatches at %d index triples (e.g. %r)"
             % (os.path.basename(path), len(bad), bad[0]))
    else:
        ok("%s: %d-term decomposition exact over %s on the full index space"
           % (os.path.basename(path), len(cert["terms"]), cert["field"]))


def check_border(cert, path):
    """GF(2)[eps]/(eps^2): coefficient pairs (c0, c1); multiplication:
    (a0,a1)(b0,b1) = (a0 b0, a0 b1 + a1 b0). Requires sum_r u v w = eps^h T + tail."""
    field = field_of(cert["field"])
    if field != ("Fp", 2):
        fail("%s: border checker wired for F_2 only" % os.path.basename(path))
        return
    d = cert["ring"]["d"]
    if d != 2:
        fail("%s: border checker wired for d=2 only" % os.path.basename(path))
        return
    h = cert["order_h"]
    blocks = [tuple(b) for b in (cert["tensor"].get("blocks") or [cert["tensor"]["format"]])]
    if tuple(blocks[0]) != (2, 2, 2) or len(blocks) != 1:
        fail("%s: border checker wired for single <2,2,2> block" % os.path.basename(path))
        return
    A = [(i, j) for i in range(2) for j in range(2)]
    B = [(j, k) for j in range(2) for k in range(2)]
    C = [(i, k) for i in range(2) for k in range(2)]

    def parse(coefs):
        # coefs[r][idx][lev] -> r-th term vector
        out = []
        for r in range(len(coefs)):
            vec = []
            for idx in range(4):
                pair = []
                for lev in range(d):
                    pair.append(coeff(field, coefs[r][idx][lev]))
                vec.append(pair)
            out.append(vec)
        return out

    us = parse([t["u"] for t in cert["terms"]])
    vs = parse([t["v"] for t in cert["terms"]])
    ws = parse([t["w"] for t in cert["terms"]])
    # accumulate per (pa, pb, pc) the (c0, c1) coefficient
    acc = {}
    for r in range(len(us)):
        for aidx in range(4):
            (u0, u1) = us[r][aidx]
            if u0 == 0 and u1 == 0:
                continue
            for bidx in range(4):
                (v0, v1) = vs[r][bidx]
                if v0 == 0 and v1 == 0:
                    continue
                # product (u0 + u1 e)(v0 + v1 e) = (u0 v0, u0 v1 + u1 v0)
                p0 = (u0 * v0) % 2
                p1 = (u0 * v1 + u1 * v0) % 2
                if p0 == 0 and p1 == 0:
                    continue
                for cidx in range(4):
                    (w0, w1) = ws[r][cidx]
                    if w0 == 0 and w1 == 0:
                        continue
                    q0 = (p0 * w0) % 2
                    q1 = (p0 * w1 + p1 * w0) % 2
                    if q0 == 0 and q1 == 0:
                        continue
                    key = (A[aidx], B[bidx], C[cidx])
                    cur = acc.get(key, (0, 0))
                    acc[key] = ((cur[0] + q0) % 2, (cur[1] + q1) % 2)
    problems = 0
    for pa in A:
        for pb in B:
            for pc in C:
                t = 1 if (pa[0] == pc[0] and pa[1] == pb[0] and pb[1] == pc[1]) else 0
                c0, c1 = acc.get((pa, pb, pc), (0, 0))
                # eps^h T: level h carries T, other levels below h vanish; above h free
                if h == 0:
                    if c0 != t:
                        problems += 1
                elif h == 1:
                    if c0 != 0 or c1 != t:
                        problems += 1
                else:
                    fail("%s: checker wired for h in {0,1}" % os.path.basename(path))
                    return
    if problems:
        fail("%s: border witness wrong at %d entries" % (os.path.basename(path), problems))
    else:
        ok("%s: %d-term border witness over F_2[eps]/(eps^2), order h=%d, exact"
           % (os.path.basename(path), len(cert["terms"]), h))


def rank_exact(M, nrows, ncols, field):
    rows = [dict() for _ in range(nrows)]
    for (r, c), v in M.items():
        rows[r][c] = v
    kind, p = field
    rank = 0
    for col in range(ncols):
        piv = next((r for r in range(rank, nrows) if rows[r].get(col, 0) != 0), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        pv = rows[rank][col]
        for r in range(rank + 1, nrows):
            f = rows[r].get(col, 0)
            if f == 0:
                continue
            if kind == "Fp":
                f = (f * pow(pv, -1, p)) % p
                for c, v in rows[rank].items():
                    rows[r][c] = (rows[r].get(c, 0) - f * v) % p
            else:
                f = f / pv
                for c, v in rows[rank].items():
                    rows[r][c] = rows[r].get(c, Fraction(0)) - f * v
        rank += 1
    return rank


def check_flattening(cert, path):
    field = field_of(cert["field"])
    fmt = cert["tensor"]["format"]
    a, b, c = fmt
    comp = {c2["kind"]: c2 for c2 in cert["computations"]}
    # ordinary flattening A | (B, C)
    A = [(i, j) for i in range(a) for j in range(b)]
    B = [(j, k) for j in range(b) for k in range(c)]
    C = [(i, k) for i in range(a) for k in range(c)]
    M = {}
    for (i, j) in A:
        for (j2, k) in B:
            for (i2, k2) in C:
                if j == j2 and i == i2 and k == k2:
                    r = A.index((i, j))
                    col = B.index((j2, k)) * len(C) + C.index((i2, k2))
                    M[(r, col)] = coeff(field, 1)
    rk = rank_exact(M, len(A), len(B) * len(C), field)
    if rk != comp["ordinary_flattening"]["exact_rank"]:
        fail("%s: ordinary flattening rank %d != claimed %d"
             % (os.path.basename(path), rk, comp["ordinary_flattening"]["exact_rank"]))
    else:
        ok("%s: ordinary flattening rank %d re-derived" % (os.path.basename(path), rk))
    # Koszul p=1 (dim A = 4 scope)
    if "koszul_p1" in comp:
        import itertools
        pairs = list(itertools.combinations(range(len(A)), 2))
        rows = [(eta, beta) for eta in A for beta in B]
        cols = [(pair, cc) for pair in pairs for cc in C]
        Mk = {}
        for (i, j), (j2, k), (i2, k2) in [(pa, pb, pc) for pa in A for pb in B for pc in C
                                          if pa[1] == pb[0] and pa[0] == pc[0] and pb[1] == pc[1]]:
            # elementary rank-1 term e_pa (x) e_pb (x) e_pc, coefficient 1
            q = A.index((i, j))
            for r, (eta, beta) in enumerate(rows):
                if beta != (j2, k):
                    continue
                for p_col, (p1, p2) in enumerate(pairs):
                    e1 = 1 if eta == A[p1] else 0
                    e2 = 1 if eta == A[p2] else 0
                    co = e1 * (1 if p2 == q else 0) - e2 * (1 if p1 == q else 0)
                    if co:
                        col = p_col * len(C) + C.index((i2, k2))
                        Mk[(r, col)] = Mk.get((r, col), 0) + co
        rk_k = rank_exact(Mk, len(rows), len(cols), field)
        claimed = comp["koszul_p1"]["exact_rank"]
        if rk_k != claimed:
            fail("%s: koszul rank %d != claimed %d" % (os.path.basename(path), rk_k, claimed))
        else:
            ok("%s: koszul p=1 rank %d re-derived (bound R >= ceil(rank/3) = %d)"
               % (os.path.basename(path), rk_k, -(-rk_k // 3)))


def dec_out(s, direction, digits=30):
    with decimal_localcontext():
        d = Decimal(str(s))
        q = Decimal(1).scaleb(-digits)
        return d.quantize(q, rounding=ROUND_FLOOR if direction == "down" else ROUND_CEILING)


def decimal_localcontext():
    import decimal
    ctx = decimal.Context(prec=90)
    return decimal.localcontext(ctx)


def check_analysis(cert, path):
    kind = cert["kind"]
    if kind == "tensor_power_bound":
        base = cert["base"]
        decomp = os.path.join(ROOT, base["decomposition_cert"])
        if not os.path.exists(decomp):
            fail("%s: referenced decomposition cert missing: %s"
                 % (os.path.basename(path), base["decomposition_cert"]))
            return
        with open(decomp) as fh:
            dc = json.load(fh)
        if dc.get("schema") != "omega.cert.decomposition/1":
            fail("%s: referenced file is not a decomposition cert" % os.path.basename(path))
            return
        r = base["rank_bound"]
        val = mp.log(r) / mp.log(2)
        margin = mp.mpf(10) ** -32
        lo = mp.nstr(val - margin, 45)
        hi = mp.nstr(val + margin, 45)
        lo_d = dec_out(lo, "down")
        hi_d = dec_out(hi, "up")
        s_lo = Decimal(cert["bound"]["enclosure_lo"])
        s_hi = Decimal(cert["bound"]["enclosure_hi"])
        if not (lo_d <= s_lo and s_hi <= hi_d):
            fail("%s: stored enclosure [%s, %s] not inside recomputed [%s, %s]"
                 % (os.path.basename(path), s_lo, s_hi, lo_d, hi_d))
        else:
            ok("%s: log_2(%d) enclosure contained in recomputed enclosure at 80 digits"
               % (os.path.basename(path), r))
    elif kind == "asymptotic_sum_inequality":
        prods = cert["instance"]["products_nmp"]
        r = cert["instance"]["border_rank_input"]["r"]
        ev = os.path.join(ROOT, cert["instance"]["border_rank_input"]["evidence"])
        if not os.path.exists(ev):
            fail("%s: border-rank evidence file missing: %s" % (os.path.basename(path), ev))
        else:
            with open(ev) as fh:
                evc = json.load(fh)
            if evc.get("schema") != "omega.cert.decomposition/1":
                fail("%s: border-rank evidence is not a decomposition cert" % os.path.basename(path))
        f = lambda t: sum(mp.mpf(p) ** mp.mpf(str(t)) for p in prods) - mp.mpf(r)
        lo_s = cert["tau_enclosure"]["lo"]
        hi_s = cert["tau_enclosure"]["hi"]
        flo = f(Decimal(lo_s))
        fhi = f(Decimal(hi_s))
        if not (flo < 0 < fhi):
            fail("%s: tau enclosure does not bracket the root (f(lo)=%s, f(hi)=%s)"
                 % (os.path.basename(path), mp.nstr(flo, 10), mp.nstr(fhi, 10)))
        else:
            ok("%s: tau root bracketed by stored enclosure (f(lo)<0<f(hi), 80 digits)"
               % os.path.basename(path))
        # outward-rounding direction discipline
        if Decimal(lo_s) >= Decimal(hi_s):
            fail("%s: tau enclosure edges inverted" % os.path.basename(path))
        # consistency with a sibling bound if declared
        cc = cert.get("consistency_check")
        if cc:
            sib_path = os.path.join(ROOT, cc["against"])
            with open(sib_path) as fh:
                sib = json.load(fh)
            inter_lo = max(Decimal(cert["bound"]["enclosure_lo"]),
                           Decimal(sib["bound"]["enclosure_lo"]))
            inter_hi = min(Decimal(cert["bound"]["enclosure_hi"]),
                           Decimal(sib["bound"]["enclosure_hi"]))
            if inter_lo > inter_hi:
                fail("%s: enclosures of %s and %s do not intersect"
                     % (os.path.basename(path), cert["claim_id"], sib["claim_id"]))
            else:
                ok("%s: enclosures intersect: [%s, %s]"
                   % (os.path.basename(path), inter_lo, inter_hi))
    else:
        fail("%s: unknown analysis kind %r" % (os.path.basename(path), kind))


def check_unsat(cert, path):
    kind = cert["kind"]
    if kind != "exhaustive_enumeration":
        fail("%s: unsat kind %r not supported" % (os.path.basename(path), kind))
        return
    # Re-run the enumeration with an independent packing: supports as 64-bit masks.
    def mask(triples):
        m = 0
        for (i, j), (j2, k), (i2, k2) in triples:
            m |= 1 << (((i * 2 + j) * 4 + (j2 * 2 + k)) * 4 + (i2 * 2 + k2))
        return m
    A4 = [(i, j) for i in range(2) for j in range(2)]
    B4 = [(j, k) for j in range(2) for k in range(2)]
    C4 = [(i, k) for i in range(2) for k in range(2)]
    full_space = [(pa, pb, pc) for pa in A4 for pb in B4 for pc in C4]
    consistent = [((i, j), (j, k), (i, k))
                  for i in range(2) for j in range(2) for k in range(2)]
    target = mask(consistent)
    terms = []
    for ux in range(16):
        for vx in range(16):
            for wx in range(16):
                triples = [t for t in full_space
                           if (ux >> (t[0][0] * 2 + t[0][1])) & 1
                           and (vx >> (t[1][0] * 2 + t[1][1])) & 1
                           and (wx >> (t[2][0] * 2 + t[2][1])) & 1]
                terms.append(mask(triples))
    achievable = {0}
    achievable.update(terms)
    for x in range(len(terms)):
        tx = terms[x]
        for y in range(x, len(terms)):
            achievable.add(tx ^ terms[y])
    if target in achievable:
        fail("%s: enumeration re-run FOUND a decomposition with <= 2 terms; cert is wrong"
             % os.path.basename(path))
    else:
        ok("%s: enumeration re-run confirms no decomposition with <= 2 terms "
           "(%d candidate sums, symmetric-pair reduction)" % (os.path.basename(path), len(achievable)))
        if cert["result"]["target_achieved"] is not False:
            fail("%s: cert field target_achieved inconsistent" % os.path.basename(path))


def main():
    import yaml
    ledger_path = os.path.join(ROOT, "dep", "claims-ledger.yaml")
    with open(ledger_path) as fh:
        ledger = yaml.safe_load(fh)
    claim_ids = {row["id"] for row in ledger["claims"]}
    cert_dirs = ["decompositions", "border", "unsat", "analysis", "flattenings"]
    handlers = {
        "omega.cert.decomposition/1": check_decomposition,
        "omega.cert.border/1": check_border,
        "omega.cert.flattening/1": check_flattening,
        "omega.cert.analysis/1": check_analysis,
        "omega.cert.unsat/1": check_unsat,
    }
    n = 0
    for d in cert_dirs:
        full = os.path.join(ROOT, "certs", d)
        if not os.path.isdir(full):
            continue
        for fn in sorted(os.listdir(full)):
            if not fn.endswith(".json"):
                continue
            path = os.path.join(full, fn)
            with open(path) as fh:
                cert = json.load(fh)
            n += 1
            print("[%s] %s" % (cert.get("schema", "?"), os.path.relpath(path, ROOT)))
            h = handlers.get(cert.get("schema"))
            if h is None:
                fail("unknown schema %r in %s" % (cert.get("schema"), path))
                continue
            cid = cert.get("claim_id")
            if cid not in claim_ids:
                fail("%s: claim_id %r not in the ledger" % (fn, cid))
            h(cert, path)
    # ledger rows claiming verified statuses must have a cert and a checker
    for row in ledger["claims"]:
        if row["status"] in ("verified-numeric", "machine-checked"):
            if not row.get("cert") or not row.get("checker"):
                fail("%s: status %s requires cert and checker" % (row["id"], row["status"]))
    print("\n%d certificates checked, %d positive results, %d failures"
          % (n, CHECKED, len(FAILURES)))
    if FAILURES:
        sys.exit(1)


if __name__ == "__main__":
    main()
