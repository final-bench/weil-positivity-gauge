# -*- coding: utf-8 -*-
"""Step 4: lowest eigenvalue lambda_1(a) of the Weil quadratic form operator for Dirichlet L-functions.
Same assembly as decay_law.py (zeta), generalized:
   g(t) = POLE(t) - (t/2)(psi(nu) - log(pi/q)) - (1/4) Lambda^{(nu)}(t) + sum_n chi(n) Lambda(n)/sqrt(n) (t - log n)_+
   POLE(t) = -4(e^{t/2}+e^{-t/2}-2) for zeta only (L(s,chi) has no pole).  nu = 1/4 (even chi), 3/4 (odd chi).
The form for chi is written by analogy with the explicit formula; controls C1-C3 are deliberately wrong objects.
Diagnostic (as in the paper, R7): ratio lam1(N=800)/lam1(N=1600) ~ 1 => converged, genuinely positive; ~4 => below resolution.
"""
import math, sys, time, json
import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.linalg import eigh
from scipy.interpolate import CubicSpline
import mpmath as mp
sys.stdout.reconfigure(encoding="utf-8")
mp.mp.dps = 25
PI = math.pi

def make_lam(nu):
    nu_f = float(nu); ZET = mp.zeta(2, mp.mpf(nu)); TAIL = float(mp.zeta(2, mp.mpf(2000) + mp.mpf(nu)))
    lo_t = np.concatenate([[0.0], np.geomspace(1e-7, 0.01, 300)])
    lo_v = np.array([0.0 if tv == 0 else float(ZET - mp.e ** (-2 * mp.mpf(nu) * tv) * mp.lerchphi(mp.e ** (-2 * tv), 2, mp.mpf(nu))) for tv in lo_t])
    spl = CubicSpline(lo_t, lo_v)
    def lam(t):
        t = np.asarray(t, float); out = np.empty_like(t); hi = t >= 0.01
        if hi.any():
            acc = np.zeros(int(hi.sum()))
            for k0 in range(0, 2000, 200):
                k = np.arange(k0, k0 + 200)[:, None] + nu_f
                acc += ((1.0 - np.exp(-2.0 * t[hi][None, :] * k)) / k ** 2).sum(0)
            out[hi] = acc + TAIL
        if (~hi).any(): out[~hi] = spl(t[~hi])
        return out
    return lam

def vonmangoldt(nmax):
    out = []
    for pk in range(2, int(nmax) + 1):
        m = pk; b = 0
        for q in range(2, int(pk ** 0.5) + 1):
            if m % q == 0:
                while m % q == 0: m //= q
                b = q if m == 1 else -1; break
        else: b = pk
        if b > 0: out.append((pk, math.log(pk), math.log(b) / math.sqrt(pk)))
    return out

def lam1(a, N, nu, q, chi, pole, lamf):
    PSI = float(mp.digamma(mp.mpf(nu)))
    VM = [(L, w * chi(n)) for (n, L, w) in vonmangoldt(math.exp(2 * a)) if chi(n) != 0]
    h = 2.0 * a / N; tt = np.linspace(0.0, 2.0 * a, 8 * N + 1)
    o = -(tt / 2.0) * (PSI - math.log(PI / q)) - 0.25 * lamf(tt)
    if pole: o = o - 4.0 * (np.exp(tt / 2) + np.exp(-tt / 2) - 2.0)
    for (L, w) in VM: o = o + w * np.clip(tt - L, 0, None)
    G1 = cumulative_trapezoid(o, tt, initial=0.0); G2 = cumulative_trapezoid(G1, tt, initial=0.0); G2h = G2[::8]
    I = np.empty(N); I[0] = 2.0 * G2h[1]
    for d in range(1, N): I[d] = G2h[d + 1] - 2.0 * G2h[d] + G2h[d - 1]
    ar = np.arange(N); T = I[np.abs(ar[:, None] - ar[None, :])]
    Q = (T[:-1, :-1] - T[:-1, 1:] - T[1:, :-1] + T[1:, 1:]) / h ** 2; Q = (Q + Q.T) / 2
    M = np.zeros((N - 1, N - 1)); np.fill_diagonal(M, 4.0)
    ix = np.arange(N - 2); M[ix, ix + 1] = 1.0; M[ix + 1, ix] = 1.0; M *= h / 6.0
    return eigh(Q, M, subset_by_index=[0, 0], eigvals_only=True)[0], len(VM)

one = lambda n: 1
chi3 = lambda n: (0, 1, -1)[n % 3]
chi4 = lambda n: (0, 1, 0, -1)[n % 4]
chi5 = lambda n: (0, 1, -1, -1, 1)[n % 5]
chi8 = lambda n: (0, 1, 0, -1, 0, -1, 0, 1)[n % 8]
Q14, Q34 = mp.mpf(1) / 4, mp.mpf(3) / 4
CASES = [  # label, nu, q, chi, pole, kind
    ("zeta (reference, reproduces R7)", Q14, 1, one, True, "L"),
    ("chi mod 3 (odd)", Q34, 3, chi3, False, "L"),
    ("chi mod 4 (odd)", Q34, 4, chi4, False, "L"),
    ("chi mod 5 quadratic (even)", Q14, 5, chi5, False, "L"),
    ("chi mod 8 (even)", Q14, 8, chi8, False, "L"),
    ("C1 control: zeta primes, pole term removed", Q14, 1, one, False, "CONTROL"),
    ("C2 control: chi mod 3 with wrong parity nu=1/4", Q14, 3, chi3, False, "CONTROL"),
    ("C3 control: chi mod 3 with prime signs flipped", Q34, 3, lambda n: -chi3(n), False, "CONTROL"),
]
AS = [0.20, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.85, 1.00]
lamc = {Q14: make_lam(Q14), Q34: make_lam(Q34)}
res = []; t0 = time.time()
for label, nu, q, chi, pole, kind in CASES:
    print("\n### %s   [nu=%s q=%d pole=%s]" % (label, mp.nstr(nu, 3), q, pole))
    print("   %-6s %-4s %-18s %-18s %-8s %s" % ("a", "#n", "lam1(N=800)", "lam1(N=1600)", "ratio", "verdict"))
    for a in AS:
        v1, n1 = lam1(a, 800, nu, q, chi, pole, lamc[nu]); v2, _ = lam1(a, 1600, nu, q, chi, pole, lamc[nu])
        rat = v1 / v2 if abs(v2) > 1e-300 else float("nan")
        if v2 < 0 and v1 < 0 and 0.5 < rat < 1.5: verdict = "NEGATIVE (converged)"
        elif v2 > 0 and 0.9 < rat < 1.1: verdict = "positive (converged)"
        elif v2 > 0 and rat >= 1.1: verdict = "below resolution"
        else: verdict = "unresolved"
        print("   %-6.2f %-4d %-+18.10e %-+18.10e %-8.3f %s" % (a, n1, v1, v2, rat, verdict))
        res.append(dict(case=label, kind=kind, a=a, n_terms=n1, lam800=float(v1), lam1600=float(v2), ratio=float(rat), verdict=verdict))
json.dump(res, open(__file__.replace(".py", "_results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("\n[%.0fs] GRH_POSITIVITY_DONE" % (time.time() - t0))
