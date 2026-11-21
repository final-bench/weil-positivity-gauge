# -*- coding: utf-8 -*-
"""Weil quadratic form operator (Suzuki 2026) for zeta and real Dirichlet characters.
Finite elements on [-a, a], Dirichlet boundary. Same assembly as the July 2026 VIDRAFT paper (R7)."""
import math
import numpy as np
from functools import lru_cache
from scipy.integrate import cumulative_trapezoid
from scipy.linalg import eigh
from scipy.interpolate import CubicSpline
import mpmath as mp

mp.mp.dps = 25
PI = math.pi

@lru_cache(maxsize=None)
def make_lam(nu_str):
    nu = mp.mpf(nu_str); nu_f = float(nu); ZET = mp.zeta(2, nu); TAIL = float(mp.zeta(2, mp.mpf(2000) + nu))
    lo_t = np.concatenate([[0.0], np.geomspace(1e-7, 0.01, 300)])
    lo_v = np.array([0.0 if tv == 0 else float(ZET - mp.e ** (-2 * nu * tv) * mp.lerchphi(mp.e ** (-2 * tv), 2, nu)) for tv in lo_t])
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

CHARS = {  # name: (conductor q, parity 0 even / 1 odd, values mod q, has pole)
    "Riemann zeta": (1, 0, (1,), True),
    "Dirichlet L, character mod 3": (3, 1, (0, 1, -1), False),
    "Dirichlet L, character mod 4": (4, 1, (0, 1, 0, -1), False),
    "Dirichlet L, quadratic character mod 5": (5, 0, (0, 1, -1, -1, 1), False),
    "Dirichlet L, character mod 8": (8, 0, (0, 1, 0, -1, 0, -1, 0, 1), False),
}

def screw(name, tt, a, flip_parity=False, flip_pole=False, flip_signs=False):
    """Screw function g(t) on the grid tt; the three flags turn the object into an imitation."""
    q, par, vals, pole = CHARS[name]
    if flip_parity: par = 1 - par
    if flip_pole: pole = not pole
    nu = "0.25" if par == 0 else "0.75"
    sgn = -1.0 if flip_signs else 1.0
    o = -(tt / 2.0) * (float(mp.digamma(mp.mpf(nu))) - math.log(PI / q)) - 0.25 * make_lam(nu)(tt)
    if pole: o = o - 4.0 * (np.exp(tt / 2) + np.exp(-tt / 2) - 2.0)
    n_terms = 0
    for (n, L, w) in vonmangoldt(math.exp(2 * a)):
        c = vals[n % q]
        if c != 0: o = o + sgn * c * w * np.clip(tt - L, 0, None); n_terms += 1
    return o, n_terms

def assemble(name, a, N, **flags):
    h = 2.0 * a / N; tt = np.linspace(0.0, 2.0 * a, 8 * N + 1)
    o, n_terms = screw(name, tt, a, **flags)
    G1 = cumulative_trapezoid(o, tt, initial=0.0); G2 = cumulative_trapezoid(G1, tt, initial=0.0); G2h = G2[::8]
    I = np.empty(N); I[0] = 2.0 * G2h[1]
    I[1:] = G2h[2:N + 1] - 2.0 * G2h[1:N] + G2h[0:N - 1]
    ar = np.arange(N); T = I[np.abs(ar[:, None] - ar[None, :])]
    Q = (T[:-1, :-1] - T[:-1, 1:] - T[1:, :-1] + T[1:, 1:]) / h ** 2; Q = (Q + Q.T) / 2
    M = np.zeros((N - 1, N - 1)); np.fill_diagonal(M, 4.0)
    ix = np.arange(N - 2); M[ix, ix + 1] = 1.0; M[ix + 1, ix] = 1.0; M *= h / 6.0
    return Q, M, h, n_terms

def lam1(name, a, N, **flags):
    Q, M, h, n_terms = assemble(name, a, N, **flags)
    return float(eigh(Q, M, subset_by_index=[0, 0], eigvals_only=True)[0]), n_terms

def verdict(v1, v2):
    r = v1 / v2 if abs(v2) > 1e-300 else float("nan")
    if v1 < 0 and v2 < 0 and 0.5 < r < 1.5: return r, "NEGATIVE"
    if v2 > 0 and 0.9 < r < 1.1: return r, "positive"
    if v2 > 0 and r >= 1.1: return r, "positive, below resolution"
    return r, "unresolved"

def scan(name, a_values, N=800, **flags):
    rows = []
    for a in a_values:
        v1, n = lam1(name, a, N // 2, **flags); v2, _ = lam1(name, a, N, **flags)
        r, vd = verdict(v1, v2)
        rows.append(dict(a=a, terms=n, lam_coarse=v1, lam_fine=v2, ratio=r, verdict=vd))
    return rows

def boundary(name, a, N):
    """Local slopes of the first eigenfunction toward the boundary."""
    Q, M, h, _ = assemble(name, a, N)
    w, V = eigh(Q, M, subset_by_index=[0, 0]); u = np.abs(V[:, 0]); u = u / u.max(); d = np.arange(1, N) * h
    rows = []
    for lo, hi in ((0.005, 0.01), (0.01, 0.02), (0.02, 0.04), (0.04, 0.08), (0.08, 0.16)):
        s = (d >= lo * a) & (d <= hi * a)
        if s.sum() < 6: continue
        B = float(np.polyfit(np.log(d[s]), np.log(u[s]), 1)[0])
        S = float(np.polyfit(np.log(1 / d[s]), u[s] ** -2.0, 1)[0])
        rows.append(dict(lo=lo, hi=hi, power_slope=B, log_slope=S))
    return rows, d / a, u
