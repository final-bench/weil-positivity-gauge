# Seeing the Riemann Hypothesis Hold: A Live Weil Positivity Gauge for Zeta and Dirichlet L-Functions

**VIDRAFT · FINAL-Bench · 21 November 2026**

**Live instrument:** https://huggingface.co/spaces/FINAL-Bench/weil-positivity-gauge
**Article:** https://huggingface.co/blog/FINAL-Bench/seeing-the-riemann-hypothesis-hold-a-live-weil-pos
**Dataset:** https://huggingface.co/datasets/FINAL-Bench/weil-positivity-gauge

## Summary

On 20 November 2026 Levent Alpöge announced a proof of the Riemann Hypothesis, found with Claude and released as 17.4 million lines of Lean. A formal proof establishes that the statement holds. We release an instrument that shows it holding.

The instrument computes the lowest eigenvalue of Weil's quadratic form, realized as the operator introduced by M. Suzuki in 2026. By Weil's criterion the Riemann Hypothesis is equivalent to this form never being negative. We report four results.

1. **Positivity for genuine L-functions.** The zeta function and four Dirichlet L-functions (conductors 3, 4, 5, 8) give a positive lowest eigenvalue at every resolved interval size.
2. **Negativity for imitations.** Three objects that differ from a genuine L-function in a single ingredient give a negative lowest eigenvalue, converged to three digits.
3. **A boundary law.** The eigenfunctions vanish at the endpoints as `(log(1/d))^(-1/2)`, the optimal rate of the logarithmic Laplacian.
4. **Formal verification.** Ten statements on the Archimedean constants of the operator are verified by the Lean 4 kernel.

Every figure in the Space is computed in the visitor's session. The full experiment reproduces in about thirty seconds on a free CPU.

## Repository layout

| Path | Content |
|---|---|
| `code/` | Experiments of Tables 3.1 and 3.2, and the operator assembly |
| `lean/` | Lean 4 files verified by the kernel |
| `results/` | Raw outputs of 21 November 2026 |
| `space/` | Source of the live Gradio instrument |

## 1. Background

Weil (1952) showed that the Riemann Hypothesis is equivalent to the positivity of a quadratic form assembled from the von Mangoldt function and the Gamma factor of the functional equation. Yoshida localized the criterion to test functions supported in `[-a, a]`. Suzuki (arXiv:2606.09096) wrote the localized form through the screw function `g` of the zeta function,

```
Q_a(v) = ∬ g(x - y) v'(x) v'(y) dx dy ,   v ∈ H^1_0(-a, a),
```

and proved that it defines a self-adjoint operator with discrete spectrum. The paper contains no numerics. VIDRAFT gave the first numerical realization in July 2026, obtained the closed form of the Archimedean spectrum, and measured the lowest eigenvalue for the zeta function.

The proof announced on 20 November passes through positivity statements of the same functional. That is the reason this operator is the natural instrument for looking at the result.

## 2. Method

For a real primitive character `χ` of conductor `q` and parity `𝔞`, the screw function is

```
g_χ(t) = P(t) - (t/2)(ψ(ν) - log(π/q)) - (1/4) Λ_ν(t) + Σ_n χ(n) Λ(n) n^(-1/2) (t - log n)_+ ,
ν = 1/4 + 𝔞/2 ,   Λ_ν(t) = Σ_{k≥0} (1 - e^{-2t(k+ν)}) / (k+ν)^2 ,
```

with the pole term `P(t) = -4(e^{t/2} + e^{-t/2} - 2)` present for the zeta function only. The form is discretized with P1 finite elements on `[-a, a]`, assembled with 8x oversampling, and the lowest eigenvalue is obtained from the generalized symmetric eigenproblem.

**Convergence diagnostic.** By Rayleigh-Ritz the discrete eigenvalue decreases to the true one as the mesh is refined. A ratio `λ(N=800)/λ(N=1600)` equal to one identifies a measured value. A ratio near four identifies a value under the numerical resolution. Only measured values are reported as signs.

**Controls.** Each imitation alters one ingredient of a genuine object: the pole term, the parity of the Gamma factor, or the sign of the prime weights.

## 3. Results

### 3.1 Genuine L-functions and imitations

| Object | λ₁ at a = 0.35 | a = 0.50 | a = 0.70 | a = 0.85 | a = 1.00 | Sign |
|---|---|---|---|---|---|---|
| Riemann zeta | 1.198e-3 | 1.0e-6 | under res. | under res. | under res. | + |
| L(s, χ₃) | 1.386e-1 | 2.121e-2 | 2.057e-4 | under res. | under res. | + |
| L(s, χ₄) | 4.247e-1 | 1.403e-1 | 6.550e-3 | 1.437e-4 | under res. | + |
| L(s, χ₅) | 3.147e-1 | 9.029e-2 | 4.784e-3 | 2.042e-4 | under res. | + |
| L(s, χ₈) | 7.827e-1 | 3.590e-1 | 8.715e-2 | 1.238e-2 | 9.246e-4 | + |
| Imitation A: zeta primes, pole term removed | -1.299 | -1.987 | -2.866 | -3.572 | -4.304 | - |
| Imitation B: χ₃ with the wrong parity | -0.196 | -0.421 | -0.587 | -0.775 | -0.876 | - |
| Imitation C: χ₃ with prime signs flipped | +0.135 | -0.403 | -0.857 | -1.052 | -1.286 | - |

All five genuine objects are positive at every resolved point. All three imitations are negative with a mesh ratio of 1.000. Imitation C coincides with the genuine `χ₃` until the first prime enters the interval at `a = (log 2)/2`, and turns negative immediately after. The zeta row reproduces the July 2026 measurement to ten digits.

The quadratic form separates arithmetic objects from objects that only resemble them. For Dirichlet L-functions the resolvable window extends to `a = 1.0`, twice the window available for the zeta function.

### 3.2 The boundary law

Let `d` be the distance to an endpoint. For the first eigenfunction at `a = 0.2`, `N = 6400`:

| Octave `d/a` | Local power exponent | Local logarithmic slope |
|---|---|---|
| 0.08 to 0.16 | 0.351 | 3.758 |
| 0.04 to 0.08 | 0.271 | 4.455 |
| 0.02 to 0.04 | 0.210 | 4.809 |
| 0.01 to 0.02 | 0.167 | 4.943 |
| 0.005 to 0.01 | 0.136 | 4.975 |
| 0.0025 to 0.005 | 0.115 | 4.991 |

The power exponent decreases monotonically toward zero. The logarithmic slope `d(u^-2)/d log(1/d)` converges. Hence

```
u(d) ~ c (log(1/d))^(-1/2)   as d → 0.
```

The same pipeline applied to the Laplacian returns the exponent 1.0000. The rate is the optimal boundary regularity of the logarithmic Laplacian (Hernández-Santamaría, López Ríos, Saldaña, arXiv:2401.18033), consistent with the principal symbol `log|D|` of the Weil operator.

### 3.3 Formal verification

Verified with Lean 4.37.0-rc1 and Mathlib `3eae40f`, standard axioms only:

- `RiemannR2.cancellation`, `B_zero_zeta`, `B_zero_conductor`, `B_zero_indep_of_nu`: the spectral constant `B₀ = log q - 2 log 2` depends on the conductor alone; Euler's constant and `ψ(ν)` cancel identically.
- `DigammaSeries2.summable_term`: the digamma series converges for every complex `s`.
- `DigammaSeries2.tsum_term_add_one`, `digammaSeries_add_one`: the series satisfies `f(s+1) = f(s) + 1/s`.
- `DigammaSeries2.diff_periodic`: the difference between `Complex.digamma` and the series has period one.

## 4. Independent reproduction of the proof

VIDRAFT compiles the released proof from scratch and queries the Lean kernel for the axioms of the final theorem. Archive SHA-256 `9631b4f0…49c7fc`, 175,187 files, Lean 4.33.1, Mathlib `0df444a3`. `Main.lean` states `riemannHypothesis`, `riemannZeta_eq_zero_re`, `LFunction_ne_zero_of_half_lt_re` and `LFunction_eq_zero_re`. A 192-core node builds the tree at 250 files per minute. The result is posted on the Space.

## 5. The Cyclic Phase Hypothesis

The Archimedean spectrum of the operator has the closed form

```
μ_k = log(k - 1/2) + γ + log(π/2).
```

The offset one half was identified through the **Cyclic Phase Hypothesis**, a VIDRAFT result. From the sum rule `Σ δλ_k = 0` and the even and odd cycle of the spectrum it proposes that the offset is a phase that winds once around the boundary. A sweep from Dirichlet to Neumann conditions moved the offset from `-1/2` to `+1/2`, an integer step of one, which identifies it as the boundary Maslov phase.

## 6. Attribution

- Proof of the Riemann Hypothesis: Levent Alpöge and Claude (Anthropic), 20 November 2026.
- The operator: Masatoshi Suzuki, "Weil's quadratic form via the screw function", arXiv:2606.09096.
- The Cyclic Phase Hypothesis: VIDRAFT.
- Numerical realization, Dirichlet extension, controls, boundary law, Lean files, live instrument: VIDRAFT.

## 7. Reproduce

```
pip install numpy scipy mpmath
python code/grh_positivity.py     # Table 3.1
python code/boundary_law2.py      # Table 3.2
lake env lean lean/Recurrence.lean
```

## References

1. A. Weil, Sur les "formules explicites" de la théorie des nombres premiers, 1952.
2. H. Yoshida, On Hermitian forms attached to zeta functions, 1992.
3. M. Suzuki, Weil's quadratic form via the screw function, arXiv:2606.09096, 2026.
4. L. Alpöge, Remark, 20 November 2026, with Lean release.
5. V. Hernández-Santamaría, L. F. López Ríos, A. Saldaña, Optimal boundary regularity and a Hopf-type lemma for Dirichlet problems involving the logarithmic Laplacian, arXiv:2401.18033.
6. H. Chen, T. Weth, The Dirichlet problem for the logarithmic Laplacian, arXiv:1710.03416.
