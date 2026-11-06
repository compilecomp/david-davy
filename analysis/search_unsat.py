"""Exhaustive-enumeration refutation: R_F2(<2,2,2>) >= 3.

Annotation:
  ID: analysis.search_unsat
  CLASS: DEP-1
  WHAT: Enumerates every decomposition of <2,2,2> over F_2 into at most 2 rank-1
        terms (declared finite domain) and emits an omega.cert.unsat/1 certificate
        that none exists, hence R_F2(<2,2,2>) >= 3.
  WHY:  Tier 0 of the search trust ladder (enumeration before solver trust before
        proof logs); exercises the unsat certificate format without any solver in
        the trusted computing base.
  STATUS: verified-numeric
  COMPLETE: complete
  HYP: the enumeration covers all candidates (justified below and in the cert)
  DEPENDS: [C-0014]
  GAP: none
  OWNER: repo-maintainer
  EVIDENCE: python3 analysis/search_unsat.py exits 0; cert re-checked in CI by
            re-running the enumeration

Search-space justification (in-module, 2 IGUs):
  S1. The 64 entries of the ambient space (F_2)^4 (x) (F_2)^4 (x) (F_2)^4 are packed
      into one 64-bit word; tensor addition over F_2 is bitwise XOR on words
      (justification: algebra:ring; the packing is F_2-linear). All 64 entries are
      packed, so equality is tested on the whole space, not only on the support of
      the matrix multiplication tensor.
  S2. Every rank-1 term u (x) v (x) w with u, v, w in F_2^4 is one of the 2^12 = 4096
      triples enumerated in the term table; a decomposition into at most 2 terms has
      byte equal to the XOR of 0, 1, or 2 table entries. Enumerating those XORs is
      therefore an exhaustive enumeration of all decompositions with at most 2 terms.
  Conclusion: if the target byte is not obtained, no decomposition into at most 2
  terms exists, so R_F2(<2,2,2>) >= 3 over F_2.
"""

import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "certs", "unsat")

N = 4  # each factor of <2,2,2> has 2*2 = 4 entries


def entry_index(pa, pb, pc):
    """Bit index of the full 4x4x4 tensor space: A-index (i,j) -> i*2+j etc.
    All 64 entries are packed; a valid decomposition must match the target on all
    of them, including the 56 entries where the mm tensor vanishes."""
    (i, j), (j2, k), (i2, k2) = pa, pb, pc
    a_i = i * 2 + j
    b_i = j2 * 2 + k
    c_i = i2 * 2 + k2
    return (a_i * 4 + b_i) * 4 + c_i


def target_word():
    """64-bit packing of <2,2,2> over F_2 in the full index space."""
    w = 0
    for i in range(2):
        for j in range(2):
            for k in range(2):
                w |= 1 << entry_index((i, j), (j, k), (i, k))
    return w


def term_word(u, v, w):
    """64-bit packing of the rank-1 term (u, v, w) in the full index space."""
    out = 0
    for ia in range(4):
        if not u[ia]:
            continue
        i, j = ia // 2, ia % 2
        for ib in range(4):
            if not v[ib]:
                continue
            j2, k = ib // 2, ib % 2
            base = (ia * 4 + ib) * 4
            for ic in range(4):
                if w[ic]:
                    out |= 1 << (base + ic)
    return out


def main():
    t0 = time.time()
    tgt = target_word()
    # Term table over all 2^12 triples (u, v, w).
    table = []
    for ux in range(1 << N):
        u = [(ux >> b) & 1 for b in range(N)]
        for vx in range(1 << N):
            v = [(vx >> b) & 1 for b in range(N)]
            for wx in range(1 << N):
                w = [(wx >> b) & 1 for b in range(N)]
                table.append(term_word(u, v, w))
    assert len(table) == 4096
    # All sums of 0, 1, 2 terms.
    achievable = {0}
    achievable.update(table)
    pairs = set()
    for b1 in table:
        for b2 in table:
            pairs.add(b1 ^ b2)
    achievable |= pairs
    hit = tgt in achievable
    assert not hit, "a decomposition into at most 2 terms was found; claim C-0014 fails"
    runtime = time.time() - t0
    cert = {
        "schema": "omega.cert.unsat/1",
        "claim_id": "C-0014",
        "created": "2026-11-07",
        "kind": "exhaustive_enumeration",
        "field": "F_2",
        "tensor": {"kind": "matrix_mult", "format": [2, 2, 2],
                   "entry_convention": "dep/conventions.yaml#conv.mm_entry",
                   "packing": "64-bit word over the full 4x4x4 index space; bit "
                              "((ia*4 + ib)*4 + ic) = entry with A-index ia, B-index ib, "
                              "C-index ic; all 64 entries are packed, so a candidate must "
                              "match the target everywhere including the 56 vanishing "
                              "entries"},
        "search_space": {
            "terms_max": 2,
            "term_parameterization": "u, v, w in F_2^4 (all 2^12 triples tabulated)",
            "assignments_reduced": "1 (empty) + 4096 (one term) + 4096^2 (two terms, as XOR pairs)",
            "justification": "S1, S2 in analysis/search_unsat.py module docstring",
        },
        "result": {"target_byte": tgt, "achieved_byte_count": len(achievable),
                   "target_achieved": False},
        "conclusion": "R_F2(<2,2,2>) >= 3",
        "runtime_seconds": round(runtime, 3),
        "producer": {"module": "analysis/search_unsat.py", "arithmetic": "exact (booleans)"},
        "verifier": {"tool": "tools/check_certs.py",
                     "independence": "re-runs the enumeration from the cert parameters "
                                     "with its own packing and compares"},
        "note": ("Corroborated from above by certs/flattenings/222_Q_rank4.json (rank >= 4 "
                 "over Q, and the same flattening matrix over F_2) and by C-0009 "
                 "(rank >= 7 over every field, literature). This cert exists to validate "
                 "the unsat format, not to advance the record."),
    }
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "222_F2_rank_ge3.json")
    with open(path, "w") as fh:
        json.dump(cert, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("wrote %s (enumerated %d candidates in %.2fs)"
          % (os.path.relpath(path, ROOT), 1 + len(table) + len(table) ** 2, runtime))


if __name__ == "__main__":
    main()
