# Claims Ledger

GENERATED FILE. Source of truth: `dep/claims-ledger.yaml`.
Regenerate with `python3 tools/ledger_lint.py`; manual edits are
reverted (standards.md section 3.1, DEP&CC 2.0 Chapter 6.4).

Statuses are the closed set of DEP&CC 2.0 Chapter 5.4. The mapping
from the RESEARCH_PLAN.md draft vocabulary is fixed in standards.md
section 3.2. Justification tokens are from DEP&CC 2.0 Appendix F.

## Summary

| ID | Status | Field | Certificate | Statement |
|---|---|---|---|---|
| C-0001 | verified-numeric | Q | `certs/decompositions/222_Q_7.json` | R_Q(<2,2,2>) <= 7: there exist 7 triples (u_r, v_r, w_r) with u_r: Z^4-indexed integer vectors, sum_r u_r (x) v_r (x) w_r = <2,2,2> exact... |
| C-0002 | verified-numeric | F_2 | `certs/decompositions/222_F2_7.json` | R_F2(<2,2,2>) <= 7: the same 7-term decomposition, reduced modulo 2, is an exact decomposition over the field with 2 elements |
| C-0003 | verified-numeric | Q | `certs/flattenings/222_Q_rank4.json` | the (A tensor B) against C flattening of <2,2,2>_Q has exact rank 4 and the p=1 Koszul flattening has exact rank 16; by the in-module der... |
| C-0004 | proved-modulo | any | `certs/analysis/strassen_power_bound.json` | omega <= log_2(7) < 2.8073549221 |
| C-0005 | verified-numeric | Q | `certs/decompositions/222sum222_Q_14.json` | R_Q(<2,2,2> direct-sum <2,2,2>) <= 14: a 14-term exact decomposition of the direct-sum tensor (block-diagonal embedding) over Q |
| C-0006 | verified-numeric | Q | `certs/decompositions/222sum122_Q_11.json` | R_Q(<2,2,2> direct-sum <1,2,2>) <= 11: an 11-term exact decomposition over Q (7 terms from C-0001 plus 4 terms for <1,2,2>) |
| C-0007 | proved-modulo | any | `certs/analysis/sumineq_mixed.json` | if R_Q(<2,2,2> + <1,2,2>) <= 11 then omega <= 3 tau where 8^tau + 4^tau = 11; certified enclosure of 3 tau at 30 digits: [2.8585845396485... |
| C-0008 | proved-modulo | any | `certs/analysis/sumineq_uniform222.json` | if R_Q(2 copies of <2,2,2>) <= 14 then omega <= 3 tau where 2 * 8^tau = 14, giving omega <= log_2(7) < 2.8073549221; agrees with C-0004 t... |
| C-0009 | proved-modulo | any | `none` | for every field F: R_F(<2,2,2>) >= 7 |
| C-0010 | proved-modulo | any | `none` | for every field F: R_F(<3,3,3>) <= 23 |
| C-0011 | proved-modulo | any | `none` | omega < 2.371177 |
| C-0012 | proved-modulo | any | `none` | omega <= 2.371552 |
| C-0013 | proved-modulo | any | `none` | omega <= 2.371866, proved by Duan, Wu, Zhou (FOCS 2023) and stated as the prior record in ext:wxxz2023alpha |
| C-0014 | verified-numeric | F_2 | `certs/unsat/222_F2_rank_ge3.json` | R_F2(<2,2,2>) >= 3: no decomposition into at most 2 rank-1 terms exists over F_2, established by exhaustive enumeration of all 1 + 2^12 +... |
| C-0015 | empirical | F_2 | `none` | conditional on the z3 5.3.3 UNSAT answer under the declared timeout (G-0005, TCB): R_F2(<2,2,2>) >= 6, i.e. no decomposition into 5 rank-... |
| C-0016 | machine-checked | Z | `lean/Omega/Certs/CheckStrassen.lean` | kernel-checked (Lean 4 core, v4.15.0, zero admitted tokens, zero axioms): the Strassen 7-term scheme, with the output assembly folded int... |
| C-0018 | verified-numeric | F_2 | `certs/border/222_F2_border7_d2h1.json` | RBF2(<2,2,2>) <= 7 with a proper border witness: there are 7 triples of coefficient polynomials in F_2[eps]/(eps^2) with sum_r u_r v_r w_... |
| C-0017 | conjectural | any | `none` | Q(<2,2,2>) = 4 (research target T2 of RESEARCH_PLAN.md) |

## Rows

### C-0001

- **Statement.** R_Q(<2,2,2>) <= 7: there exist 7 triples (u_r, v_r, w_r) with u_r: Z^4-indexed integer vectors, sum_r u_r (x) v_r (x) w_r = <2,2,2> exactly over the rationals (in fact over Z)
- **Field.** Q
- **Claim status.** verified-numeric
- **Completeness.** complete
- **Certificate.** certs/decompositions/222_Q_7.json
- **Checker.** tools/check_certs.py
- **Provenance.** ext:strassen1969 (scheme); page-level pinpoint pending G-0003
- **Hypotheses.** none beyond the field axioms of Q
- **Depends on.** nothing
- **Gaps.** G-0003
- **Evidence.** computation:certified:222_Q_7.json checked by tools/check_certs.py (exact Fraction arithmetic) and independently by analysis/bilin.py
- **Owner.** repo-maintainer

### C-0002

- **Statement.** R_F2(<2,2,2>) <= 7: the same 7-term decomposition, reduced modulo 2, is an exact decomposition over the field with 2 elements
- **Field.** F_2
- **Claim status.** verified-numeric
- **Completeness.** complete
- **Certificate.** certs/decompositions/222_F2_7.json
- **Checker.** tools/check_certs.py
- **Provenance.** derived from C-0001 by reduction modulo 2 (justification: algebra:ring; the scheme is defined over Z and Z -> F_2 is a ring homomorphism)
- **Hypotheses.** none beyond the field axioms of F_2
- **Depends on.** C-0001
- **Gaps.** none
- **Evidence.** computation:certified:222_F2_7.json checked by tools/check_certs.py (exact GF(2) arithmetic)
- **Owner.** repo-maintainer

### C-0003

- **Statement.** the (A tensor B) against C flattening of <2,2,2>_Q has exact rank 4 and the p=1 Koszul flattening has exact rank 16; by the in-module derivations D1 and D2 of analysis/flattenings.py this yields R_Q(<2,2,2>) >= 4 and R_Q(<2,2,2>) >= 6
- **Field.** Q
- **Claim status.** verified-numeric
- **Completeness.** complete
- **Certificate.** certs/flattenings/222_Q_rank4.json
- **Checker.** tools/check_certs.py
- **Provenance.** flattening bound; general reference to be pinned and audited under G-0003 (candidate: Landsberg, Geometry and Complexity Theory)
- **Hypotheses.** flattening rank <= tensor rank (external standard fact, audit pending G-0003)
- **Depends on.** nothing
- **Gaps.** G-0003
- **Evidence.** computation:certified:222_Q_rank4.json; rank computed by exact Fraction Gaussian elimination in analysis/flattenings.py, re-derived by an independent elimination in tools/check_certs.py
- **Owner.** repo-maintainer

### C-0004

- **Statement.** omega <= log_2(7) < 2.8073549221
- **Field.** any
- **Claim status.** proved-modulo
- **Completeness.** gap-declared
- **Certificate.** certs/analysis/strassen_power_bound.json
- **Checker.** tools/check_certs.py
- **Provenance.** ext:strassen1969 for the base decomposition; tensor-power inference recorded under gap G-0001
- **Hypotheses.** H1: R(S tensor T) <= R(S) R(T); H2: omega = log_2 RA(<2,2,2>) with RA the asymptotic rank (both carried by G-0001)
- **Depends on.** C-0001
- **Gaps.** G-0001, G-0003
- **Evidence.** computation:certified:222_Q_7.json plus certified enclosure of log_2 7 (mpmath 60-bit working precision, outward rounding)
- **Owner.** repo-maintainer

### C-0005

- **Statement.** R_Q(<2,2,2> direct-sum <2,2,2>) <= 14: a 14-term exact decomposition of the direct-sum tensor (block-diagonal embedding) over Q
- **Field.** Q
- **Claim status.** verified-numeric
- **Completeness.** complete
- **Certificate.** certs/decompositions/222sum222_Q_14.json
- **Checker.** tools/check_certs.py
- **Provenance.** constructed by us, 2026-11-07, from C-0001 (justification: rule:substitution; the direct sum of two decompositions is a decomposition of the direct sum)
- **Hypotheses.** none
- **Depends on.** C-0001
- **Gaps.** none
- **Evidence.** computation:certified:222sum222_Q_14.json
- **Owner.** repo-maintainer

### C-0006

- **Statement.** R_Q(<2,2,2> direct-sum <1,2,2>) <= 11: an 11-term exact decomposition over Q (7 terms from C-0001 plus 4 terms for <1,2,2>)
- **Field.** Q
- **Claim status.** verified-numeric
- **Completeness.** complete
- **Certificate.** certs/decompositions/222sum122_Q_11.json
- **Checker.** tools/check_certs.py
- **Provenance.** constructed by us, 2026-11-07 (justification: rule:substitution)
- **Hypotheses.** none
- **Depends on.** C-0001
- **Gaps.** none
- **Evidence.** computation:certified:222sum122_Q_11.json
- **Owner.** repo-maintainer

### C-0007

- **Statement.** if R_Q(<2,2,2> + <1,2,2>) <= 11 then omega <= 3 tau where 8^tau + 4^tau = 11; certified enclosure of 3 tau at 30 digits: [2.858584539648584406977511276291, 2.858584539648584406977511276294], re-verified in CI at 80 digits
- **Field.** any
- **Claim status.** proved-modulo
- **Completeness.** gap-declared
- **Certificate.** certs/analysis/sumineq_mixed.json
- **Checker.** tools/check_certs.py
- **Provenance.** ext:alman2026speedup Theorem 1.1 (asymptotic sum inequality, attributing ext:schonhage1981); instance and enclosure computed by us, 2026-11-07
- **Hypotheses.** H1: the asymptotic sum inequality holds as stated in ext:alman2026speedup Theorem 1.1 (carried by G-0002); H2: the border-rank input R <= 11, carried by C-0006 at verified-numeric
- **Depends on.** C-0006
- **Gaps.** G-0002
- **Evidence.** computation:certified:sumineq_mixed.json; tau enclosure by mpmath bisection with outward rounding at declared precision
- **Owner.** repo-maintainer

### C-0008

- **Statement.** if R_Q(2 copies of <2,2,2>) <= 14 then omega <= 3 tau where 2 * 8^tau = 14, giving omega <= log_2(7) < 2.8073549221; agrees with C-0004 to the certified precision
- **Field.** any
- **Claim status.** proved-modulo
- **Completeness.** gap-declared
- **Certificate.** certs/analysis/sumineq_uniform222.json
- **Checker.** tools/check_certs.py
- **Provenance.** ext:alman2026speedup Theorem 1.1; instance constructed by us, 2026-11-07; cross-check against C-0004
- **Hypotheses.** as C-0007
- **Depends on.** C-0005, C-0004
- **Gaps.** G-0002
- **Evidence.** computation:certified:sumineq_uniform222.json
- **Owner.** repo-maintainer

### C-0009

- **Statement.** for every field F: R_F(<2,2,2>) >= 7
- **Field.** any
- **Claim status.** proved-modulo
- **Completeness.** gap-declared
- **Certificate.** none
- **Checker.** none
- **Provenance.** ext:alderstrassen1981 (lower bound for the total rank of the algebra of 2x2 matrices); audit pending G-0003
- **Hypotheses.** H1: the Alder-Strassen bound R >= 2 dim(A) - 1 for the multiplication tensor of a semisimple-free algebra, with hypotheses as in the source (audit pending G-0003)
- **Depends on.** nothing
- **Gaps.** G-0003
- **Evidence.** ext:alderstrassen1981
- **Owner.** repo-maintainer

### C-0010

- **Statement.** for every field F: R_F(<3,3,3>) <= 23
- **Field.** any
- **Claim status.** proved-modulo
- **Completeness.** gap-declared
- **Certificate.** none
- **Checker.** none
- **Provenance.** ext:laderman1976; the scheme is division-free (bilinear), hence valid over every commutative ring; audit and machine encoding of the 23 terms pending G-0003
- **Hypotheses.** H1: the published scheme is bilinear with integer coefficients (audit pending G-0003)
- **Depends on.** nothing
- **Gaps.** G-0003
- **Evidence.** ext:laderman1976
- **Owner.** repo-maintainer

### C-0011

- **Statement.** omega < 2.371177
- **Field.** any
- **Claim status.** proved-modulo
- **Completeness.** gap-declared
- **Certificate.** none
- **Checker.** none
- **Provenance.** ext:alman2025asymmetry (arXiv:2404.16349v3, abstract, SODA 2025), numerics of ext:dupont2026; audit pending G-0003
- **Hypotheses.** H1: correctness of the laser-method analysis and the numerical optimization in the source (audit pending G-0003)
- **Depends on.** nothing
- **Gaps.** G-0003
- **Evidence.** ext:alman2025asymmetry
- **Owner.** repo-maintainer

### C-0012

- **Statement.** omega <= 2.371552
- **Field.** any
- **Claim status.** proved-modulo
- **Completeness.** gap-declared
- **Certificate.** none
- **Checker.** none
- **Provenance.** ext:wxxz2023alpha (arXiv:2307.07970v2, abstract, SODA 2024); audit pending G-0003
- **Hypotheses.** as C-0011
- **Depends on.** nothing
- **Gaps.** G-0003
- **Evidence.** ext:wxxz2023alpha
- **Owner.** repo-maintainer

### C-0013

- **Statement.** omega <= 2.371866, proved by Duan, Wu, Zhou (FOCS 2023) and stated as the prior record in ext:wxxz2023alpha
- **Field.** any
- **Claim status.** proved-modulo
- **Completeness.** gap-declared
- **Certificate.** none
- **Checker.** none
- **Provenance.** ext:wxxz2023alpha abstract (prior-bound attribution); primary source ext:dwz2023 not yet read; audit pending G-0003
- **Hypotheses.** as C-0011
- **Depends on.** nothing
- **Gaps.** G-0003
- **Evidence.** ext:wxxz2023alpha (secondary); ext:dwz2023 (primary, unread)
- **Owner.** repo-maintainer

### C-0014

- **Statement.** R_F2(<2,2,2>) >= 3: no decomposition into at most 2 rank-1 terms exists over F_2, established by exhaustive enumeration of all 1 + 2^12 + 2^24 candidate decompositions (finite domain and packing justification declared in the cert)
- **Field.** F_2
- **Claim status.** verified-numeric
- **Completeness.** complete
- **Certificate.** certs/unsat/222_F2_rank_ge3.json
- **Checker.** tools/check_certs.py
- **Provenance.** computed by us, 2026-11-07, tools/search_unsat.py; corroboration: C-0003 gives the stronger bound 4 over Q, and ext:alderstrassen1981 gives 7 over every field
- **Hypotheses.** the enumeration covers every assignment of the declared variable set (declared in the cert, re-checked in CI by re-running the enumeration)
- **Depends on.** nothing
- **Gaps.** none
- **Evidence.** computation:certified:222_F2_rank_ge3.json; verifier re-runs the enumeration and compares counts
- **Owner.** repo-maintainer

### C-0015

- **Statement.** conditional on the z3 5.3.3 UNSAT answer under the declared timeout (G-0005, TCB): R_F2(<2,2,2>) >= 6, i.e. no decomposition into 5 rank-1 terms exists over F_2
- **Field.** F_2
- **Claim status.** empirical
- **Completeness.** partial
- **Certificate.** none
- **Checker.** search/enc.py
- **Provenance.** search by us, 2026-11-07, search/enc.py with z3 5.3.3, timeout declared in search/results/; DRAT certificate pending G-0005
- **Hypotheses.** H1: z3 5.3.3 unsat under timeout is correct (TCB, G-0005)
- **Depends on.** nothing
- **Gaps.** G-0005
- **Evidence.** search/results/probe_rank5_unsat.json (solver record with declared timeout)
- **Owner.** repo-maintainer

### C-0016

- **Statement.** kernel-checked (Lean 4 core, v4.15.0, zero admitted tokens, zero axioms): the Strassen 7-term scheme, with the output assembly folded into the C-vectors, equals the 2x2 matrix multiplication tensor over Z on all 64 index triples of the full 4x4x4 space (theorem strassen7_full_space)
- **Field.** Z
- **Claim status.** machine-checked
- **Completeness.** complete
- **Certificate.** lean/Omega/Certs/CheckStrassen.lean
- **Checker.** lean build (lake), pinned leanprover/lean4:v4.15.0; axiom dump dep/out/axioms_checkstrassen.txt
- **Provenance.** formalization by us, 2026-11-07, of the scheme of ext:strassen1969
- **Hypotheses.** none; the theorem is the literal 64-entry equality at the fixed 2x2x2 instance
- **Depends on.** C-0001
- **Gaps.** none
- **Evidence.** lean/Omega/Certs/CheckStrassen.lean; axiom dump dep/out/axioms_checkstrassen.txt (zero axioms); statement-fidelity map doc/fidelity-checkstrassen.md
- **Owner.** repo-maintainer

### C-0018

- **Statement.** RBF2(<2,2,2>) <= 7 with a proper border witness: there are 7 triples of coefficient polynomials in F_2[eps]/(eps^2) with sum_r u_r v_r w_r = eps^1 T + O(eps^2); the witness was found by z3 search and re-verified by exact arithmetic, and re-checks in CI
- **Field.** F_2
- **Claim status.** verified-numeric
- **Completeness.** complete
- **Certificate.** certs/border/222_F2_border7_d2h1.json
- **Checker.** tools/check_certs.py
- **Provenance.** found by us, run 2026-11-07, search/enc.py --probe; solver only generated the candidate, the evidence is the exactly re-verified model
- **Hypotheses.** none beyond the ring axioms of F_2[eps]/(eps^2)
- **Depends on.** C-0002
- **Gaps.** none
- **Evidence.** computation:certified:222_F2_border7_d2h1.json
- **Owner.** repo-maintainer

### C-0017

- **Statement.** Q(<2,2,2>) = 4 (research target T2 of RESEARCH_PLAN.md)
- **Field.** any
- **Claim status.** conjectural
- **Completeness.** placeholder
- **Certificate.** none
- **Checker.** none
- **Provenance.** RESEARCH_PLAN.md target T2
- **Hypotheses.** none
- **Depends on.** nothing
- **Gaps.** none
- **Evidence.** none
- **Owner.** repo-maintainer

## Gap register (view)

| Gap | Open | Expires | Downgrades | Target |
|---|---|---|---|---|
| G-0001 | 2026-11-07 | 2027-05-07 | C-0004->proved-modulo | Omega/Analysis/SumIneq.lean or Omega/Tensor/Basic.lean (Mathlib layer) |
| G-0002 | 2026-11-07 | 2027-05-07 | C-0007->proved-modulo, C-0008->proved-modulo | Omega/Analysis/SumIneq.lean |
| G-0003 | 2026-11-07 | 2027-05-07 | C-0009->proved-modulo, C-0010->proved-modulo, C-0011->proved-modulo, C-0012->proved-modulo, C-0013->proved-modulo | lit/ notes per source, then upgrade rows to proved |
| G-0004 | 2026-11-07 | 2027-05-07 | none | Mathlib layer: Fin-indexed tensors, tensor products, degeneration |
| G-0005 | 2026-11-07 | 2027-05-07 | C-0015->empirical | search/enc.py DRAT export; certs/unsat/ |
| G-0006 | 2026-11-07 | 2027-05-07 | none | lakefile require mathlib + lake exe cache get, then port drafts |
