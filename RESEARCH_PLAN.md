# RESEARCH_PLAN.md

IMPORTED PROGRAM DOCUMENT, 2026-11-07. This is the founding program of the repository, committed verbatim. It predates the adoption of DEP&CC 2.0; where its draft vocabulary conflicts with `standards.md`, the standard governs (status mapping: standards.md section 3.2). The banned-phrase rules of DEP&CC 2.0 Appendix A are not retroactively applied to this document; findings against it are Severity 3 (see `tools/dep_lint.py` header).

---

# Research Program: Formal Methods for Matrix Multiplication Complexity

## Goal

**Develop a formalized algebraic framework using SMT/ITP/ATP to either prove ω = 2 or establish new barriers, with machine-checked certificates for all claims.**

### Precise Targets

Three equivalent formulations of ω = 2:

**T1 (Constructive):** Find a family of decompositions with $\underline{R}(\langle n,n,n\rangle) = n^{2+o(1)}$

**T2 (Asymptotic subrank):** Prove $Q(\langle 2,2,2\rangle) = 4$

**T3 (Spectral):** Prove $\min_{F\in\Delta} F(\langle 2,2,2\rangle) = 4$ where $\Delta$ is the asymptotic spectrum

### The Constraint

**Irreversibility barrier (Christandl–Vrana–Zuiddam):** Any method routing through a fixed intermediate tensor $T$ with $\iota(T) > 1$ inherits $\omega > 2$.

**Implication:** ω = 2 requires either:
- A family $\{T_k\}$ with $\iota(T_k) \to 1$, OR
- A method outside the restriction/degeneration framework

This is your north star. Write it on the wall.

---

## Attack Surface

### Tier A — Laser-method optimization (START HERE)

**What:** Optimize the analysis of existing tensors to improve the exponent.

**Why viable:** Every recent ω improvement came from better analysis, not new decompositions. Laptop-scale.

**Method:**
- Take $T^{\otimes N}$, zero out index subsets to obtain $\bigoplus_i \langle n_i, m_i, p_i\rangle$
- Apply asymptotic sum inequality
- Optimize distribution $\pi$ on index set
- Objective: ratio of log-dimensions to entropy terms
- Constraints: marginal consistency

**Your moves:**
1. Reimplement current best analysis, reproduce published exponent to 4 decimals
2. Formalize constraint system (not solver) so feasible region is machine-checked
3. Attack loss terms: identify non-tight inequalities in the chain
4. Produce dual certificates for optimization results

**Deliverable:** `papers/02-laser-optimization` + `certs/analysis/`

**Kill criterion:** If after 6 months you can't reproduce a published exponent, the gap is in your understanding.

### Tier B — Border rank over $k[\varepsilon]$

**What:** Search for border-rank decompositions, not exact rank.

**Why viable:** Only border rank matters asymptotically. Over $\mathbb{F}_2[\varepsilon]/(\varepsilon^2)$, this is pure Boolean.

**Encoding:**
$$\sum_{r=1}^{R} \alpha_r \otimes \beta_r \otimes \gamma_r = \varepsilon^{h}\, T + O(\varepsilon^{h+1})$$

Over $\mathbb{F}_2$ with $d=2$: $d \cdot 3Rn^2$ variables, XOR-friendly, laptop-scale.

**Deliverable:** Border-rank upper bound certificates in `certs/border/`

### Tier B' — Symmetry-adapted search

**What:** Search for $H$-invariant decompositions where $H \le \mathrm{Aut}(T)$.

**Why matters:** Invariant decompositions are descriptions, not lists. Descriptions generalize to families. Families are what T1 requires.

**Method:**
- Fix $H \le \mathrm{Aut}(\langle n,n,n\rangle)$
- Search for $H$-orbits of rank-1 terms
- $R = \sum |\text{orbit}|$

**Deliverable:** Structured decomposition families in `certs/decompositions/`

### Tier C — Automated flattenings

**What:** Mechanize Koszul/Young flattenings for border-rank lower bounds.

**Why viable:** Explicit rank computations on constructible matrices. Mechanizable, certifiable.

**Pipeline:**
- Macaulay2/Singular constructs flattening, computes rank
- Emits certificate
- Lean checks construction is claimed map
- Search over module choices for better bounds

**Deliverable:** `papers/04-flattenings` + `certs/flattenings/`

### Tier D — Formalize asymptotic spectrum

**What:** Machine-check the entire Strassen spectrum theory.

**Why valuable:** Nobody has done this. Useful independent of ω. Builds the language T2/T3 are written in.

**Deliverable:** `papers/01-spectrum-lean` + `lean/Omega/Spectrum/`

### Tier E — The family question

**What:** Find $\{T_k\}$ with $\iota(T_k) \to 1$ or prove no such family exists.

**When:** Only after Tiers A–D give standing and machinery.

**Deliverable:** Either new lead toward T1 or new obstruction theorem.

---

## Repo Structure

```
omega/
├── CLAIMS.md                    # Ledger — see schema below
├── papers/
│   ├── 00-landscape/            # Barriers, what is actually open
│   ├── 01-spectrum-lean/        # Formalization paper
│   ├── 02-laser-optimization/   # Tier A results
│   ├── 03-structured-search/    # Tier B results
│   └── 04-flattenings/          # Tier C results
├── certs/                       # Machine-checkable evidence
│   ├── decompositions/          # Rank/border-rank witnesses
│   ├── border/                  # ε-adic witnesses
│   ├── unsat/                   # DRAT/LRAT proofs
│   ├── analysis/                # LP/optimization dual certificates
│   └── flattenings/             # Flattening rank certificates
├── lean/Omega/                  # Lean 4 formalization
│   ├── Tensor/
│   │   ├── Basic.lean           # ⟨n,m,p⟩, ⊗, ⊕, restriction, degeneration
│   │   ├── Rank.lean            # R, rank-1 predicate, witness checker
│   │   ├── Border.lean          # Border rank via k[ε]
│   │   └── Subrank.lean         # Q, Q̲, asymptotic subrank
│   ├── Spectrum/
│   │   ├── Preorder.lean        # Strassen preorder, asymptotic spectrum Δ
│   │   └── Duality.lean         # R̲(T) = max_{F∈Δ} F(T)
│   ├── Analysis/
│   │   ├── SumIneq.lean         # Asymptotic sum inequality
│   │   └── Laser.lean           # Laser method
│   ├── Barriers/
│   │   └── Irreversibility.lean # ι(T), CVZ obstruction
│   └── Certs/                   # Tactic + decide-based checkers
├── search/                      # Encodings, ansätze, symmetry adapters
├── analysis/                    # Laser-method optimizer
├── cas/                         # Macaulay2/Singular: flattenings, ideals
└── lit/                         # PDFs + structured notes
```

Seed-stage additions to this tree (documented in standards.md): `standards.md`, `dep/` (registries and emitted artifacts), `doc/`, `tools/`, `.github/`, `Makefile`, `requirements.txt`.

### Claims Ledger Schema

```yaml
id: C-0041
statement: R_F2(<4,4,4>) <= 47
field: F_2
status: verified  # conjectured | computed | verified | refuted | published
cert: certs/decompositions/444_F2_47.json
checker: lean/Omega/Certs/Check444.lean
provenance: <primary source, or "found by us, run 2027-03-11">
```

**Rule:** No number enters `papers/` without a ledger row and a certificate that re-checks in CI. If you can't produce the certificate, the row says `conjectured`.

Note: the status vocabulary above is the draft vocabulary; the closed set of DEP&CC 2.0 Chapter 5.4 governs (standards.md section 3.2).

---

## Lean Formalization Plan

### Module Dependency Graph

```
Omega/Tensor/Basic.lean          ⟨n,m,p⟩, ⊗, ⊕, restriction ≤, degeneration ⊴
Omega/Tensor/Rank.lean           R, rank-1 predicate, witness checker
Omega/Tensor/Border.lean         ⊴ via k[ε]; R ≤ r over truncated poly rings
Omega/Tensor/Subrank.lean        Q, Q̲, asymptotic subrank, supermultiplicativity
Omega/Spectrum/Preorder.lean     Strassen preorder, asymptotic spectrum Δ
Omega/Spectrum/Duality.lean      R̲(T) = max_{F∈Δ} F(T)
Omega/Analysis/SumIneq.lean      Schönhage τ-theorem / asymptotic sum inequality
Omega/Analysis/Laser.lean        The laser method, stated as a theorem
Omega/Barriers/Irreversibility.lean   ι(T), the CVZ obstruction
Omega/Certs/                     Tactic + decide-based witness checkers
```

### First Theorems

```lean
theorem strassen_upper : R (⟨2,2,2⟩ : Tensor ℚ) ≤ 7
theorem subrank_supermult : Q (S ⊗ T) ≥ Q S * Q T
```

The second reveals how much asymptotic-limit infrastructure Mathlib lacks. Budget months.

### Crown Jewel

`Omega/Analysis/Laser.lean` — a machine-checked statement of the laser method. This lets you modify the method with the proof assistant tracking exactly which hypotheses you broke.

---

## Workstream Details

### WS1 — Laser-Method Optimization (Tier A)

**Step 1: Reproduction**
- Reimplement current best analysis from scratch
- Reproduce published exponent to 4 decimals
- This is the entry ticket

**Step 2: Formalization**
- Formalize constraint system (not solver)
- Machine-check feasible region
- Bugs in these programs are how wrong exponents get published

**Step 3: Loss-term attack**
- Read Williams–Xu–Xu–Zhou (2024) as: "which inequality in the chain is not tight?"
- Every remaining non-tight step is a target
- The 2024 asymmetric-hashing work removed a specific combinatorial loss

**Step 4: Dual certificates**
- Produce dual certificates for optimization results
- Bound is checkable without rerunning solver

**Deliverable:** `papers/02-laser-optimization` + `certs/analysis/`

**Kill criterion:** If after 6 months you can't reproduce a published exponent, change workstream.

### WS2 — Border Rank Search (Tier B)

**Encoding:**
```
Variables: α[r,i,j], β[r,i,j], γ[r,i,j] ∈ 𝔽_q[ε]/(ε^d)
Constraint: Σ_r α_r ⊗ β_r ⊗ γ_r = ε^h · T + O(ε^{h+1})
```

**Implementation:**
- Over 𝔽₂ with d=2: pure Boolean, XOR-friendly
- Small d, small n, laptop-scale
- Satisfying assignment = border-rank upper bound certificate
- Checkable by exact arithmetic in 𝔽₂[ε]

**Deliverable:** Border-rank certificates in `certs/border/`

### WS3 — Symmetry-Adapted Search (Tier B')

**Method:**
- Fix H ≤ Aut(⟨n,n,n⟩)
- Search for H-orbits of rank-1 terms
- R = Σ |orbit|

**Why:**
- H-invariant decomposition = description, not list
- Descriptions generalize to families
- Families are what T1 requires

**Deliverable:** Structured families in `certs/decompositions/`

### WS4 — Automated Flattenings (Tier C)

**Pipeline:**
1. Macaulay2/Singular constructs Koszul/Young flattening
2. Computes rank
3. Emits certificate
4. Lean checks construction is claimed map
5. Search over module choices for better bounds

**Deliverable:** `papers/04-flattenings` + `certs/flattenings/`

### WS5 — Spectrum and Irreversibility (Tier D → E)

**Formalize:**
- Δ (asymptotic spectrum)
- Strassen duality
- ι (irreversibility)

**Question:** Which families have ι → 1?

**Method:**
- Compute ι for candidate families with certified numerics
- If you find family where it decreases: first genuine lead toward T1

**Deliverable:** `papers/01-spectrum-lean` + analysis in `papers/03-structured-search/`

---

## Phasing

### Year 1

**Q1–Q2:**
- WS1 step 1: reproduce published exponent
- WS2 encoding: border rank over 𝔽₂[ε]
- `Omega/Tensor/*` in Lean

**Q3–Q4:**
- WS1 step 2: formalize constraint system
- WS3 initial symmetry search
- First paper: landscape survey with certified claims ledger

**Deliverable:** `papers/00-landscape` + `lean/Omega/Tensor/`

### Year 2

**Q1–Q2:**
- WS1 step 3: loss-term attack
- WS3 symmetry search
- WS4 flattenings pipeline

**Q3–Q4:**
- WS1 step 4: dual certificates
- `Omega/Analysis/SumIneq.lean`
- Target: one certified numerical improvement OR one new structured family

**Deliverable:** `papers/02-laser-optimization` or `papers/03-structured-search`

### Year 3

**Q1–Q2:**
- WS5: formalize spectrum and irreversibility
- `Omega/Analysis/Laser.lean`
- `Omega/Barriers/Irreversibility.lean`

**Q3–Q4:**
- Compute ι for candidate families
- Target: machine-checked laser method (real contribution whether or not ω moves)

**Deliverable:** `papers/01-spectrum-lean` + `papers/04-flattenings`

### Years 4–6

**The family question:**
- Either find {T_k} with ι → 1
- Or prove new obstruction
- Or conclude framework can't do it and publish that

**Deliverable:** Either breakthrough or deep negative result

### Global Kill Criterion

At any 12-month boundary with no new ledger rows at status `verified`, the program is producing infrastructure and not results. That's acceptable once. Twice means change workstream.

---

## Reading List

**Verify every one against the actual paper.**

### Core Theory
- **Strassen**, *Relative bilinear complexity and matrix multiplication* (1987) — the spectrum
- **Christandl, Vrana, Zuiddam**, *Barriers for Fast Matrix Multiplication from Irreversibility* — the ι obstruction
- **Christandl, Vrana, Zuiddam**, *Universal points in the asymptotic spectrum of tensors* — quantum functionals
- **Landsberg**, *Geometry and Complexity Theory* — flattenings, border rank, geometric machinery
- **Bläser**, *On the complexity of the multiplication of matrices of small formats* — substitution method

### Current Frontier
- **Alman**, *Limits on the Universal Method for Matrix Multiplication* (FOCS 2021) — read for exact constant and hypothesis
- **Williams, Xu, Xu, Zhou**, *Better bounds for ω via asymmetric hashing* (2024) — WS1 entry point
- **Duan, Wu, Zhou** (2023) — prior exponent step

### Search Methods
- **Heule, Kauers, Seidl**, *Local search for fast matrix multiplication* (SAT 2019)
- **Heule, Kauers, Seidl**, *New ways to multiply 3×3 matrices* (JSC 2021)
- **Kauers, Moosbauer**, flip-graph papers — get decomposition files, not just PDFs

### Formal Methods
- **De Moura & Bjørner**, *Z3: An Efficient SMT Solver* (2008)
- **Lean 4 manual** (lean-lang.org)
- **Kovács & Voronkov**, *First-Order Theorem Proving* (2013)

---

## Success Criteria

### Minimum Viable (Year 2)
- Papers 00–02 published
- Lean formalization of tensor basics + laser method
- Clear path to ω = 2 identified (or new obstruction proven)

### Publication-Worthy (Year 3)
- Machine-checked laser method
- One certified improvement to exponent OR one new structured family
- Framework accepted by community

### Breakthrough (Year 4+)
- Lean-verified proof that ω = 2 OR
- New obstruction theorem explaining why ω > 2
- Framework applied to other major problems

### Honest Base Rate
- Year 1 (infrastructure): 80%
- Year 2 (first results): 50%
- Year 3 (laser method formalized): 40%
- Year 4+ (ω = 2 or new obstruction): 10%

**But:** Even partial success produces a shelf of certified artifacts that are useful to the field.

---

## Failure Modes

The barriers are theorems, not opinions. Tier A is crowded with strong people and the remaining losses may be genuinely tight. Formalization is slow and Mathlib's asymptotic-analysis support will fight you.

**The plan is constructed so that the failure mode is a shelf of certified artifacts rather than nothing:**
- A Lean tensor-rank library
- A machine-checked laser method
- A trustworthy claims ledger
- Better flattenings

Those exist whether or not ω moves, and they're the things that would make someone hand you the resources to attack the real target later.

---

## Immediate Action

**Today:**
1. Create repo with structure above
2. Write CLAIMS.md with schema
3. Install Z3, Lean 4, Vampire, Macaulay2
4. Start WS1 step 1: reimplement current best laser-method analysis

**This week:**
1. Reproduce published exponent to 4 decimals
2. Set up dual certificate pipeline
3. Begin `Omega/Tensor/Basic.lean`

**This month:**
1. Complete WS1 step 1
2. First ledger row at status `verified`
3. `Omega/Tensor/Basic.lean` compiles

Everything else is downstream of proving to yourself that you can make the current machinery run.
