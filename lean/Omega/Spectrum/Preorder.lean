/-!
# Omega.Spectrum.Preorder

STATUS: placeholder. Owner: repo-maintainer. Ticket: OMEGA-6 / gap G-0006.

Statement drafts:

  class MonoidalInvariant (F : Tensor3 k -> NNReal) : Prop where
    monotone : S le_Deg T -> F S <= F T
    additive : F (S (+) T) >= F S + F T
    multiplicative : F (S (x) T) = F S * F T
    normalized : F (one tensor) = 1

  def Spectrum : Set (Tensor3 k -> NNReal) := {F | MonoidalInvariant F}

The relation le_Deg (degeneration) is defined in conv.degeneration and must be
formalized in Omega.Tensor.Border before this file has content. Pinpoint source for
the axioms: ext:strassen1987 (audit pending, gap G-0003).
