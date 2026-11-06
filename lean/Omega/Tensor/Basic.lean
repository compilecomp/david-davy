/-!
# Omega.Tensor.Basic

Matrix multiplication tensors and rank-1 terms over core Lean 4 (no Mathlib).

Annotation:
  ID: Omega.Tensor.Basic
  CLASS: DEP-0
  WHAT: The tensor space of a matrix multiplication tensor shape, represented as
        functions on index triples; the matrix multiplication tensor; rank-1 terms.
  WHY:  Foundation of every Lean artifact in this repository.
  STATUS: machine-checked (the smoke theorems are kernel-checked by decide)
  COMPLETE: complete
  HYP: none
  DEPENDS: []
  GAP: [G-0006]
  OWNER: repo-maintainer
  EVIDENCE: lean/lake build exits 0 under the pinned toolchain

Conventions (dep/conventions.yaml, conv.mm_entry):
  A tensor of shape (a, b, c) is a function on triples (pa, pb, pc) with
  pa = (i, j) in [a]x[b], pb = (j2, k) in [b]x[c], pc = (i2, k2) in [a]x[c].
  The matrix multiplication tensor is 1 exactly at the consistent triples
  (i = i2 and j = j2 and k = k2) and 0 elsewhere. Equality of tensors is tested on
  the full index space, including the vanishing entries; a candidate decomposition
  that agrees only on the support of the target is rejected (see the third smoke
  theorem, which pins a vanishing entry).

Mathlib target (G-0006): restate the definitions over finite-dimensional modules
once Mathlib is integrated; the Nat-index encoding below is computational and
self-contained.
-/

/-- Index into the first (A) factor: a pair (row, column) of an a x b matrix. -/
abbrev AIdx := Nat × Nat

/-- Index into the second (B) factor: a pair (column, output column). -/
abbrev BIdx := Nat × Nat

/-- Index into the third (C) factor: a pair (row, output column). -/
abbrev CIdx := Nat × Nat

/-- The ambient space of a tensor shape: functions on index triples. -/
def Tensor3 (α : Type) : Type := AIdx → BIdx → CIdx → α

/-- The matrix multiplication tensor, per dep/conventions.yaml conv.mm_entry. -/
def mmTensor {α : Type} [Zero α] [inst : OfNat α 1] [DecidableEq α] : Tensor3 α :=
  fun (i, jx) (jy, k) (iz, kz) =>
    if i = iz ∧ jx = jy ∧ k = kz then inst.ofNat else 0

/-- A rank-1 term: the tensor of a triple of vectors. -/
def rankOne {α : Type} [Mul α] (u : AIdx → α) (v : BIdx → α) (w : CIdx → α) : Tensor3 α :=
  fun pa pb pc => u pa * v pb * w pc

-- Smoke theorems (kernel-checked): the mm tensor is 1 on consistent triples and 0
-- on inconsistent ones. The fourth pins a vanishing entry of the full space.
example : mmTensor (α := Int) (0, 0) (0, 0) (0, 0) = 1 := by decide
example : mmTensor (α := Int) (1, 1) (0, 0) (0, 0) = 0 := by decide
example : mmTensor (α := Int) (0, 1) (1, 0) (0, 0) = 1 := by decide
example : mmTensor (α := Int) (0, 1) (1, 0) (0, 1) = 0 := by decide
