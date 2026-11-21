### Statements verified by the Lean 4 kernel

Checked with Lean 4.37.0-rc1 and Mathlib `3eae40f`. Every statement below depends only on the three standard axioms (`propext`, `Classical.choice`, `Quot.sound`).

| File | Statement | Meaning |
|---|---|---|
| `RiemannR2_Basic.lean` | `cancellation`, `B_zero_zeta`, `B_zero_conductor`, `B_zero_indep_of_nu` and two logarithm identities | The spectral constant of the operator depends only on the conductor. Euler's constant and the digamma value cancel identically. |
| `Recurrence.lean` | `summable_term` | The digamma series converges for every complex `s`. |
| `Recurrence.lean` | `tsum_term_add_one`, `digammaSeries_add_one` | The series obeys the digamma recurrence `f(s+1) = f(s) + 1/s`. |
| `Recurrence.lean` | `diff_periodic` | The difference between Mathlib's digamma function and the series is periodic with period one. |

To check them yourself: install Lean with Mathlib, then run `lake env lean Recurrence.lean`. The command prints the axiom list for each statement.