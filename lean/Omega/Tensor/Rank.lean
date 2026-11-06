import Omega.Tensor.Basic

/-!
# Omega.Tensor.Rank

The bounded-domain witness checker for rank decompositions over the integers.

Annotation:
  ID: Omega.Tensor.Rank
  CLASS: DEP-0
  WHAT: A Bool-valued checker that a list of rank-1 integer terms sums to a given
        tensor on all 64 index triples of the 2x2x2 space.
  WHY:  Turns a witness into a machine-checked statement without Mathlib.
  STATUS: machine-checked
  COMPLETE: complete
  HYP: 'the checker enumerates all 64 triples exactly once (mixed-radix counting
       with m = 32*i + 16*jx + 8*jy + 4*k + 2*iz + kz)'
  DEPENDS: [Omega.Tensor.Basic]
  GAP: [G-0006]
  OWNER: repo-maintainer
  EVIDENCE: lean/lake build exits 0

Statement scope: the checker covers the 2x2x2 full index space (six indices of
range 2). Generalization to symbolic sizes requires Fin-indexed enumeration and is
part of the Mathlib layer (G-0006).
-/

/-- Mixed-radix enumeration of the 64 triples, each exactly once. -/
def checkUpTo (p : AIdx → BIdx → CIdx → Bool) : Nat → Bool
  | 0 => true
  | n + 1 =>
    let m := n % 64
    let i := m / 32
    let jx := (m / 16) % 2
    let jy := (m / 8) % 2
    let k := (m / 4) % 2
    let iz := (m / 2) % 2
    let kz := m % 2
    p (i, jx) (jy, k) (iz, kz) && checkUpTo p n

/-- Sum of a list of rank-1 terms. -/
def sumTerms {α : Type} [Add α] [Mul α] [Zero α]
    (terms : List ((AIdx → α) × (BIdx → α) × (CIdx → α))) : Tensor3 α :=
  fun pa pb pc =>
    terms.foldl (fun acc t => acc + t.1 pa * t.2.1 pb * t.2.2 pc) (Zero.zero : α)

/-- The witness checker for a 2x2x2 integer tensor against a term list. -/
def witnessCheck (T : Tensor3 Int)
    (terms : List ((AIdx → Int) × (BIdx → Int) × (CIdx → Int))) : Bool :=
  checkUpTo (fun pa pb pc => sumTerms terms pa pb pc == T pa pb pc) 64
