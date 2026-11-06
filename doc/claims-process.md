# Claims Process

## Abstract

This document specifies the lifecycle of a ledger row in `dep/claims-ledger.yaml`: the closed status vocabulary, the transition rules, the evidence required at each status, and the mechanical checks applied in CI. Inputs: claims with evidence. Outputs: ledger rows, the generated view `CLAIMS.md`, and emitted artifacts under `dep/out/`.

## Formal Definitions

A row is a mapping with keys `id`, `statement`, `field`, `status`, `cert`, `checker`, `provenance`, `gaps`, `annotation`. The status set is closed (DEP&CC 2.0 Chapter 5.4): `machine-checked`, `proved`, `proved-modulo`, `conditional`, `verified-numeric`, `empirical`, `sketched`, `conjectural`, `heuristic`, `retracted`. The completeness status is closed (Chapter 5.5): `complete`, `partial`, `sketch`, `gap-declared`, `placeholder`, `retracted`.

The mapping from the RESEARCH_PLAN.md draft vocabulary is fixed and total:

| Draft | Closed set | Condition |
|---|---|---|
| `conjectured` | `conjectural` | always |
| `computed` | `empirical` | solver-trusted, no certificate |
| `computed` | `verified-numeric` | exact or certified check over a declared finite domain |
| `verified` | `verified-numeric` | certificate plus independent verifier |
| `verified` | `machine-checked` | kernel-verified, zero admitted tokens, axiom ledger extracted |
| `refuted` | `retracted` | plus counterexample row and blast-radius propagation |
| `published` | `proved-modulo` | before statement-fidelity audit; `proved` after |

## Algorithm

Lifecycle of a claim:

1. Register the row at status `conjectural` (or `sketched` with a gap) at the moment the question is adopted.
2. Produce evidence: a certificate under `certs/` in one of the formats of `doc/cert-format.md`, or a formal artifact under `lean/`.
3. Record the evidence: set `cert` and `checker`, set the status per the Appendix H decision procedure of DEP&CC 2.0, register any open gap in `dep/gaps.yaml` with blast radius and expiry.
4. Run `python3 tools/ledger_lint.py` and `python3 tools/dep_lint.py`; commit ledger, certificates, generated view, and emitted artifacts in one commit.
5. Upgrade status only with new evidence and a review record (DEP&CC 2.0 Chapter 5.4 transition rules). A `verified-numeric` claim never becomes `proved` without a proof; an `empirical` claim never becomes `proved` without a proof.

Ledger rule (standards.md section 3.3): no number enters `papers/` without a row whose status is at least `verified-numeric` and a certificate that re-checks in CI.

## Invariants

1. Statuses and completeness values are members of the closed sets; `dep_lint` enforces this.
2. A row with status `verified-numeric` or `machine-checked` has an existing `cert` and `checker`; enforced by rule `DEP-LINT-CLAIM-INFLATION`.
3. Every gap referenced by a row exists in `dep/gaps.yaml` and carries owner, ticket, blast radius, and expiry; expired open gaps fail the build.
4. `CLAIMS.md` equals its regeneration; drift fails `ledger_lint`.
5. A `complete` row depends, transitively, only on `complete` rows (status contamination rule).

## Integration Points

Depends on: `dep/claims-ledger.yaml`, `dep/gaps.yaml`, `dep/references.yaml`, certificates under `certs/`, formal artifacts under `lean/`.

Depended on by: `CLAIMS.md` (generated view), `dep/out/claims.json`, `dep/out/gaps.json`, `papers/` (every number cited in a paper must resolve to a row), `tools/dep_lint.py`.

## Known Limitations

The seed ledger imports literature results at `proved-modulo` with a single shared audit gap (G-0003); per-source audit records will replace it as `lit/` notes are written. The `retracted` path has no exercised instance yet; its blast-radius propagation is specified but untested.
