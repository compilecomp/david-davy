"""Analysis certificates: tensor-power bound and asymptotic sum inequality instances.

Annotation:
  ID: analysis.sumineq
  CLASS: DEP-1
  WHAT: Solves the tau equation sum_i (n_i m_i p_i)^tau = r by certified bisection,
        encloses log_2(7), and emits omega.cert.analysis/1 certificates for the two
        asymptotic-sum-inequality instances and the tensor-power bound.
  WHY:  WS1 step 2 seed: the constraint system (shapes, certified border-rank input,
        tau equation, enclosure) is machine-checked end to end; the inequality
        theorem itself is external (gap G-0002) and no certificate pretends otherwise.
  STATUS: verified-numeric (enclosures) ; the exponent statements carry status
          proved-modulo through the ledger
  COMPLETE: complete (for the certified part)
  HYP: monotonicity of tau |-> sum_i prod_i^tau on [0, 1] for the shipped instances
       (each prod_i > 1, r between the values at 0 and 1; checked below)
  DEPENDS: [C-0004, C-0005, C-0006, C-0007, C-0008]
  GAP: [G-0001, G-0002]
  OWNER: repo-maintainer
  EVIDENCE: python3 analysis/sumineq.py exits 0

Enclosure discipline (dep/numerics.yaml, class certified):
  Working precision 60 decimal digits (mpmath mp.dps = 60). Bisection until the
  interval width is below 10^-40. The stored edges are the working enclosure rounded
  OUTWARD to 30 decimal digits: lower edge with ROUND_FLOOR, upper edge with
  ROUND_CEILING. tools/check_certs.py recomputes at 80 digits and requires the stored
  enclosure to contain the true root with margin.
"""

import json
import os
import sys
import decimal
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING

import mpmath as mp

mp.mp.dps = 60

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "certs", "analysis")


def tau_root(products, r):
    """Unique solution of sum_i prod_i^tau = r on [0,1], as an mp.mpf."""
    f = lambda t: sum(mp.mpf(p) ** t for p in products) - r
    lo, hi = mp.mpf(0), mp.mpf(1)
    assert f(lo) < 0 < f(hi), "instance must bracket the root on [0,1]"
    while hi - lo > mp.mpf(10) ** -40:
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return lo, hi, f


def enclosure_str(x_mp, direction, digits=30):
    """Decimal string of x rounded outward to `digits` decimals."""
    s = mp.nstr(mp.mpf(x_mp), 45)
    dec = Decimal(s)
    with decimal.localcontext() as ctx:
        ctx.prec = 80
        q = Decimal(1).scaleb(-digits)
        if direction == "down":
            return dec.quantize(q, rounding=ROUND_FLOOR)
        return dec.quantize(q, rounding=ROUND_CEILING)


def mul3(dec_str):
    """Exact multiply-by-3 of a decimal string, at raised precision."""
    with decimal.localcontext() as ctx:
        ctx.prec = 80
        return str(Decimal(dec_str) * 3)


def certify_tau(products, r):
    lo, hi, f = tau_root(products, r)
    # Margin discipline: the stored edges must satisfy f(lo_stored) < 0 < f(hi_stored)
    # when recomputed at higher precision; widen the working edges by 10^-38 before
    # rounding outward so the rounding step cannot flip the sign.
    margin = mp.mpf(10) ** -38
    lo_s = str(enclosure_str(lo - margin, "down"))
    hi_s = str(enclosure_str(hi + margin, "up"))
    return lo_s, hi_s


def main():
    os.makedirs(OUT, exist_ok=True)
    certs = []

    # --- C-0004: tensor power bound, omega <= log_2(7) -------------------------
    val = mp.log(7) / mp.log(2)
    margin = mp.mpf(10) ** -38
    lo = str(enclosure_str(val - margin, "down"))
    hi = str(enclosure_str(val + margin, "up"))
    certs.append({
        "schema": "omega.cert.analysis/1",
        "claim_id": "C-0004",
        "created": "2026-11-07",
        "kind": "tensor_power_bound",
        "base": {"tensor": "<2,2,2>", "field": "Q",
                 "decomposition_cert": "certs/decompositions/222_Q_7.json",
                 "rank_bound": 7},
        "chain": ("R(<2,2,2>) <= 7 implies R(<2^N,2^N,2^N>) <= 7^N for every N >= 1 by "
                  "submultiplicativity; omega <= log_2(7). The implication is recorded "
                  "under gap G-0001 and is not discharged by this certificate; the "
                  "arithmetic of the bound is."),
        "bound": {"symbolic": "omega <= log_2(7)",
                  "enclosure_lo": lo, "enclosure_hi": hi,
                  "digits": 30,
                  "decimal_display": "2.807354922057604 (truncated display of the "
                                     "enclosure; the enclosure is authoritative)"},
        "hypotheses": {"G-0001": ["H1 submultiplicativity", "H2 definition of omega"]},
        "producer": {"module": "analysis/sumineq.py",
                     "arithmetic": "certified (mpmath 60-digit working precision, "
                                   "outward rounding, see dep/numerics.yaml#num.log2_7)"},
        "verifier": {"tool": "tools/check_certs.py",
                     "independence": "recomputation at 80 digits and containment check"},
    })

    # --- C-0007: asymptotic sum inequality, mixed instance ---------------------
    prods_mixed = [8, 4]           # (2*2*2) and (1*2*2)
    r_mixed = 11
    lo, hi = certify_tau(prods_mixed, r_mixed)
    certs.append({
        "schema": "omega.cert.analysis/1",
        "claim_id": "C-0007",
        "created": "2026-11-07",
        "kind": "asymptotic_sum_inequality",
        "instance": {"shapes": [[2, 2, 2], [1, 2, 2]],
                     "products_nmp": prods_mixed,
                     "border_rank_input": {"r": r_mixed,
                                           "evidence": "certs/decompositions/222sum122_Q_11.json",
                                           "evidence_claim": "C-0006"},
                     "tau_equation": "8^tau + 4^tau = 11",
                     "nontriviality": "n_i m_i p_i > 1 for i = 0 (8 > 1)"},
        "theorem": {"statement": "omega <= 3*tau",
                    "source": "ext:alman2026speedup Theorem 1.1 (asymptotic sum "
                              "inequality, attributing ext:schonhage1981)",
                    "status_of_use": "external, carried by gap G-0002"},
        "tau_enclosure": {"lo": lo, "hi": hi, "digits": 30},
        "bound": {"symbolic": "omega <= 3*tau",
                  "enclosure_lo": mul3(lo), "enclosure_hi": mul3(hi),
                  "digits": 30},
        "producer": {"module": "analysis/sumineq.py",
                     "arithmetic": "certified (mpmath 60-digit bisection, outward "
                                   "rounding, see dep/numerics.yaml#num.tau_enclosure)"},
        "verifier": {"tool": "tools/check_certs.py",
                     "independence": "recomputes f at the stored edges at 80 digits and "
                                     "requires f(lo) < 0 < f(hi)"},
    })

    # --- C-0008: asymptotic sum inequality, uniform instance -------------------
    prods_uni = [8, 8]
    r_uni = 14
    lo2, hi2 = certify_tau(prods_uni, r_uni)
    certs.append({
        "schema": "omega.cert.analysis/1",
        "claim_id": "C-0008",
        "created": "2026-11-07",
        "kind": "asymptotic_sum_inequality",
        "instance": {"shapes": [[2, 2, 2], [2, 2, 2]],
                     "products_nmp": prods_uni,
                     "border_rank_input": {"r": r_uni,
                                           "evidence": "certs/decompositions/222sum222_Q_14.json",
                                           "evidence_claim": "C-0005"},
                     "tau_equation": "2 * 8^tau = 14",
                     "nontriviality": "n_i m_i p_i = 8 > 1"},
        "theorem": {"statement": "omega <= 3*tau",
                    "source": "ext:alman2026speedup Theorem 1.1",
                    "status_of_use": "external, carried by gap G-0002"},
        "tau_enclosure": {"lo": lo2, "hi": hi2, "digits": 30},
        "bound": {"symbolic": "omega <= 3*tau = log_2(7)",
                  "closed_form": "tau = log_8(7) = log_2(7)/3 exactly",
                  "enclosure_lo": mul3(lo2), "enclosure_hi": mul3(hi2),
                  "digits": 30},
        "consistency_check": {"against": "certs/analysis/strassen_power_bound.json",
                              "requirement": "the two bounds agree within the "
                                             "intersection of their enclosures"},
        "producer": {"module": "analysis/sumineq.py",
                     "arithmetic": "certified (as above)"},
        "verifier": {"tool": "tools/check_certs.py"},
    })

    names = {"C-0004": "strassen_power_bound.json",
             "C-0007": "sumineq_mixed.json",
             "C-0008": "sumineq_uniform222.json"}
    for cert in certs:
        path = os.path.join(OUT, names[cert["claim_id"]])
        with open(path, "w") as fh:
            json.dump(cert, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print("wrote %s" % os.path.relpath(path, ROOT))
    print("tau (mixed): [%s, %s]; 3*tau in [%s, %s]" % (lo, hi, mul3(lo), mul3(hi)))


if __name__ == "__main__":
    main()
