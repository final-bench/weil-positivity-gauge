/-
  Step 2 (iteration 1): summability of the digamma series, no hypothesis on s.
  term s n = 1/(n+1) - 1/(n+s).  For large n the closed form (s-1)/((n+1)(n+s)) is O(n^-2).
-/
import Mathlib

namespace DigammaSeries2

open Complex Filter Topology

theorem cast_add_one_ne_zero (n : ℕ) : ((n : ℂ) + 1) ≠ 0 := by
  have h : ((n : ℂ) + 1) = ((n + 1 : ℕ) : ℂ) := by push_cast; ring
  rw [h, Ne, Nat.cast_eq_zero]
  omega

noncomputable def term (s : ℂ) (n : ℕ) : ℂ := 1 / (n + 1) - 1 / (n + s)

theorem term_eq (s : ℂ) (n : ℕ) (h : (n : ℂ) + s ≠ 0) :
    term s n = (s - 1) / (((n : ℂ) + 1) * ((n : ℂ) + s)) := by
  have h1 : ((n : ℂ) + 1) ≠ 0 := cast_add_one_ne_zero n
  simp only [term]
  field_simp
  ring

theorem norm_term_le (s : ℂ) (n : ℕ) (hn : Nat.ceil (2 * ‖s‖) + 1 ≤ n) :
    ‖term s n‖ ≤ (2 * ‖s - 1‖) * (1 / (n : ℝ) ^ 2) := by
  have hn1' : (1 : ℕ) ≤ n := le_trans (Nat.le_add_left 1 _) hn
  have hn0 : (0 : ℝ) < n := by exact_mod_cast hn1'
  have h2s : 2 * ‖s‖ ≤ n := by
    have h1 := Nat.le_ceil (2 * ‖s‖)
    have h2 : ((Nat.ceil (2 * ‖s‖) : ℕ) : ℝ) ≤ n := by
      exact_mod_cast (le_trans (Nat.le_succ _) hn)
    linarith
  have hnorm : ‖(n : ℂ)‖ = n := by simp
  have hns : (n : ℝ) / 2 ≤ ‖(n : ℂ) + s‖ := by
    have h1 : ‖(n : ℂ)‖ - ‖-s‖ ≤ ‖(n : ℂ) - (-s)‖ := norm_sub_norm_le _ _
    rw [norm_neg, sub_neg_eq_add, hnorm] at h1
    linarith
  have hn1 : (n : ℝ) ≤ ‖(n : ℂ) + 1‖ := by
    have h : ((n : ℂ) + 1) = ((n + 1 : ℕ) : ℂ) := by push_cast; ring
    rw [h, Complex.norm_natCast]
    push_cast
    linarith
  have hne : (n : ℂ) + s ≠ 0 := by
    intro h
    rw [h, norm_zero] at hns
    linarith
  have hprod : (n : ℝ) ^ 2 / 2 ≤ ‖(n : ℂ) + 1‖ * ‖(n : ℂ) + s‖ := by
    have : (n : ℝ) * ((n : ℝ) / 2) ≤ ‖(n : ℂ) + 1‖ * ‖(n : ℂ) + s‖ :=
      mul_le_mul hn1 hns (by positivity) (norm_nonneg _)
    nlinarith [this]
  have hpos : 0 < ‖(n : ℂ) + 1‖ * ‖(n : ℂ) + s‖ := lt_of_lt_of_le (by positivity) hprod
  rw [term_eq s n hne, norm_div, norm_mul, div_le_iff₀ hpos]
  have hk : ‖s - 1‖ = (2 * ‖s - 1‖) * (1 / (n : ℝ) ^ 2) * ((n : ℝ) ^ 2 / 2) := by
    field_simp
  calc ‖s - 1‖ = (2 * ‖s - 1‖) * (1 / (n : ℝ) ^ 2) * ((n : ℝ) ^ 2 / 2) := hk
    _ ≤ (2 * ‖s - 1‖) * (1 / (n : ℝ) ^ 2) * (‖(n : ℂ) + 1‖ * ‖(n : ℂ) + s‖) := by
        apply mul_le_mul_of_nonneg_left hprod
        positivity

/-- Summability of the digamma series for every complex `s` (Lean's `1/0 = 0` makes the
pole terms harmless, so no hypothesis is needed). -/
theorem summable_term (s : ℂ) : Summable (term s) := by
  have hsum : Summable (fun n : ℕ => (2 * ‖s - 1‖) * (1 / (n : ℝ) ^ 2)) :=
    (Real.summable_one_div_nat_pow.mpr (by norm_num)).mul_left _
  refine Summable.of_norm_bounded_eventually_nat hsum ?_
  filter_upwards [eventually_ge_atTop (Nat.ceil (2 * ‖s‖) + 1)] with n hn
  exact norm_term_le s n hn

end DigammaSeries2

#print axioms DigammaSeries2.summable_term
