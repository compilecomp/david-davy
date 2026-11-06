# Repository Engineering Standard

## Abstract

This document declares the conformance profile of the `omega` repository against DEP&CC 2.0 (`standard.md`) and the Documentation Style Guide (`doc standard.md`), both canonical at the repository root as published upstream. It fixes the claims-ledger schema, the certificate requirements, the enforcement tooling, and the security policy of this repository. It is normative for every file under version control.

## 1. Governing documents

Authority order, highest first:

1. `standard.md` (DEP&CC 2.0, normative draft standard, upstream file of `compilecomp/david-davy`, present at root since its creation; Apache-2.0).
2. `doc standard.md` (Documentation Style Guide, same source).
3. This file (repository-specific rules; may only tighten, never relax, items 1 and 2).
4. `dep/conventions.yaml`, `dep/symbols.yaml` (registry files; mechanics in section 4).

## 2. Conformance profile

**DEP&CC 2.0 Profile: Core** is in force (DEP&CC 2.0, Appendix J). Core comprises, without exception:

1. Laws 1-14 of DEP&CC 2.0 Chapter 4.
2. Annotation blocks with fields `STATUS`, `COMPLETE`, `HYP`, `DEPENDS`, `GAP` on every DEP-0 and DEP-1 node (DEP&CC 2.0 Chapter 32.2, reduced field set).
3. Symbol registry (`dep/symbols.yaml`) and convention manifest (`dep/conventions.yaml`).
4. Hypothesis discharge and acyclicity of the dependency graph.
5. Interchange ledger; at seed stage this repository declares the ledger empty and records the two limiting operations it must never perform silently (section 5.6).
6. Zero claim inflation.
7. Zero admitted tokens (`sorry`, `admit`, `native_decide`, `axiom`, `postulate`) in any artifact backing a `machine-checked` claim.
8. Banned-phrase list of DEP&CC 2.0 Appendix A.
9. `tools/dep_lint.py` at zero Severity 0 findings.

Dated full-conformance plan (Core is not a permanent resting place, DEP&CC 2.0 Appendix J):

| Milestone | Scope | Target |
|---|---|---|
| F1 | Full annotation blocks (all fields of Chapter 32.2) on all DEP-0 nodes | with first paper draft |
| F2 | Statement-fidelity audit for every `machine-checked` claim (Chapter 19.5) | with `papers/01-spectrum-lean` |
| F3 | Degeneracy battery per DEP-0 node (Chapter 30.3) | with `papers/02-laser-optimization` |
| F4 | Machine-extracted axiom ledgers archived per build (Chapter 19.2) | when Lean CI is green on Mathlib |
| F5 | Readability metrics measured and reported (Chapter 21) | with first paper draft |
| F6 | `dep_lint` rule coverage per Chapter 33.2 raised from the subset in section 6 to the full catalog | within 6 months of repo creation |

## 3. Claims ledger

### 3.1 Single source

The machine-readable ledger is `dep/claims-ledger.yaml`. `CLAIMS.md` is a generated view produced by `tools/gen_claims_md.py`. Manual edits to `CLAIMS.md` are reverted in review (DEP&CC 2.0 Chapter 6.4 bans manual editing of generated files). CI regenerates `CLAIMS.md` and fails on drift.

### 3.2 Status vocabulary

The claim status of a ledger row is exactly one value from DEP&CC 2.0 Chapter 5.4 (closed set): `machine-checked`, `proved`, `proved-modulo`, `conditional`, `verified-numeric`, `empirical`, `sketched`, `conjectural`, `heuristic`, `retracted`. No other value is permitted. `dep_lint` enforces this.

The research program (RESEARCH_PLAN.md) used a draft vocabulary. The mapping into the closed set is fixed:

| Program draft value | Closed-set value | Condition |
|---|---|---|
| `conjectured` | `conjectural` | always |
| `computed` | `empirical` | solver output trusted, no certificate (e.g. SMT `unsat` without proof log) |
| `computed` | `verified-numeric` | exact or certified check over a declared finite domain |
| `verified` | `verified-numeric` | certificate + independent verifier, finite domain declared |
| `verified` | `machine-checked` | kernel-verified in a pinned proof assistant, zero admitted tokens, axiom ledger extracted |
| `refuted` | `retracted` + counterexample node | always, with blast-radius propagation |
| `published` | `proved-modulo` | literature result imported before the statement-fidelity audit of DEP&CC 2.0 Chapter 19.5 is performed |

A `published` row upgrades to `proved` only after the fidelity audit against the pinned source is recorded.

### 3.3 Row schema

Every row of `dep/claims-ledger.yaml` carries: `id`, `statement` (self-contained, quantifiers explicit), `field`, `status` (closed set), `cert` (path or `none`), `checker` (path or `none`), `provenance` (pinpoint: identifier plus locator, per Law 9), `annotation` (ID, CLASS, WHAT, STATUS, COMPLETE, HYP, DEPENDS, GAP, OWNER, EVIDENCE), `gaps` (list of gap IDs from `dep/gaps.yaml` or empty).

The ledger rule of RESEARCH_PLAN.md holds in the tightened form: no number enters `papers/` unless a ledger row exists whose status is at least `verified-numeric`, with a certificate that re-checks in CI. Rows that cannot produce the certificate carry status `conjectural` or `empirical`, never `verified-numeric`.

## 4. Registries

`dep/conventions.yaml` fixes every convention key with an explicit value. `dep/symbols.yaml` registers every symbol used in DEP-0 regions with sort, meaning, scope, and declaration site. A symbol absent from the registry must not appear in a DEP-0 region (Law 3). Overloads require an entry in `dep/symbols.yaml` with a mechanically applicable disambiguation rule.

## 5. Certificates

### 5.1 Formats

Certificates live under `certs/` and are JSON documents with a `schema` tag:

| Tag | Directory | Content |
|---|---|---|
| `omega.cert.decomposition/1` | `certs/decompositions/` | rank witness: list of rank-1 terms over a declared field |
| `omega.cert.border/1` | `certs/border/` | border-rank witness over a truncated polynomial ring |
| `omega.cert.analysis/1` | `certs/analysis/` | exponent bounds: derivation chain, symbolic bound, certified numeric enclosure |
| `omega.cert.flattening/1` | `certs/flattenings/` | flattening or Koszul-flattening rank certificate |
| `omega.cert.unsat/1` | `certs/unsat/` | refutation evidence (DRAT/LRAT or enumerated exhaustive check) |

Schemas are specified in `doc/cert-format.md`.

### 5.2 Arithmetic classes

Every numeric element of a certificate is classified per DEP&CC 2.0 Chapter 18.1. Certificates admit classes `exact` and `certified` only. Class `floating` is banned inside `certs/`. Enclosures must state method, precision, rounding direction, and failure policy (`dep/numerics.yaml`).

### 5.3 Producer and checker independence

For every certificate, the checker under `tools/` or `analysis/` must be a re-implementation that does not import the producer code path. At seed stage the pair is: `analysis/` (producer) and `tools/check_certs.py` (checker). Lean checkers under `lean/Omega/Certs/` are a third path where present.

### 5.4 Solver trust

SMT/SAT solver output is governed by DEP&CC 2.0 Chapter 19.8: declared finite timeout per invocation; `unknown` and timeout are not `unsat`; solver version pinned in `dep/toolchain.lock`; a trusted `unsat` is a TCB entry in `dep/gaps.yaml`-linked toolchain notes. A satisfying model is evidence only after exact re-verification by repository code. Search results without certificates stay under `search/results/` and enter the ledger at status `empirical` at most.

## 6. Enforcement

`tools/dep_lint.py` implements the following DEP&CC 2.0 Chapter 33.2 rule subset; rule IDs match the catalog:

- `DEP-LINT-STATUS-VALUE`: ledger statuses in the closed set.
- `DEP-LINT-STATUS-CONTAMINATION`: no `complete` node depends on a node with completeness status other than `complete` (over the declared dependency edges of the ledger and gap register).
- `DEP-LINT-ADMITTED`: banned tokens in Lean artifacts backing `machine-checked` claims.
- `DEP-LINT-BANNED-PHRASE`: Appendix A phrases in repository markdown and Lean comments (the restricted set that is unconditional: justification-masking and marketing classes).
- `DEP-LINT-GAP-EXPIRY`: gaps in `dep/gaps.yaml` with `expires` in the past and status `open`.
- `DEP-LINT-CLAIM-INFLATION`: every certificate referenced by a row exists, re-checks, and the row status does not exceed the evidence class.
- `DEP-LINT-ORPHAN`: every certificate directory referenced in this standard is non-empty or carries an explicit `EMPTY.md` declaration.

`tools/check_certs.py` re-verifies every certificate. `tools/ledger_lint.py` regenerates `CLAIMS.md`, checks drift, cross-references rows, certificates, and gaps. CI (`.github/workflows/ci.yml`) runs all three and the Lean build. Severity 0 findings fail the build.

## 7. Security

Credentials, tokens, and keys are banned from the repository in any form, including history. `.gitignore` blocks common credential file names. A credential exposed outside the credential store is treated as compromised and must be rotated; it must not be committed, echoed into logs, or embedded in scripts. Remotes authenticate through the local user's credential helper; the repository carries no remote URLs with embedded userinfo.

## 8. Documentation structure

Documents under `doc/` follow the exact structure of `doc standard.md` section 3: Title, Abstract, Formal Definitions, Algorithm, Invariants, Integration Points, Known Limitations. The guide's Rust-specific examples are adapted: artifact signatures are given in the language of the component (Python, Lean, JSON Schema). The guide's prose rules (objectivity, precision, conciseness, completeness; no hype, no AI idioms, no emojis, exclamation marks, or nested bullets deeper than two levels) apply to every document in this repository.

## 9. Change process

A commit that changes a claim status, a certificate, or a normative section of this file must, in the same commit: update `dep/claims-ledger.yaml` or the certificate, re-run the checkers, and update the gap register if a gap opens or closes (Documentation Style Guide section 5, co-location rule).
