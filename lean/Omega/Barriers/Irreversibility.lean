/-!
# Omega.Barriers.Irreversibility

STATUS: placeholder. Owner: repo-maintainer. Ticket: OMEGA-8 / gap G-0003.

Statement draft: the Christandl-Vrana-Zuiddam irreversibility barrier.

  def Irreversibility (T) : Real  -- iota(T), exact form pinned by ext:cvz2021barriers

  theorem cvz_barrier (T) (hT : F(T) = omega for some F in Spectrum)
      (hiota : iota(T) > 1) : <method class routed through T inherits omega > 2>

The exact hypothesis shape (which method class, which inequality) must be
transcribed from the pinned source before this file carries a statement; the
transcription is gated on gap G-0003 (statement-fidelity audit). The research-plan
constraint "omega = 2 requires a family with iota -> 1 or a method outside the
restriction/degeneration framework" is DEP-2 prose until then.
