"""Exact bilinear-decomposition machinery over Q and F_p.

Annotation:
  ID: analysis.bilin
  CLASS: DEP-1
  WHAT: Constructs the matrix multiplication tensor <a,b,c> and the direct sum of
        such tensors over Q or F_p, and verifies exact decompositions into rank-1
        terms against them.
  WHY:  Producer-side arithmetic for every certificate in certs/decompositions/.
  STATUS: verified-numeric (self-tests in __main__)
  COMPLETE: complete
  HYP: none
  DEPENDS: [dep/conventions.yaml#conv.mm_entry, dep/conventions.yaml#conv.rank1_term]
  GAP: none
  OWNER: repo-maintainer
  EVIDENCE: python3 analysis/bilin.py exits 0 (self-tests below)

Conventions (dep/conventions.yaml):
  Index sets for <a,b,c>: A = [a]x[b], B = [b]x[c], C = [a]x[c], [k] = {0..k-1}.
  Entry: T[(i,j),(j2,k),(i2,k2)] = 1 iff j == j2 and i == i2 and k == k2.
  A rank-1 term is (u, v, w) with u: A -> F, v: B -> F, w: C -> F.
  Direct sum: block s uses index keys (s, local_index) in every factor; entries are
  nonzero only within a single block.
  Coefficients in certificates and in this module are integers. Over Q an integer n
  denotes itself; over F_p it denotes its residue class.
"""

from fractions import Fraction


class Field:
    """Exact field of coefficients. kind is 'Q' or 'Fp' (p prime)."""

    def __init__(self, kind, p=None):
        if kind not in ("Q", "Fp"):
            raise ValueError("kind must be 'Q' or 'Fp'")
        if kind == "Fp" and (p is None or p < 2):
            raise ValueError("Fp requires a prime p >= 2")
        self.kind, self.p = kind, p

    def zero(self):
        return Fraction(0) if self.kind == "Q" else 0

    def of_int(self, n):
        if not isinstance(n, int):
            raise TypeError("coefficients must be integers; got %r" % (n,))
        return Fraction(n) if self.kind == "Q" else n % self.p

    def name(self):
        return "Q" if self.kind == "Q" else "F_%d" % self.p


def mm_entry(a, b, c, pa, pb, pc):
    """Entry of <a,b,c> at (pa, pb, pc) with pa=(i,j), pb=(j2,k), pc=(i2,k2)."""
    (i, j), (j2, k), (i2, k2) = pa, pb, pc
    return 1 if (j == j2 and i == i2 and k == k2) else 0


def _all_indices(shapes):
    """ALL index triples of the full tensor space (Cartesian product of the three
    factor index sets per block), not only the support of the mm tensor. Equality
    of tensors is tested on the whole space; the vanishing entries carry information."""
    for s, (a1, b1, c1) in enumerate(shapes):
        A = [(s, (i, j)) for i in range(a1) for j in range(b1)]
        B = [(s, (j2, k)) for j2 in range(b1) for k in range(c1)]
        C = [(s, (i2, k2)) for i2 in range(a1) for k2 in range(c1)]
        for pa in A:
            for pb in B:
                for pc in C:
                    yield pa, pb, pc


def dense_tensor(field, shapes):
    """Dense dict {(pa,pb,pc): coeff} of the direct sum of blocks `shapes`."""
    out = {}
    for pa, pb, pc in _all_indices(shapes):
        sa, ia = pa
        sb, ib = pb
        sc, ic = pc
        if sa == sb == sc:
            val = mm_entry(*shapes[sa], ia, ib, ic)
        else:
            val = 0
        if val:
            out[(pa, pb, pc)] = field.of_int(val)
    return out


def term_tensor(field, shapes, u, v, w):
    """The rank-1 term (u, v, w) as a dense dict over the direct-sum space."""
    out = {}
    for key in _all_indices(shapes):
        val = u.get(key[0], 0) * v.get(key[1], 0) * w.get(key[2], 0)
        if val:
            out[key] = field.of_int(val)
    return out


def verify_decomposition(field, shapes, terms, dense_target):
    """Exact check that the terms sum to dense_target everywhere. Returns (ok, fails)."""
    acc = {}
    for u, v, w in terms:
        for key, val in term_tensor(field, shapes, u, v, w).items():
            acc[key] = acc.get(key, field.zero()) + val
    fails = []
    for key in set(acc) | set(dense_target):
        lhs = acc.get(key, field.zero())
        rhs = dense_target.get(key, field.zero())
        if field.kind == "Fp":
            eq = (lhs - rhs) % field.p == 0
        else:
            eq = lhs == rhs
        if not eq:
            fails.append((key, str(lhs), str(rhs)))
    return (not fails), fails


# ---------------------------------------------------------------------------
# The Strassen 7-term scheme, in sparse form. Defined over Z; valid over every
# ring by substitution (justification: algebra:ring). Block 0 of a direct-sum
# space; use lifted() to move it to another block.
#
# Annotation:
#   ID: analysis.strassen7
#   CLASS: DEP-0
#   WHAT: The 7-rank-1-term decomposition of <2,2,2>.
#   STATUS: verified-numeric (checked exactly by make_decomposition_certs.py)
#   COMPLETE: complete
#   DEPENDS: [C-0001]
#   GAP: none
#   OWNER: repo-maintainer
# ---------------------------------------------------------------------------

def _U(*kvs):
    return {(0, (i, j)): v for (i, j, v) in kvs}


def _V(*kvs):
    return {(0, (j, k)): v for (j, k, v) in kvs}


def _W(*kvs):
    return {(0, (i, k)): v for (i, k, v) in kvs}


def strassen_terms():
    """[(u, v, w)] for <2,2,2>, product order M1..M7:
      M1 = (a11+a22)(b11+b22);  M2 = (a21+a22)b11;  M3 = a11(b12-b22);
      M4 = a22(b21-b11);        M5 = (a11+a12)b22;  M6 = (a21-a11)(b11+b12);
      M7 = (a12-a22)(b21+b22).
    Output assembly c11 = M1+M4-M5+M7, c12 = M3+M5, c21 = M2+M4,
    c22 = M1-M2+M3+M6 is folded into the w vectors.
    """
    return [
        (_U((0, 0, 1), (1, 1, 1)), _V((0, 0, 1), (1, 1, 1)), _W((0, 0, 1), (1, 1, 1))),
        (_U((1, 0, 1), (1, 1, 1)), _V((0, 0, 1)),            _W((1, 0, 1), (1, 1, -1))),
        (_U((0, 0, 1)),            _V((0, 1, 1), (1, 1, -1)), _W((0, 1, 1), (1, 1, 1))),
        (_U((1, 1, 1)),            _V((1, 0, 1), (0, 0, -1)), _W((1, 0, 1), (0, 0, 1))),
        (_U((0, 0, 1), (0, 1, 1)), _V((1, 1, 1)),            _W((0, 1, 1), (0, 0, -1))),
        (_U((1, 0, 1), (0, 0, -1)), _V((0, 0, 1), (0, 1, 1)), _W((1, 1, 1))),
        (_U((0, 1, 1), (1, 1, -1)), _V((1, 0, 1), (1, 1, 1)), _W((0, 0, 1))),
    ]


def lifted(terms, block):
    """Re-index terms from block 0 into block `block` of a direct-sum space."""
    def lift(d):
        return {(block, k[1]): v for k, v in d.items()}
    return [(lift(u), lift(v), lift(w)) for (u, v, w) in terms]


def small122_terms(block):
    """The 4 rank-1 terms of <1,2,2> in block `block`: term (j,k) is
    u = e_j (row vector entry), v = e_(j,k), w = e_k."""
    out = []
    for j in range(2):
        for k in range(2):
            out.append((
                {(block, (0, j)): 1},
                {(block, (j, k)): 1},
                {(block, (0, k)): 1},
            ))
    return out


def sparse_to_json(d):
    """Sparse dict {(block,(i,j)): int} -> JSON list [[block, i, j, coeff]]."""
    return [[s, idx[0], idx[1], int(v)] for (s, idx), v in sorted(d.items())]


def json_to_sparse(lst):
    return {(s, (i, j)): v for (s, i, j, v) in lst}


if __name__ == "__main__":
    fq, f2, f3 = Field("Q"), Field("Fp", 2), Field("Fp", 3)
    assert len(dense_tensor(fq, [(2, 2, 2)])) == 8
    for f in (fq, f2, f3):
        ok, fails = verify_decomposition(f, [(2, 2, 2)], strassen_terms(),
                                         dense_tensor(f, [(2, 2, 2)]))
        assert ok, (f.name(), fails)
    ok, fails = verify_decomposition(fq, [(2, 2, 2), (2, 2, 2)],
                                     lifted(strassen_terms(), 0) + lifted(strassen_terms(), 1),
                                     dense_tensor(fq, [(2, 2, 2), (2, 2, 2)]))
    assert ok, fails
    ok, fails = verify_decomposition(fq, [(2, 2, 2), (1, 2, 2)],
                                     lifted(strassen_terms(), 0) + small122_terms(1),
                                     dense_tensor(fq, [(2, 2, 2), (1, 2, 2)]))
    assert ok, fails
    print("bilin self-tests: all passed")
