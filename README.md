# omega

Formal methods for the matrix multiplication exponent: a repository where every number is a ledger row, every ledger row has evidence, and every piece of evidence re-checks in CI.

North star (RESEARCH_PLAN.md): develop a formalized algebraic framework using SMT, ITP, and ATP tooling to either prove ω = 2 or establish new barriers, with machine-checked certificates for all claims. The constraint that shapes the program is the irreversibility barrier of Christandl, Vrana, and Zuiddam: ω = 2 requires a family of tensors with irreversibility tending to 1, or a method outside the restriction and degeneration framework.

## Governing standards

This repository conforms to **DEP&CC 2.0 Profile: Core** (`standard.md`, canonical at the repository root, upstream from `compilecomp/david-davy`) and to the Documentation Style Guide (`doc standard.md`). The adoption declaration, the claims-ledger schema, the certificate contract, and the security policy are in `standards.md`. `doc/` holds the component documentation.

Claim statuses are the closed set of DEP&CC 2.0 Chapter 5.4; the research program's draft vocabulary maps onto it as fixed in standards.md section 3.2.

## Current certified inventory (2026-11-07)

| Result | Row | Status |
|---|---|---|
| R_Q(⟨2,2,2⟩) ≤ 7, R_F2(⟨2,2,2⟩) ≤ 7 (exact witnesses) | C-0001, C-0002 | verified-numeric |
| Kernel-checked Strassen theorem over Z, full 64-entry space, zero axioms | C-0016 | machine-checked |
| Flattening rank 4 and Koszul p=1 rank 16, giving R_Q(⟨2,2,2⟩) ≥ 4 and ≥ 6 | C-0003 | verified-numeric |
| ω ≤ log_2(7) with certified enclosure | C-0004 | proved-modulo (G-0001) |
| Asymptotic sum inequality instances with certified τ enclosures | C-0007, C-0008 | proved-modulo (G-0002) |
| R_F2(⟨2,2,2⟩) ≥ 3 by exhaustive enumeration | C-0014 | verified-numeric |
| Proper border witness over F_2[ε]/(ε²), 7 terms, order h = 1 | C-0018 | verified-numeric |
| R_F2(⟨2,2,2⟩) ≥ 6 (z3, solver-trusted) | C-0015 | empirical (G-0005) |
| Literature imports (Alder–Strassen, Laderman, exponent record ω < 2.371177) | C-0009..C-0013 | proved-modulo (G-0003) |

The authoritative inventory is `CLAIMS.md` (generated view of `dep/claims-ledger.yaml`).

## Repository layout

```
standards.md          adoption manifest (DEP&CC 2.0 Profile: Core)
standards/            vendored normative documents
dep/                  registries: toolchain.lock, conventions, symbols, gaps,
                      numerics, references, claims-ledger; out/ = emitted artifacts
CLAIMS.md             generated ledger view (edit dep/claims-ledger.yaml instead)
certs/                machine-checkable evidence: decompositions, border, unsat,
                      analysis, flattenings
lean/                 Lean 4 package, core-only profile (gap G-0006);
                      Omega/Certs/CheckStrassen.lean is the anchor theorem
analysis/             exact-arithmetic producers for certificates
search/               z3 encodings and run records (WS2)
cas/                  Macaulay2 scripts (WS4), local runs
papers/               00-landscape plus four scoped directories
lit/                  reading list with verification state; notes per source
doc/                  component documentation (cert format, claims process,
                      toolchain, fidelity map)
tools/                check_certs.py, dep_lint.py, ledger_lint.py
```

## Quickstart

```
pip install -r requirements.txt
make all          # producers, independent checker, ledger, dep_lint, lean build
```

Individual gates: `make check` (certificates), `make ledger` (cross-references and generated-view drift), `make lint` (dep_lint rule subset), `make lean` (pinned toolchain build plus axiom dump), `make search` (z3 selftest with declared timeouts).

CI (`.github/workflows/ci.yml`) runs the same gates on every push: certificate regeneration must be committed (drift fails the build).

## Entry points by workstream

1. WS1 (Tier A, laser-method optimization): `analysis/sumineq.py`, `papers/02-laser-optimization/README.md`. Entry ticket: reproduce a published exponent to 4 decimals.
2. WS2 (Tier B, border rank over F_2[ε]): `search/enc.py --probe`, `search/README.md`.
3. WS3 (Tier B', symmetry): not started; output format decision in `papers/03-structured-search/README.md`.
4. WS4 (Tier C, flattenings): `analysis/flattenings.py`, `cas/flattenings.m2`.
5. WS5 (Tier D/E, spectrum and barriers): `lean/Omega/Spectrum/`, `lean/Omega/Barriers/` (placeholders).

## Security

No credentials, tokens, or keys are accepted in this repository in any form, including history; see standards.md section 7. Remotes authenticate through the local user's credential helper.
