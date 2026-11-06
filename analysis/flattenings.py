"""Flattening rank certificates, exact arithmetic over Q or F_p.

Annotation:
  ID: analysis.flattenings
  CLASS: DEP-1
  WHAT: Constructs the (A (x) B) against C flattening matrix and the p=1 Koszul
        flattening matrix of a matrix multiplication tensor, computes exact ranks,
        and emits omega.cert.flattening/1 certificates.
  WHY:  Tier C pipeline seed (WS4): mechanized rank lower bounds with certifiable
        output at a size where results are independently checkable.
  STATUS: verified-numeric
  COMPLETE: complete
  HYP: 'rank of the flattening <= R(T)' and 'rank of the p=1 Koszul flattening
       <= 3 R(T) for dim A = 4'; both derived in this module, see DERIVATIONS below
  DEPENDS: [C-0003]
  GAP: [G-0003]
  OWNER: repo-maintainer
  EVIDENCE: python3 analysis/flattenings.py exits 0

DERIVATIONS (in-module, one inference granularity unit each):
  D1 (ordinary flattening). T = sum_r u_r (x) v_r (x) w_r. The flattening matrix of
     a single rank-1 term is the outer product (u (x) v) w^T of rank at most 1. The
     rank of a sum of matrices is at most the sum of ranks. Hence
     rank_F(T_{AB|C}) <= R(T). (justification: algebra:ring; subadditivity of rank)
  D2 (Koszul, p=1, dim A = 4). The Koszul flattening is the linear map
     K_T: A (x) B* -> Lambda^2 A (x) C*,  eta (x) beta |-> sum_r (eta wedge u_r)
     beta(v_r) (x) w_r, where beta pairs with v_r through the standard dot product.
     K_T is linear in T. For one rank-1 term the map factors as
     (eta -> eta wedge u_r) (x) (beta -> beta(v_r)) (x) w_r, of rank at most
     rank(eta -> eta wedge u_r). For u_r != 0 the kernel of eta -> eta wedge u_r is
     span(u_r) (eta wedge u_r = 0 iff eta and u_r are proportional, p = 1), so the
     rank is dim A - 1 = 3. Summing: rank(K_T) <= 3 R(T). Consequently
     R(T) >= ceil(rank(K_T) / 3).
  Scope: D2 is stated and used only for p = 1 and dim A = 4 (the 2x2x2 case). The
  general normalization for larger shapes is not shipped here.
"""

import itertools
import json
import os
import sys
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "certs", "flattenings")


class Field:
    """Minimal exact field; kept local so this module has no analysis/ import."""

    def __init__(self, kind, p=None):
        assert kind in ("Q", "Fp")
        self.kind, self.p = kind, p

    def zero(self):
        return Fraction(0) if self.kind == "Q" else 0

    def of(self, n):
        return Fraction(n) if self.kind == "Q" else n % self.p


def mm_dense(field, a, b, c):
    """Dense dict {(i,j),(j2,k),(i2,k2)} -> coeff of <a,b,c> (dep/conventions.yaml)."""
    out = {}
    for i in range(a):
        for j in range(b):
            for k in range(c):
                out[((i, j), (j, k), (i, k))] = field.of(1)
    return out


def rank_exact(M, nrows, ncols, field):
    """Gaussian elimination with exact entries. M: {(r,c): coeff}. Returns rank."""
    rows = [dict() for _ in range(nrows)]
    for (r, c), v in M.items():
        rows[r][c] = v
    rank = 0
    for col in range(ncols):
        pivot = next((r for r in range(rank, nrows)
                      if rows[r].get(col, field.zero()) != field.zero()), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pv = rows[rank][col]
        for r in range(rank + 1, nrows):
            f = rows[r].get(col, field.zero())
            if f == field.zero():
                continue
            if field.kind == "Fp":
                f = (f * pow(pv, -1, field.p)) % field.p
                for c, v in rows[rank].items():
                    rows[r][c] = (rows[r].get(c, 0) - f * v) % field.p
            else:
                f = f / pv
                for c, v in rows[rank].items():
                    rows[r][c] = rows[r].get(c, Fraction(0)) - f * v
        rank += 1
    return rank


def ordinary_flattening(field, a, b, c):
    """Rows: A-index (i,j). Cols: (B-index (j2,k), C-index (i2,k2)) pairs.
    Entry T[(i,j),(j2,k),(i2,k2)]."""
    dense = mm_dense(field, a, b, c)
    A = [(i, j) for i in range(a) for j in range(b)]
    B = [(j, k) for j in range(b) for k in range(c)]
    C = [(i, k) for i in range(a) for k in range(c)]
    M = {}
    for r, ar in enumerate(A):
        for bi, br in enumerate(B):
            for ci, cc in enumerate(C):
                val = dense.get((ar, br, cc), 0)
                if val:
                    M[(r, bi * len(C) + ci)] = val
    return M, len(A), len(B) * len(C)


def koszul_p1(field, a, b, c):
    """K_T for p=1 per DERIVATION D2, on <a,b,c>. Requires a*b = 4 (dim A = 4)."""
    assert a * b == 4, "D2 scope is dim A = 4"
    A = [(i, j) for i in range(a) for j in range(b)]
    B = [(j, k) for j in range(b) for k in range(c)]
    C = [(i, k) for i in range(a) for k in range(c)]
    dense = mm_dense(field, a, b, c)
    # Express T as a sum of elementary rank-1 terms from its dense entries; D2 is
    # per-term, and K_T is linear in T, so summing over dense entries is exact.
    entries = [(pa, pb, pc) for (pa, pb, pc), v in dense.items() if v]
    pairs = list(itertools.combinations(range(len(A)), 2))
    rows = [(eta, beta) for eta in A for beta in B]
    cols = [(pair, cc) for pair in pairs for cc in C]
    M = {}
    for r, (eta, beta) in enumerate(rows):
        for (pa, pb, pc) in entries:  # single-entry rank-1 term, coefficient 1
            i, j = pa
            j2, k = pb
            i2, k2 = pc
            # beta pairs with the B-part (j2, k): beta(v) = beta(j2, k)
            bv = 1 if beta == (j2, k) else 0
            if not bv:
                continue
            # eta wedge u where u = e_(i,j): coefficient on pair (p,q) is
            # [eta wedge u]_{p,q} = eta_p u_q - eta_q u_p with u_q = 1 at index (i,j).
            q = A.index((i, j))
            # [eta ^ u]_{p1,p2} = eta_{p1} u_{p2} - eta_{p2} u_{p1}; u is supported
            # only at index q, so this is eta_{p1}[p2==q] - eta_{p2}[p1==q].
            for (p_col, (p1, p2)) in enumerate(pairs):
                e1 = 1 if eta == A[p1] else 0
                e2 = 1 if eta == A[p2] else 0
                co = e1 * (1 if p2 == q else 0) - e2 * (1 if p1 == q else 0)
                if co:
                    col = p_col * len(C) + C.index((i2, k2))
                    M[(r, col)] = M.get((r, col), field.zero()) + field.of(co)
    return M, len(rows), len(cols)


def main():
    os.makedirs(OUT, exist_ok=True)
    fq = Field("Q")
    M, nr, nc = ordinary_flattening(fq, 2, 2, 2)
    rk_flat = rank_exact(M, nr, nc, fq)
    Mk, nrk, nck = koszul_p1(fq, 2, 2, 2)
    rk_kos = rank_exact(Mk, nrk, nck, fq)
    koszul_bound = -(-rk_kos // 3)  # ceil division; DERIVATION D2
    # Self-tests from the derivations.
    assert rk_flat == 4, rk_flat
    # Rank-1 sanity for D1: single dense entry must give flattening rank 1.
    M1 = {(0, 0): 1}
    assert rank_exact(M1, 4, 16, fq) == 1
    print("ordinary flattening rank of <2,2,2> over Q: %d (bound D1: R >= %d)" % (rk_flat, rk_flat))
    print("koszul p=1 rank of <2,2,2> over Q: %d of %dx%d (bound D2: R >= %d)"
          % (rk_kos, nrk, nck, koszul_bound))
    cert = {
        "schema": "omega.cert.flattening/1",
        "claim_id": "C-0003",
        "created": "2026-11-07",
        "field": "Q",
        "tensor": {"kind": "matrix_mult", "format": [2, 2, 2],
                   "entry_convention": "dep/conventions.yaml#conv.mm_entry"},
        "computations": [
            {"kind": "ordinary_flattening", "grouping": "A | (B,C)",
             "matrix_shape": [nr, nc], "exact_rank": rk_flat,
             "derivation": "D1 in analysis/flattenings.py",
             "consequence": "R_Q(<2,2,2>) >= %d" % rk_flat},
            {"kind": "koszul_p1", "domain_dim": nrk, "codomain_dim": nck,
             "exact_rank": rk_kos, "derivation": "D2 in analysis/flattenings.py",
             "consequence": "R_Q(<2,2,2>) >= ceil(%d/3) = %d" % (rk_kos, koszul_bound)},
        ],
        "consequence": "R_Q(<2,2,2>) >= max(%d, %d) = %d" % (rk_flat, koszul_bound, max(rk_flat, koszul_bound)),
        "producer": {"module": "analysis/flattenings.py",
                     "arithmetic": "exact (fractions.Fraction)"},
        "verifier": {"tool": "tools/check_certs.py",
                     "independence": "independent re-implementation of both matrices and of the elimination"},
        "note": ("Koszul bound D2 is derived in-module only for p=1, dim A = 4; the "
                 "general normalization is out of scope (module docstring)."),
    }
    path = os.path.join(OUT, "222_Q_rank4.json")
    with open(path, "w") as fh:
        json.dump(cert, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote %s" % os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
