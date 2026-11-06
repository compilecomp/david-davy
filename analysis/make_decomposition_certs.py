"""Generates the decomposition certificates under certs/decompositions/.

Annotation:
  ID: analysis.make_decomposition_certs
  CLASS: DEP-1
  WHAT: Producer for certs 222_Q_7, 222_F2_7, 222sum222_Q_14, 222sum122_Q_11.
  WHY:  Machine-written certificates avoid transcription errors; each file is
        verified by the producer gate below and re-verified by tools/check_certs.py.
  STATUS: verified-numeric
  COMPLETE: complete
  DEPENDS: [C-0001, C-0002, C-0005, C-0006]
  GAP: none
  OWNER: repo-maintainer
  EVIDENCE: run log in certs/decompositions/PRODUCER_LOG.md
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bilin import (Field, dense_tensor, sparse_to_json, strassen_terms,
                   lifted, small122_terms, verify_decomposition)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "certs", "decompositions")

CERTS = [
    {
        "name": "222_Q_7.json",
        "claim_id": "C-0001",
        "field": "Q",
        "blocks": [[2, 2, 2]],
        "terms": strassen_terms(),
        "bound": 7,
        "invariant": "rank",
        "note": ("Strassen scheme defined over Z; over Q the integer coefficients "
                 "denote themselves. Signs of the output assembly are folded into w."),
    },
    {
        "name": "222_F2_7.json",
        "claim_id": "C-0002",
        "field": "F_2",
        "blocks": [[2, 2, 2]],
        "terms": strassen_terms(),
        "bound": 7,
        "invariant": "rank",
        "note": ("Same scheme reduced modulo 2: Z -> F_2 is a ring homomorphism, so the "
                 "identity over Z implies the identity over F_2 (justification: algebra:ring). "
                 "The producer and the checker both re-verify over F_2 directly."),
    },
    {
        "name": "222sum222_Q_14.json",
        "claim_id": "C-0005",
        "field": "Q",
        "blocks": [[2, 2, 2], [2, 2, 2]],
        "terms": lifted(strassen_terms(), 0) + lifted(strassen_terms(), 1),
        "bound": 14,
        "invariant": "rank",
        "note": "Block-diagonal direct sum of two copies of C-0001.",
    },
    {
        "name": "222sum122_Q_11.json",
        "claim_id": "C-0006",
        "field": "Q",
        "blocks": [[2, 2, 2], [1, 2, 2]],
        "terms": lifted(strassen_terms(), 0) + small122_terms(1),
        "bound": 11,
        "invariant": "rank",
        "note": ("Direct sum of C-0001 with the 4-term decomposition of <1,2,2>; "
                 "rank of <1,2,2> equals 4 by the identity flattening (see "
                 "certs/flattenings/222_Q_rank4.json for the method at 2x2x2)."),
    },
]


def to_json_terms(terms):
    return [
        {"u": sparse_to_json(u), "v": sparse_to_json(v), "w": sparse_to_json(w)}
        for (u, v, w) in terms
    ]


def main():
    os.makedirs(OUT, exist_ok=True)
    written = []
    for spec in CERTS:
        field = Field("Q") if spec["field"] == "Q" else Field("Fp", 2)
        shapes = [tuple(b) for b in spec["blocks"]]
        # Producer gate: exact verification before anything is written.
        ok, fails = verify_decomposition(field, shapes, spec["terms"],
                                         dense_tensor(field, shapes))
        if not ok:
            raise SystemExit("producer gate FAILED for %s: %r" % (spec["claim_id"], fails[:3]))
        cert = {
            "schema": "omega.cert.decomposition/1",
            "claim_id": spec["claim_id"],
            "created": "2026-11-07",
            "field": spec["field"],
            "tensor": {"kind": "direct_sum_of_matrix_mult",
                       "blocks": spec["blocks"],
                       "entry_convention": "dep/conventions.yaml#conv.mm_entry"},
            "invariant": spec["invariant"],
            "bound": spec["bound"],
            "terms": to_json_terms(spec["terms"]),
            "producer": {
                "module": "analysis/bilin.py + analysis/make_decomposition_certs.py",
                "arithmetic": "exact (fractions.Fraction over Q, residues over F_p)",
            },
            "verifier": {
                "tool": "tools/check_certs.py",
                "independence": ("independent re-implementation; does not import "
                                 "analysis/ (standards.md section 5.3)"),
            },
            "note": spec["note"],
        }
        path = os.path.join(OUT, spec["name"])
        with open(path, "w") as fh:
            json.dump(cert, fh, indent=2, sort_keys=True)
            fh.write("\n")
        written.append((path, len(spec["terms"]), spec["field"]))
    for path, n, field in written:
        print("wrote %s (%d terms over %s)" % (os.path.relpath(path, ROOT), n, field))


if __name__ == "__main__":
    main()
