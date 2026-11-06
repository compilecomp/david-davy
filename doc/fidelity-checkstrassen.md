# Statement-Fidelity Map: CheckStrassen

## Abstract

This document is the fidelity mapping required by DEP&CC 2.0 Chapter 19.5 for the claim C-0016 (`machine-checked`). It maps each component of the prose statement onto the formal term in `lean/Omega/Certs/CheckStrassen.lean` and records the audit verdict per component.

## Formal Definitions

Claim C-0016, prose statement: the Strassen 7-term scheme, with the output assembly folded into the C-vectors, equals the 2x2 matrix multiplication tensor over the integers on all 64 index triples of the full 4x4x4 space.

## Mapping and audit

| Prose component | Formal term | Audit |
|---|---|---|
| "Strassen 7-term scheme" | the seven triples `(uS r, vS r, wS r)` for r in [0, 7) | matches; the product order M1..M7 is fixed in the file docstring and matches the certificate `certs/decompositions/222_Q_7.json` |
| "output assembly folded into the C-vectors" | `wS`, with c11 = M1+M4-M5+M7, c12 = M3+M5, c21 = M2+M4, c22 = M1-M2+M3+M6 | matches; the folding is the standard identification of the assembly coefficients with the C-vector entries; the same folding is used by the independent Python checker, which passes |
| "equals the 2x2 matrix multiplication tensor" | `mmTensor (α := Int)`, definition per `dep/conventions.yaml` conv.mm_entry | matches; conv.mm_entry fixes T[(i,j),(j2,k),(i2,k2)] = 1 iff i = i2 and j = j2 and k = k2 |
| "over the integers" | `Int` as the coefficient type | matches; `decide` evaluates integer arithmetic exactly |
| "on all 64 index triples of the full 4x4x4 space" | `witnessCheck` uses `checkUpTo` over counters 0..63 with the mixed-radix decode m = 32*i + 16*jx + 8*jy + 4*k + 2*iz + kz | matches; the decode is a bijection from [0, 64) onto {0,1}^6, so the Bool check is equivalent to the universally quantified statement at this fixed size; vanishing entries are included because the comparison is against `mmTensor` everywhere |
| "kernel-checked, zero admitted tokens" | `theorem strassen7_full_space : strassenFullCheck = true := by decide` | matches; the proof term is a `decide` proof, the axiom dump `dep/out/axioms_checkstrassen.txt` reports "does not depend on any axioms" |

Mandatory audit checks (Chapter 19.5): quantifier shape matches (bounded enumeration equals universal quantification at fixed size); no extra or missing hypotheses; definitions unfold to the intended objects (`Int` arithmetic, no `Nat` subtraction); degenerate entries are covered (the enumeration includes all 56 vanishing triples); the statement is not vacuous (the witness is the explicit term list); non-vacuity is witnessed formally by the theorem itself reducing to `true`.

## Known Limitations

The map covers the fixed 2x2x2 integer instance only. The general statement over arbitrary fields and sizes is gap G-0004; a new fidelity map is required when that layer lands.
