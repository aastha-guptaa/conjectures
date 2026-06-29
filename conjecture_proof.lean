--not complete yet, just trying to formalize some structures--



structure SimpleGraph (V : Type) where
  Adj : V → V → Prop
  symm : ∀ u v, Adj u v → Adj v u
  loopless : ∀ v, ¬ Adj v v


def IsComplete {V : Type} (G : SimpleGraph V) : Prop :=
  ∀ u v, u ≠ v → G.Adj u v


theorem adj_implies_ne {V : Type} (G : SimpleGraph V) (u v : V) (h : G.Adj u v) : u ≠ v := by
  intro heq
  subst heq
  have hloop := G.loopless u
  exact hloop h

theorem complete_graph_adj_iff_ne {V : Type} (G : SimpleGraph V) (hcomplete : IsComplete G) (u v : V) :
    G.Adj u v ↔ u ≠ v := by
  constructor
  ·
    apply adj_implies_ne G
  ·
    apply hcomplete u v


def Path2 {V : Type} (G : SimpleGraph V) (u w : V) : Prop :=
  ∃ v, G.Adj u v ∧ G.Adj v w

theorem path2_intermediate_distinct {V : Type} (G : SimpleGraph V) (u w : V) (hpath : Path2 G u w) :
    ∃ v, G.Adj u v ∧ G.Adj v w ∧ v ≠ u ∧ v ≠ w := by
  cases hpath with
  | intro v h =>
    have hadj1 := h.left
    have hadj2 := h.right
    have h_vu : G.Adj v u := G.symm u v hadj1
    have hne1 : v ≠ u := adj_implies_ne G v u h_vu
    have hne2 : v ≠ w := adj_implies_ne G v w hadj2
    exact ⟨v, hadj1, hadj2, hne1, hne2⟩
