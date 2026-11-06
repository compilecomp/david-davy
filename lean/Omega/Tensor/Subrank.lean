/-!
# Omega.Tensor.Subrank

STATUS: placeholder. Owner: repo-maintainer. Ticket: OMEGA-6 / gap G-0006.

Statement drafts:

  def Subrank (T : Tensor3 k) : Nat := max over restrictions of T of diagonal size
  def AsymSubrank (T : Tensor3 k) : NNReal := liminf Q(T^{x N})^(1/N)

  theorem subrank_supermult : Q(S (x) T) >= Q(S) * Q(T)

The second statement is the one the research plan flags as exposing how much
asymptotic-limit infrastructure Mathlib lacks; budget accordingly (RESEARCH_PLAN.md,
Lean Formalization Plan, First Theorems). Dependencies: Mathlib order and filter
layers for liminf; Mathlib.Analysis for the real exponent machinery.
