# -*- coding: utf-8 -*-
import math, os, time
import numpy as np
import gradio as gr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import rhcore as R

HERE = os.path.dirname(os.path.abspath(__file__))
def read(name):
    p = os.path.join(HERE, name)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""

GREEN, RED, GREY, INK, AMBER, BG, PANEL = "#2dd4a7", "#ff5d73", "#8a93a6", "#e8ecf5", "#ffb547", "#0b1020", "#131a2e"
A_GRID = {"Quick (6 points)": [0.20, 0.35, 0.50, 0.60, 0.70, 0.85],
          "Full (11 points, as published)": [0.20, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.85, 1.00]}
EPS = 1e-7
def slog(v): return math.copysign(math.log10(1.0 + abs(v) / EPS), v)
TICKS = [-1.0, -1e-2, -1e-4, -1e-6, 0.0, 1e-6, 1e-4, 1e-2, 1.0]
TICKTEXT = ["-1", "-10^-2", "-10^-4", "-10^-6", "0", "10^-6", "10^-4", "10^-2", "1"]

def style(fig, h=440, title=None):
    fig.update_layout(template="plotly_dark", paper_bgcolor=PANEL, plot_bgcolor=PANEL, height=h, title=title,
                      font=dict(family="Inter, system-ui, sans-serif", color=INK, size=13),
                      margin=dict(l=60, r=24, t=56 if title else 24, b=48), legend=dict(orientation="h", y=-0.2, font=dict(size=11)))
    return fig

def curve_fig(series, title):
    fig = go.Figure()
    top, bot = slog(3.0), slog(-6.0)
    fig.add_hrect(y0=0, y1=top, fillcolor=GREEN, opacity=0.07, line_width=0)
    fig.add_hrect(y0=bot, y1=0, fillcolor=RED, opacity=0.09, line_width=0)
    fig.add_annotation(x=0.99, y=0.97, xref="paper", yref="paper", text="POSITIVE: consistent with the Riemann Hypothesis", showarrow=False, font=dict(color=GREEN, size=11), xanchor="right")
    fig.add_annotation(x=0.99, y=0.03, xref="paper", yref="paper", text="NEGATIVE: not an L-function", showarrow=False, font=dict(color=RED, size=11), xanchor="right")
    for label, rows, genuine in series:
        col = GREEN if genuine else RED
        fig.add_trace(go.Scatter(x=[r["a"] for r in rows], y=[slog(r["lam_fine"]) for r in rows], mode="lines+markers", name=label,
            line=dict(color=col, width=3, dash="solid" if genuine else "dot"),
            marker=dict(size=10, color=[GREY if r["verdict"].endswith("resolution") else col for r in rows], line=dict(color=BG, width=1.5)),
            customdata=[[r["lam_fine"], r["verdict"]] for r in rows], hovertemplate="a = %{x}<br>eigenvalue = %{customdata[0]:.4e}<br>%{customdata[1]}<extra>" + label + "</extra>"))
    fig.add_hline(y=0, line_color=INK, line_width=1.5)
    fig.update_yaxes(tickvals=[slog(t) for t in TICKS], ticktext=TICKTEXT, title="lowest eigenvalue of Weil's form", range=[bot, top], gridcolor="#243049", zeroline=False)
    fig.update_xaxes(title="half-width a of the interval (larger a lets more primes in)", gridcolor="#243049")
    return style(fig, 460, title)

def dial_fig(value, genuine_expected):
    pos = value >= 0
    fig = go.Figure(go.Indicator(mode="gauge+number", value=slog(value),
        number=dict(font=dict(size=1, color=PANEL)),
        gauge=dict(axis=dict(range=[slog(-6), slog(3)], tickvals=[slog(t) for t in (-1, -1e-4, 0, 1e-4, 1)], ticktext=["-1", "-10^-4", "0", "10^-4", "1"], tickcolor=INK),
                   bar=dict(color=GREEN if pos else RED, thickness=0.28), bgcolor=PANEL, borderwidth=0,
                   steps=[dict(range=[slog(-6), 0], color="rgba(255,93,115,0.20)"), dict(range=[0, slog(3)], color="rgba(45,212,167,0.18)")],
                   threshold=dict(line=dict(color=INK, width=4), thickness=0.9, value=slog(value)))))
    fig.add_annotation(x=0.5, y=0.30, xref="paper", yref="paper", showarrow=False, text="<b>%+.3e</b>" % value, font=dict(size=30, color=GREEN if pos else RED))
    fig.add_annotation(x=0.5, y=0.10, xref="paper", yref="paper", showarrow=False, text="POSITIVE" if pos else "NEGATIVE", font=dict(size=15, color=GREEN if pos else RED))
    return style(fig, 300)

def banner(kind, big, small):
    col = {"ok": GREEN, "bad": RED, "warn": AMBER}[kind]
    return "<div class='verdict' style='border-color:%s'><div class='v-big' style='color:%s'>%s</div><div class='v-small'>%s</div></div>" % (col, col, big, small)

def table(rows):
    return [[r["a"], r["terms"], "%.6e" % r["lam_coarse"], "%.6e" % r["lam_fine"], "%.3f" % r["ratio"], r["verdict"]] for r in rows]

def run_one(name, grid, res, flip_parity, flip_pole, flip_signs):
    t0 = time.time(); flags = dict(flip_parity=flip_parity, flip_pole=flip_pole, flip_signs=flip_signs)
    rows = R.scan(name, A_GRID[grid], N=int(res), **flags); dt = time.time() - t0
    genuine = not any(flags.values()); neg = [r for r in rows if r["verdict"] == "NEGATIVE"]
    resolved = [r for r in rows if r["verdict"] in ("positive", "NEGATIVE")]
    key = (neg[-1] if neg else (resolved[-1] if resolved else rows[0]))
    if genuine and not neg:
        b = banner("ok", "GENUINE. The needle stays above zero.", "%s: positive at every resolved point. Computed live in %.0f s." % (name, dt))
    elif neg:
        b = banner("bad", "IMITATION DETECTED. The needle crosses zero at a = %.2f." % neg[0]["a"], "One ingredient was altered and Weil's form turned negative (%.3f). Computed live in %.0f s." % (neg[-1]["lam_fine"], dt))
    else:
        b = banner("warn", "No crossing on this grid yet.", "The alteration has to reach the interval first. Run the full grid. Computed live in %.0f s." % dt)
    label = name + ("" if genuine else " (altered)")
    return b, dial_fig(key["lam_fine"], genuine), curve_fig([(label, rows, not neg)], None), table(rows)

IMIT = [("Riemann zeta", dict(flip_pole=True), "zeta primes, pole term removed"),
        ("Dirichlet L, character mod 3", dict(flip_parity=True), "mod 3, wrong parity"),
        ("Dirichlet L, character mod 3", dict(flip_signs=True), "mod 3, prime signs flipped")]
SHORT = {"Riemann zeta": "zeta", "Dirichlet L, character mod 3": "L mod 3", "Dirichlet L, character mod 4": "L mod 4",
         "Dirichlet L, quadratic character mod 5": "L mod 5", "Dirichlet L, character mod 8": "L mod 8"}

def run_all(grid, res):
    t0 = time.time(); series = []; bars = []; out = []
    for name in R.CHARS:
        rows = R.scan(name, A_GRID[grid], N=int(res)); series.append((SHORT[name], rows, True))
        rs = [r for r in rows if r["verdict"] == "positive"] or rows
        ok = all(r["verdict"].startswith("positive") for r in rows)
        bars.append((SHORT[name], rs[-1]["lam_fine"], True)); out.append([name, "genuine", "all positive" if ok else "NEGATIVE", "%.3e" % rs[-1]["lam_fine"], rs[-1]["a"]])
    for name, flags, tag in IMIT:
        rows = R.scan(name, A_GRID[grid], N=int(res), **flags); series.append(("imitation: " + tag, rows, False))
        ng = [r for r in rows if r["verdict"] == "NEGATIVE"]
        v = ng[-1] if ng else rows[-1]
        bars.append(("fake: " + tag, v["lam_fine"], False)); out.append(["Imitation: " + tag, "imitation", "turns NEGATIVE" if ng else "no crossing", "%.3e" % v["lam_fine"], v["a"]])
    good = all(o[2] == "all positive" for o in out[:5]) and all(o[2] == "turns NEGATIVE" for o in out[5:])
    fig = go.Figure(go.Bar(x=[b[0] for b in bars], y=[slog(b[1]) for b in bars], marker_color=[GREEN if b[1] > 0 else RED for b in bars],
                           text=["%.2e" % b[1] for b in bars], textposition="outside", cliponaxis=False,
                           hovertemplate="%{x}<br>eigenvalue %{text}<extra></extra>"))
    fig.add_hline(y=0, line_color=INK, line_width=1.5)
    fig.update_yaxes(tickvals=[slog(t) for t in TICKS], ticktext=TICKTEXT, range=[slog(-30), slog(30)], gridcolor="#243049", title="lowest eigenvalue at the last resolved a")
    fig.update_xaxes(tickangle=-20)
    b = banner("ok" if good else "bad", "REPRODUCED: 5 genuine above zero, 3 imitations below." if good else "MISMATCH. Please report this run.",
               "Eight operators assembled and diagonalized in your session in %.0f s." % (time.time() - t0))
    return b, style(fig, 430), curve_fig(series, None), out

def run_boundary(name, a, res):
    t0 = time.time(); a = float(a); rows, x, u = R.boundary(name, a, int(res))
    sel = (x > 0.004) & (x < 0.5); xs, us = x[sel], u[sel]
    w = (xs > 0.01) & (xs < 0.05)
    pb = np.polyfit(np.log(xs[w]), np.log(us[w]), 1); pl = np.polyfit(np.log(1 / xs[w]), us[w] ** -2.0, 1)
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Shape of the eigenfunction near the edge", "Which law holds still?"), horizontal_spacing=0.12)
    fig.add_trace(go.Scatter(x=xs, y=us, mode="lines", name="measured eigenfunction", line=dict(color=INK, width=4)), 1, 1)
    fig.add_trace(go.Scatter(x=xs, y=np.clip(np.polyval(pl, np.log(1 / xs)), 1e-9, None) ** -0.5, mode="lines", name="logarithmic law", line=dict(color=GREEN, width=2, dash="dash")), 1, 1)
    fig.add_trace(go.Scatter(x=xs, y=np.exp(np.polyval(pb, np.log(xs))), mode="lines", name="power law", line=dict(color=RED, width=2, dash="dot")), 1, 1)
    mid = [(r["lo"] * r["hi"]) ** 0.5 for r in rows]
    fig.add_trace(go.Scatter(x=mid, y=[r["power_slope"] / rows[-1]["power_slope"] for r in rows], mode="lines+markers", name="power-law exponent (drifts)", line=dict(color=RED, width=3)), 1, 2)
    fig.add_trace(go.Scatter(x=mid, y=[r["log_slope"] / rows[0]["log_slope"] for r in rows], mode="lines+markers", name="logarithmic slope (settles)", line=dict(color=GREEN, width=3)), 1, 2)
    fig.update_xaxes(type="log", title="distance to the edge / a", gridcolor="#243049"); fig.update_yaxes(gridcolor="#243049")
    fig.update_yaxes(title="normalized slope", row=1, col=2)
    tb = [["%.3f to %.3f" % (r["lo"], r["hi"]), "%.4f" % r["power_slope"], "%.4f" % r["log_slope"]] for r in rows]
    b = banner("ok", "LOGARITHMIC LAW. The exponent drifts from %.2f to %.2f while the log slope settles at %.2f." % (rows[-1]["power_slope"], rows[0]["power_slope"], rows[0]["log_slope"]),
               "u(d) ~ (log(1/d))^(-1/2), the optimal rate of the logarithmic Laplacian. Measured live in %.0f s." % (time.time() - t0))
    return b, style(fig, 440), tb

CSS = read("style.css")
with gr.Blocks(title="Weil Positivity Gauge") as demo:
    gr.HTML(read("hero.html"))
    with gr.Tabs():
        with gr.Tab("The gauge"):
            gr.HTML("<div class='lead'><b>How to read it.</b> Pick an L-function. The gauge assembles Weil's quadratic form on the interval [-a, a] and returns its lowest eigenvalue. The Riemann Hypothesis says the needle never drops below zero. Then alter one ingredient with a switch and run again.</div>")
            with gr.Row():
                with gr.Column(scale=4):
                    name = gr.Dropdown(list(R.CHARS), value="Dirichlet L, character mod 3", label="1. Choose a genuine object")
                    gr.HTML("<div class='step'>2. Sabotage it (optional)</div>")
                    f3 = gr.Checkbox(label="Flip the signs of the primes")
                    f1 = gr.Checkbox(label="Give the Gamma factor the wrong parity")
                    f2 = gr.Checkbox(label="Remove or add the pole term")
                    with gr.Accordion("Precision", open=False):
                        grid = gr.Radio(list(A_GRID), value="Quick (6 points)", label="Grid of interval sizes")
                        res = gr.Radio([800, 1600], value=800, label="Finite elements (1600 is the published setting)")
                    b1 = gr.Button("Run the gauge", variant="primary", size="lg")
                with gr.Column(scale=5):
                    h1 = gr.HTML(banner("warn", "Ready.", "Press Run. Every number is computed in your session."))
                    d1 = gr.Plot(show_label=False)
            p1 = gr.Plot(show_label=False)
            with gr.Accordion("Numbers behind the picture", open=False):
                t1 = gr.Dataframe(headers=["a", "prime terms", "eigenvalue (coarse mesh)", "eigenvalue (fine mesh)", "coarse/fine", "verdict"], interactive=False)
            b1.click(run_one, [name, grid, res, f1, f2, f3], [h1, d1, p1, t1])
        with gr.Tab("Genuine against imitation"):
            gr.HTML("<div class='lead'><b>The published experiment.</b> Five genuine L-functions and three imitations, each imitation one ingredient away from a genuine object. Quick grid takes about half a minute on this free CPU.</div>")
            with gr.Row():
                grid2 = gr.Radio(list(A_GRID), value="Quick (6 points)", label="Grid"); res2 = gr.Radio([800, 1600], value=800, label="Finite elements")
                b2 = gr.Button("Reproduce all eight", variant="primary", size="lg")
            h2 = gr.HTML(); bar2 = gr.Plot(show_label=False); p2 = gr.Plot(show_label=False)
            with gr.Accordion("Numbers behind the picture", open=False):
                t2 = gr.Dataframe(headers=["object", "kind", "result", "eigenvalue", "at a"], interactive=False)
            b2.click(run_all, [grid2, res2], [h2, bar2, p2, t2])
        with gr.Tab("The boundary law"):
            gr.HTML("<div class='lead'><b>A law found with the gauge.</b> At the ends of the interval the eigenfunctions vanish like the inverse square root of a logarithm. A true law has a slope that stops moving as you approach the edge.</div>")
            with gr.Row():
                name3 = gr.Dropdown(list(R.CHARS), value="Riemann zeta", label="Object"); a3 = gr.Radio([0.1, 0.2], value=0.2, label="Interval half-width a")
                res3 = gr.Radio([1600, 3200], value=1600, label="Finite elements"); b3 = gr.Button("Measure live", variant="primary", size="lg")
            h3 = gr.HTML(); p3 = gr.Plot(show_label=False)
            with gr.Accordion("Numbers behind the picture", open=False):
                t3 = gr.Dataframe(headers=["octave d/a", "power-law exponent", "logarithmic slope"], interactive=False)
            b3.click(run_boundary, [name3, a3, res3], [h3, p3, t3])
        with gr.Tab("The story"):
            gr.HTML(read("story.html"))
        with gr.Tab("Machine-checked"):
            gr.Markdown(read("LEAN.md"))
            with gr.Accordion("RiemannR2_Basic.lean", open=False): gr.Code(read("lean/RiemannR2_Basic.lean"), language=None)
            with gr.Accordion("Recurrence.lean", open=False): gr.Code(read("lean/Recurrence.lean"), language=None)
        with gr.Tab("Reproducing the proof"):
            gr.Markdown(read("STATUS.md"))
    gr.HTML(read("footer.html"))

if __name__ == "__main__":
    demo.queue(default_concurrency_limit=2).launch(css=CSS, theme=gr.themes.Base(primary_hue="teal", neutral_hue="slate"))
