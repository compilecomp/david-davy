# Certificate Formats

## Abstract

This document specifies the JSON schemas of the five certificate kinds stored under `certs/`, the arithmetic classes admitted inside them, and the verification contract between producers and checkers. Inputs: certificates produced by `analysis/` and `search/`. Outputs: boolean verification verdicts with diagnostic messages, emitted by `tools/check_certs.py`.

## Formal Definitions

A certificate is a JSON object with a mandatory string field `schema` from the set:

| `schema` | Meaning | Producer | Checker entry |
|---|---|---|---|
| `omega.cert.decomposition/1` | exact rank witness: finite list of rank-1 terms | `analysis/make_decomposition_certs.py` | `check_decomposition` |
| `omega.cert.border/1` | border-rank witness over a truncated polynomial ring | `search/enc.py` | `check_border` |
| `omega.cert.analysis/1` | exponent bound: derivation chain plus certified enclosure | `analysis/sumineq.py` | `check_analysis` |
| `omega.cert.flattening/1` | flattening and Koszul-flattening rank certificates | `analysis/flattenings.py` | `check_flattening` |
| `omega.cert.unsat/1` | refutation evidence over a declared finite domain | `analysis/search_unsat.py` | `check_unsat` |

Common fields, all mandatory: `schema` (string), `claim_id` (ledger row identifier, must resolve in `dep/claims-ledger.yaml`), `created` (ISO date), `field` (`Q`, or `F_q` with q a prime power that the checker supports), `tensor` (object with `kind` and either `format` or `blocks`), `producer` (object naming the producing module and the arithmetic class), `verifier` (object naming the checking tool and asserting producer/checker independence).

Domain-specific fields:

1. `omega.cert.decomposition/1`: `invariant` (`rank`), `bound` (positive integer), `terms` (list of objects `u`, `v`, `w`, each a list of quadruples `[block, i, j, coefficient]` with integer coefficient).
2. `omega.cert.border/1`: `ring` (object with `name` and `d`), `order_h` (the shift h of the witness), `bound` (term count), `terms` (list of objects with `u`, `v`, `w`, each a list over indices and epsilon levels of integer bits).
3. `omega.cert.analysis/1`: `kind` (`tensor_power_bound` or `asymptotic_sum_inequality`), `bound` (object with `symbolic` string and decimal `enclosure_lo`, `enclosure_hi` with a declared digit count), for the inequality kind also `instance` (shapes, products, border-rank input with evidence path) and `tau_enclosure`.
4. `omega.cert.flattening/1`: `computations` (list of objects with `kind`, matrix shape, `exact_rank`, `derivation`, `consequence`).
5. `omega.cert.unsat/1`: `kind` (`exhaustive_enumeration`), `search_space` (declared variable set, candidate count, and the justification of the enumeration), `result`, `conclusion`.

Arithmetic classes (DEP&CC 2.0 Chapter 18.1): coefficients are integers, interpreted over the rationals or reduced modulo the field characteristic; enclosures are decimal strings with declared digit count and outward rounding. Class `floating` is banned inside `certs/`.

## Algorithm

`tools/check_certs.py` proceeds per certificate:

1. Load the ledger; collect valid claim identifiers.
2. Dispatch on `schema` to a checker function.
3. Reconstruct the target tensor from the declared convention (`dep/conventions.yaml`, `conv.mm_entry`) over the full index space, including vanishing entries.
4. Re-derive the claimed quantity with code that shares nothing with the producer.
5. Cross-check `claim_id`, referenced evidence files, and, for enclosures, recompute at higher precision and require containment.
6. Exit nonzero if any check fails.

## Invariants

1. Every certificate equals its target exactly on the full index space, not only on the support of the target tensor.
2. Every enclosure edge, rounded outward, retains the sign conditions asserted by the claim when recomputed at higher precision.
3. Every `claim_id` resolves; every referenced evidence file exists and has the declared schema.
4. No checker imports producer code (independence, standards.md section 5.3).

## Integration Points

Depends on: `dep/claims-ledger.yaml` (identifier resolution), `dep/conventions.yaml` (tensor entry convention), `dep/toolchain.lock` (mpmath version for enclosures).

Depended on by: `.github/workflows/ci.yml` (gate), `Makefile` target `check`, `tools/dep_lint.py` rule `DEP-LINT-CLAIM-INFLATION` (file existence; verification is delegated here).

Signatures: `python3 tools/check_certs.py` exits 0 with a per-certificate report, or exits 1 listing failures.

## Known Limitations

The border checker is wired for `F_2[eps]/(eps^2)` and a single `<2,2,2>` block with h in {0, 1}. The analysis checker supports the two kinds listed. Fields beyond Q, F_2, and F_3 require extending `coeff`. Refutation certificates from SAT solvers (DRAT/LRAT formats) are not yet accepted; until that pipeline exists, solver-derived lower bounds stay at status `empirical` (gap G-0005).
