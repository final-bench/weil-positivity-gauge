/-
  R2 (Universality of the Archimedean constant): cancellation core, machine-checked.

  Paper claim:
      B(ν) = 2 - 2γ - 2ψ(ν) - 2·log 2 ,   and after the ψ-cancellation
      B₀   = log q - 2·log 2            (depends only on the conductor q).

  WHAT IS PROVED HERE (no `sorry`):
      the algebraic cancellation mechanism, i.e. that γ and ψ(ν) drop out identically
      when the head constant is combined with twice the half-sum c₁, and the two
      concrete instantiations (q = 1 and general q).

  WHAT IS *ASSUMED* (supplied as real parameters, not proved):
      the analytic identification of the Laurent data
        · Γ(s)  near s = -1        (contributes γ)
        · ζ(s,ν) near s = 1        (contributes -ψ(ν))
      These identifications are the analytic part of the paper and are not formalized here.
-/
import Mathlib

namespace RiemannR2

open Real

/-- **Cancellation core.**  `head` is the constant coming from the Γ-side Laurent data,
`c₁ = (γ + ψ + L - 1)/2` the half-sum coming from the ζ-side.  Both contain `γ` and `ψ`;
combining them as `head - 2*c₁` makes *both* disappear, leaving only `M - L`. -/
theorem cancellation (γ ψ M L : ℝ) :
    (γ - 1 + ψ + M) - 2 * ((γ + ψ + L - 1) / 2) = M - L := by
  ring

/-- The `ζ` instantiation: `M = log (π/2)`, `L = log (2π)`. -/
theorem log_pi_half_sub_log_two_pi :
    Real.log (π / 2) - Real.log (2 * π) = -2 * Real.log 2 := by
  have hπ : π ≠ 0 := ne_of_gt pi_pos
  have h2 : (2:ℝ) ≠ 0 := by norm_num
  rw [Real.log_div hπ h2, Real.log_mul h2 hπ]
  ring

/-- **B₀ for the Riemann zeta function (conductor 1).** -/
theorem B_zero_zeta (γ ψ : ℝ) :
    (γ - 1 + ψ + Real.log (π / 2)) - 2 * ((γ + ψ + Real.log (2 * π) - 1) / 2)
      = -2 * Real.log 2 := by
  rw [cancellation]
  exact log_pi_half_sub_log_two_pi

/-- The conductor-`q` instantiation: `M = log (π q / 2)`. -/
theorem log_pi_q_half_sub_log_two_pi (q : ℝ) (hq : 0 < q) :
    Real.log (π * q / 2) - Real.log (2 * π) = Real.log q - 2 * Real.log 2 := by
  have hπ : π ≠ 0 := ne_of_gt pi_pos
  have h2 : (2:ℝ) ≠ 0 := by norm_num
  have hq' : q ≠ 0 := ne_of_gt hq
  rw [Real.log_div (mul_ne_zero hπ hq') h2, Real.log_mul hπ hq', Real.log_mul h2 hπ]
  ring

/-- **B₀ depends only on the conductor.**  Neither `γ` nor `ψ(ν)` survives: the
Archimedean parameter `ν` is completely absent from the right-hand side. -/
theorem B_zero_conductor (γ ψ q : ℝ) (hq : 0 < q) :
    (γ - 1 + ψ + Real.log (π * q / 2)) - 2 * ((γ + ψ + Real.log (2 * π) - 1) / 2)
      = Real.log q - 2 * Real.log 2 := by
  rw [cancellation]
  exact log_pi_q_half_sub_log_two_pi q hq

/-- **Universality, stated as independence of `ν`.**  For any two Archimedean
parameters `ψ₁ ψ₂` (i.e. `ψ(ν₁)`, `ψ(ν₂)`) the resulting constant is the same. -/
theorem B_zero_indep_of_nu (γ ψ₁ ψ₂ q : ℝ) :
    ((γ - 1 + ψ₁ + Real.log (π * q / 2)) - 2 * ((γ + ψ₁ + Real.log (2 * π) - 1) / 2))
      = ((γ - 1 + ψ₂ + Real.log (π * q / 2)) - 2 * ((γ + ψ₂ + Real.log (2 * π) - 1) / 2)) := by
  rw [cancellation, cancellation]

end RiemannR2

section Verification
open RiemannR2
#print axioms RiemannR2.cancellation
#print axioms RiemannR2.log_pi_half_sub_log_two_pi
#print axioms RiemannR2.B_zero_zeta
#print axioms RiemannR2.log_pi_q_half_sub_log_two_pi
#print axioms RiemannR2.B_zero_conductor
#print axioms RiemannR2.B_zero_indep_of_nu
end Verification
