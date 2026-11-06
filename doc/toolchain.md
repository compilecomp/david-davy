# Toolchain

## Abstract

This document specifies the pinned toolchain of the repository, the local build procedures, and the CI gates. Inputs: the manifest `dep/toolchain.lock`. Outputs: verified certificates, lint reports, and the Lean build with its axiom dump.

## Formal Definitions

Pinned components (values in `dep/toolchain.lock`; deviations are defects):

| Component | Pin | Role |
|---|---|---|
| Python | 3.12.16 | certificate producers and checkers |
| z3-solver (pip) | 5.3.3 | search only; models re-verified exactly; trusted unsat is TCB entry G-0005 |
| mpmath | 1.3.0 | certified enclosures (`dep/numerics.yaml`) |
| Lean toolchain | `leanprover/lean4:v4.15.0` | machine-checked artifacts (`lean/lean-toolchain`) |
| Macaulay2 | not in CI | `cas/` scripts run locally; outputs committed with run records |

The Lean package builds against core Lean only (gap G-0006). Mathlib integration follows the standard procedure: add `require mathlib` to `lean/lakefile.toml` at a pinned commit, fetch the Mathlib cache with `lake exe cache get`, and re-run the fidelity audit for every cited theorem whose unfolding changed (DEP&CC 2.0 Chapter 19.7).

## Algorithm

Local verification, in order:

1. `python3 analysis/bilin.py` — producer self-tests.
2. `python3 analysis/make_decomposition_certs.py` — regenerate decomposition certificates (producer gate inside).
3. `python3 analysis/flattenings.py` — regenerate the flattening certificate.
4. `python3 analysis/sumineq.py` — regenerate the analysis certificates.
5. `python3 analysis/search_unsat.py` — regenerate the enumeration certificate.
6. `python3 search/enc.py --selftest` and, optionally, `--probe` (declared timeouts).
7. `python3 tools/check_certs.py` — independent re-verification of everything under `certs/`.
8. `python3 tools/ledger_lint.py` — cross-references, `CLAIMS.md` drift, `dep/out/` emission. Run twice after a ledger change; the first run repairs the generated view.
9. `python3 tools/dep_lint.py` — the rule subset of standards.md section 6.
10. `cd lean && lake build` — zero errors; the axiom dump lands in `dep/out/axioms_checkstrassen.txt`.

## Invariants

1. A commit that changes a claim status, a certificate, or `standards.md` re-runs steps 7 through 10 and commits all regenerated artifacts in the same commit (Documentation Style Guide section 5).
2. Solver runs declare timeouts; `unknown` is never reported as `unsat`.
3. The Lean build has zero errors and zero admitted tokens; the axiom dump of every cited theorem is archived.

## Integration Points

Depends on: `dep/toolchain.lock`, `lean/lean-toolchain`, `.github/workflows/ci.yml` (mirrors steps 7 through 10 plus the Lean build).

Depended on by: every producer script, `Makefile` targets `check`, `lint`, `lean`, `all`.

## Known Limitations

The CI Lean job builds the core-only package; a Mathlib build requires the cache workflow and is not configured at seed stage. Macaulay2 is absent from CI, so `cas/` outputs are run records, not CI gates. The z3 UNSAT trust (G-0005) is scheduled for replacement by a DRAT/LRAT export.
