### Independent reproduction of the released proof

VIDRAFT compiled the released Lean proof from scratch on its own hardware and asked the Lean kernel which axioms the final theorem uses. **Independently reproduced.**

| Item | Value |
|---|---|
| Release | 14 archive parts at `alpo.ge/lean.tar.gz.partNN` |
| SHA-256 of the joined archive | `9631b4f020199e580ba86178cb56c6e9b09f690c2369a80dc4334aa93f49c7fc` |
| Size | 175,187 Lean files, 17,374,215 lines |
| Toolchain | Lean 4.33.1, Mathlib pinned at `0df444a3` |
| Final theorems in `Main.lean` | `riemannHypothesis`, `riemannZeta_eq_zero_re`, `LFunction_ne_zero_of_half_lt_re`, `LFunction_eq_zero_re` |
| Build | 183,903 jobs, 175,187 modules, 0 errors, 17.5 hours on 8x RTX PRO 6000 / 192 cores, completed 22 November 2026 |
| Kernel axioms of `riemannHypothesis` | `propext`, `Classical.choice`, `Quot.sound` (standard axioms only) |

```
'riemannHypothesis' depends on axioms: [propext, Classical.choice, Quot.sound]
Build completed successfully (183903 jobs).
```
