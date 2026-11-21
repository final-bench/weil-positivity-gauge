### Independent reproduction of the released proof

VIDRAFT compiles the released Lean proof from scratch on its own hardware and asks the Lean kernel which axioms the final theorem uses.

| Item | Value |
|---|---|
| Release | 14 archive parts at `alpo.ge/lean.tar.gz.partNN` |
| SHA-256 of the joined archive | `9631b4f020199e580ba86178cb56c6e9b09f690c2369a80dc4334aa93f49c7fc` |
| Size | 175,187 Lean files, 17,374,215 lines |
| Toolchain | Lean 4.33.1, Mathlib pinned at `0df444a3` |
| Final theorems in `Main.lean` | `riemannHypothesis`, `riemannZeta_eq_zero_re`, `LFunction_ne_zero_of_half_lt_re`, `LFunction_eq_zero_re` |
| Measured build rate | 250 files per minute on a 192-core node (21 November 2026), about 12 hours for the full tree |
| Status | Full build scheduled. |

This page is updated with the build result and the output of `#print axioms riemannHypothesis`.