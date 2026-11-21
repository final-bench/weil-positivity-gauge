# -*- coding: utf-8 -*-
"""Step 3: boundary law of the eigenfunctions. Two competing models near the endpoint (d = distance to boundary):
   POWER : u ~ C d^beta                      => log u is linear in log d
   LOG   : u ~ c (log(1/d) + K)^(-1/2)       => u^(-2) is linear in log(1/d)     (logarithmic-Laplacian type)
Test: fit both on the same window, compare residuals, and check stability of the fitted parameters when the
window moves toward the boundary and when N doubles. A true law gives window-independent parameters.
Control: the same pipeline on -d^2/dx^2 (exact u = sin, beta = 1) must return POWER with beta = 1.
"""
import math, sys
import numpy as np
from scipy.linalg import eigh
sys.stdout.reconfigure(encoding="utf-8")
sys.argv = [sys.argv[0]]
import importlib.util, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "grh_positivity.py"), encoding="utf-8").read().split("one = lambda n: 1")[0]
ns = {}; exec(compile(src, "core", "exec"), ns)
make_lam, vonmangoldt, mp, cumulative_trapezoid = ns["make_lam"], ns["vonmangoldt"], ns["mp"], ns["cumulative_trapezoid"]
PI = math.pi

def operator(a, N, nu=mp.mpf(1) / 4, q=1, pole=True):
    lamf = make_lam(nu); PSI = float(mp.digamma(nu))
    h = 2.0 * a / N; tt = np.linspace(0.0, 2.0 * a, 8 * N + 1)
    o = -(tt / 2.0) * (PSI - math.log(PI / q)) - 0.25 * lamf(tt)
    if pole: o = o - 4.0 * (np.exp(tt / 2) + np.exp(-tt / 2) - 2.0)
    G1 = cumulative_trapezoid(o, tt, initial=0.0); G2 = cumulative_trapezoid(G1, tt, initial=0.0); G2h = G2[::8]
    I = np.empty(N); I[0] = 2.0 * G2h[1]
    for d in range(1, N): I[d] = G2h[d + 1] - 2.0 * G2h[d] + G2h[d - 1]
    ar = np.arange(N); T = I[np.abs(ar[:, None] - ar[None, :])]
    Q = (T[:-1, :-1] - T[:-1, 1:] - T[1:, :-1] + T[1:, 1:]) / h ** 2; Q = (Q + Q.T) / 2
    M = np.zeros((N - 1, N - 1)); np.fill_diagonal(M, 4.0)
    ix = np.arange(N - 2); M[ix, ix + 1] = 1.0; M[ix + 1, ix] = 1.0; M *= h / 6.0
    return Q, M, h

def laplace(a, N):
    h = 2.0 * a / N
    Q = np.zeros((N - 1, N - 1)); np.fill_diagonal(Q, 2.0); ix = np.arange(N - 2); Q[ix, ix + 1] = -1; Q[ix + 1, ix] = -1; Q /= h
    M = np.zeros((N - 1, N - 1)); np.fill_diagonal(M, 4.0); M[ix, ix + 1] = 1.0; M[ix + 1, ix] = 1.0; M *= h / 6.0
    return Q, M, h

def fits(d, u):
    x1, y1 = np.log(d), np.log(u); c1 = np.polyfit(x1, y1, 1); r1 = y1 - np.polyval(c1, x1)
    x2, y2 = np.log(1 / d), u ** -2.0; c2 = np.polyfit(x2, y2, 1); r2 = y2 - np.polyval(c2, x2)
    # compare on the same scale: relative error of u itself
    u1 = np.exp(np.polyval(c1, x1)); u2 = np.polyval(c2, x2) ** -0.5
    return c1[0], float(np.sqrt(np.mean((u1 / u - 1) ** 2))), c2[0], c2[1] / c2[0], float(np.sqrt(np.mean((u2 / u - 1) ** 2)))

def run(name, build, a, k=0):
    print("\n### %s   a=%.2f  mode k=%d" % (name, a, k + 1))
    print("   %-6s %-16s | %-9s %-10s | %-10s %-9s %-10s" % ("N", "window d/a", "beta", "rel.err", "slope", "K", "rel.err"))
    for N in (1600, 3200):
        Q, M, h = build(a, N)
        w, V = eigh(Q, M, subset_by_index=[k, k]); u = np.abs(V[:, 0]); u = u / u.max()
        d = (np.arange(1, N)) * h
        for lo, hi in ((8, 40), (20, 100), (50, 250)):       # windows in units of h*(N/1600): same physical window for both N
            s = N // 1600; sel = slice(lo * s - 1, hi * s)
            b, e1, sl, K, e2 = fits(d[sel], u[sel])
            print("   %-6d [%.4f,%.4f] | %-9.4f %-10.2e | %-10.4f %-9.3f %-10.2e  %s" %
                  (N, d[sel][0] / a, d[sel][-1] / a, b, e1, sl, K, e2, "LOG better" if e2 < e1 else "POWER better"))

a = 0.2
run("CONTROL  -d2/dx2 (exact sine, beta must be 1)", laplace, a)
run("Suzuki operator, zeta, prime-free", operator, a, 0)
run("Suzuki operator, zeta, prime-free", operator, a, 2)
run("Suzuki operator, zeta, prime-free", operator, 0.1, 0)
print("\nBOUNDARY_DONE")
