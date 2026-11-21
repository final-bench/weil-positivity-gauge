# -*- coding: utf-8 -*-
"""Step 3, second pass: does the log law become exact toward the boundary?
If u ~ c (log(1/d)+K)^(-1/2) then  S(d) = d(u^-2)/d(log(1/d))  tends to a constant 1/c^2 as d -> 0.
If u ~ C d^beta then  B(d) = d(log u)/d(log d)  is the constant beta.
We print both local slopes on successive octaves approaching the boundary, for N = 1600/3200/6400, plus a Richardson
value in N. Whichever local slope stops moving is the law. Control: the Laplacian must give B = 1.
"""
import math, sys, os, time
import numpy as np
from scipy.linalg import eigh
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "boundary_law.py"), encoding="utf-8").read().split("def fits(d, u):")[0]
ns = {"__file__": os.path.join(HERE, "boundary_law.py")}; exec(compile(src, "bl", "exec"), ns)
operator, laplace = ns["operator"], ns["laplace"]

OCT = [(0.0025, 0.005), (0.005, 0.01), (0.01, 0.02), (0.02, 0.04), (0.04, 0.08), (0.08, 0.16)]
def slopes(build, a, N, k=0):
    Q, M, h = build(a, N)
    w, V = eigh(Q, M, subset_by_index=[k, k]); u = np.abs(V[:, 0]); u = u / u.max(); d = np.arange(1, N) * h
    out = []
    for lo, hi in OCT:
        s = (d >= lo * a) & (d <= hi * a)
        if s.sum() < 6: out.append((float("nan"), float("nan"))); continue
        B = np.polyfit(np.log(d[s]), np.log(u[s]), 1)[0]
        S = np.polyfit(np.log(1 / d[s]), u[s] ** -2.0, 1)[0]
        out.append((B, S))
    return out

def table(name, build, a, k=0, Ns=(1600, 3200, 6400)):
    print("\n### %s  a=%.2f mode %d" % (name, a, k + 1)); t0 = time.time()
    R = {N: slopes(build, a, N, k) for N in Ns}
    print("   %-16s" % "octave d/a" + "".join("| B N=%-5d S N=%-5d " % (N, N) for N in Ns) + "| B(Rich)  S(Rich)")
    for i, (lo, hi) in enumerate(OCT):
        row = "   [%.4f,%.4f] " % (lo, hi)
        for N in Ns: row += "| %-9.4f %-9.4f " % R[N][i]
        b1, s1 = R[Ns[-2]][i]; b2, s2 = R[Ns[-1]][i]
        row += "| %-8.4f %-8.4f" % (b2 + (b2 - b1), s2 + (s2 - s1))      # first-order extrapolation in h
        print(row)
    print("   [%.0fs]" % (time.time() - t0))

table("CONTROL -d2/dx2 (B must be 1, S must run away)", laplace, 0.2, 0, Ns=(1600, 3200))
table("Suzuki operator, zeta, prime-free", operator, 0.2, 0)
table("Suzuki operator, zeta, prime-free", operator, 0.1, 0)
print("\nBOUNDARY2_DONE")
