/-!
# Omega.Tensor.Border

STATUS: placeholder (DEP&CC 2.0 Chapter 5.5: reserved statements, no proofs,
unreferenced by DEP-0 nodes). Owner: repo-maintainer. Ticket: OMEGA-6 / gap G-0006.

Statement drafts, to be ported onto Mathlib structures:

  variable {k : Type*} [CommRing k]
  def BorderRank (T : Tensor3 k) (r : Nat) : Prop :=
    exists terms : Fin r -> (Dual k) x (Dual k) x (Dual k),
      exists h : Nat, 1 <= h /\ (terms-sum) = (eps^h) * T in k[eps]/(eps^(h+1))

  convention: RB(T) <= r when BorderRank T r holds (conv.border).

Porting plan: define k[eps]/(eps^2) as an AdjoinRoot or a quotient of
Polynomial k; state the coefficient-pair encoding used by tools/check_certs.py
as a ring isomorphism with the quotient; discharge the well-definedness of the
coefficient extraction. Dependencies: Mathlib.Module, Mathlib.RingTheory.
