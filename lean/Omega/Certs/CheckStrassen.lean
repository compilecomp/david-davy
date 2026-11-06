import Omega.Tensor.Basic
import Omega.Tensor.Rank

/-!
# Omega.Certs.CheckStrassen

Machine-checked Strassen decomposition over the integers, full 64-entry space.

Annotation:
  ID: Omega.Certs.CheckStrassen
  CLASS: DEP-0
  WHAT: The Strassen 7-term scheme as explicit integer vectors, and the
        kernel-checked theorem that the scheme computes the 2x2 matrix
        multiplication tensor on the full 4x4x4 index space.
  WHY:  The anchor machine-checked node of the repository (ledger row C-0016).
  STATUS: machine-checked
  COMPLETE: complete
  HYP: 'none; the theorem is the literal 64-entry equality'
  DEPENDS: [Omega.Tensor.Basic, Omega.Tensor.Rank, C-0001]
  GAP: [G-0004]
  OWNER: repo-maintainer
  EVIDENCE: 'lean/lake build; axiom ledger: #print axioms below'

Statement fidelity (DEP&CC 2.0 Chapter 19.5; full map in doc/fidelity-checkstrassen.md):
  Prose: "the Strassen scheme computes the 2x2 matrix product over Z".
  Formal: strassenSum pa pb pc = mmTensor pa pb pc for all 64 index triples,
  where mmTensor encodes conv.mm_entry and strassenSum encodes the classical
  M1..M7 assembly. Quantifier shape: the bounded enumeration in checkUpTo
  covers each triple exactly once, so the Bool check equals the universally
  quantified statement at this fixed size.

Scope note (G-0004): the theorem is about the fixed 2x2x2 integer instance.
The general statement over arbitrary fields and sizes requires the Mathlib layer;
this file does not claim it.

Axiom ledger: `#print axioms strassen7_full_space` is executed below; the expected
result is "does not depend on any axioms" (no choice, no propext, no native
evaluation). CI archives the build log.
-/

/-- A-support vectors of the Strassen scheme, in the order M1..M7. -/
def uS : Nat → AIdx → Int
  | 0, (0, 0) => 1
  | 0, (1, 1) => 1
  | 1, (1, 0) => 1
  | 1, (1, 1) => 1
  | 2, (0, 0) => 1
  | 3, (1, 1) => 1
  | 4, (0, 0) => 1
  | 4, (0, 1) => 1
  | 5, (1, 0) => 1
  | 5, (0, 0) => -1
  | 6, (0, 1) => 1
  | 6, (1, 1) => -1
  | _, _ => 0

/-- B-support vectors of the Strassen scheme. -/
def vS : Nat → BIdx → Int
  | 0, (0, 0) => 1
  | 0, (1, 1) => 1
  | 1, (0, 0) => 1
  | 2, (0, 1) => 1
  | 2, (1, 1) => -1
  | 3, (1, 0) => 1
  | 3, (0, 0) => -1
  | 4, (1, 1) => 1
  | 5, (0, 0) => 1
  | 5, (0, 1) => 1
  | 6, (1, 0) => 1
  | 6, (1, 1) => 1
  | _, _ => 0

/-- C-support vectors of the Strassen scheme; the output assembly
c11 = M1+M4-M5+M7, c12 = M3+M5, c21 = M2+M4, c22 = M1-M2+M3+M6 is folded here. -/
def wS : Nat → CIdx → Int
  | 0, (0, 0) => 1
  | 0, (1, 1) => 1
  | 1, (1, 0) => 1
  | 1, (1, 1) => -1
  | 2, (0, 1) => 1
  | 2, (1, 1) => 1
  | 3, (1, 0) => 1
  | 3, (0, 0) => 1
  | 4, (0, 1) => 1
  | 4, (0, 0) => -1
  | 5, (1, 1) => 1
  | 6, (0, 0) => 1
  | _, _ => 0

/-- The Strassen scheme as a sum of 7 rank-1 terms. -/
def strassenSum : Tensor3 Int :=
  sumTerms (List.map (fun r => (uS r, vS r, wS r)) (List.range 7))

/-- The full 64-entry check. -/
def strassenFullCheck : Bool :=
  witnessCheck (mmTensor (α := Int)) (List.map (fun r => (uS r, vS r, wS r)) (List.range 7))

/-- Main theorem: the Strassen scheme equals the 2x2 matrix multiplication tensor
over the integers on the full index space. -/
theorem strassen7_full_space : strassenFullCheck = true := by decide

#print axioms strassen7_full_space
