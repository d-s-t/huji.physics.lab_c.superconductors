import argparse
from typing import Iterable

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from scipy import optimize
from var_def import AXIS_CHOICE, AXIS_TITLE


def add_points(arr: np.ndarray, num=1) -> np.ndarray:
    for _ in range(num):
        avg_arr = ((arr + np.roll(arr, -1)) / 2.0)
        arr = np.vstack([arr, avg_arr]).flatten('F')[:-1]
    return arr


def analyze(ns: argparse.Namespace, fn: str, df: pd.DataFrame):
    mean = df.mean()
    mean = {k: mean[v] for k, v in AXIS_CHOICE.items()}
    std = df.std()
    std = {"d" + k: std[v] for k, v in AXIS_CHOICE.items()}
    fig = px.scatter(df, ns.x, ns.y, ns.z).update_layout(title=ns.title.format(**dict(mean, fn=fn, **std)) or fn)
    x = (df[[ns.x, ns.y]] if ns.z else df[ns.x]).to_numpy()
    y = (df[ns.z] if ns.z else df[ns.y]).to_numpy()
    popt, pcov = None, None
    if ns.function:
        popt, pcov = optimize.curve_fit(ns.function, x, y, maxfev=100_000, p0=ns.p0)
        print("file: ", fn)
        print("T =", mean["tmp"])
        for v in zip(popt, np.diag(pcov)):
            print("%.2g +- %.2g" % v)
        if (ns.show or ns.format) and False:
            x = np.vstack(np.meshgrid(add_points(np.array(sorted(list(set(x[:, 0])))), 1),
                                      add_points(np.array(sorted(list(set(x[:, 1])))), 1))).reshape((2, -1)).T \
                if ns.z else add_points(x, 3)
            fig.add_trace(go.Heatmap(x=x[:, 0], y=x[:, 1], z=ns.function(x, *popt)) if ns.z else
                          go.Scatter(x=x, y=ns.function(x, *popt)))

    return fig, mean, std, popt, pcov


# p0=(1e-4, 2, 5e-5, 0, 3, 5e-6)
def filter_and_calibrate(df: pd.DataFrame) -> pd.DataFrame:
    df[ns.x] -= ns.xclib
    df[ns.y] -= ns.yclib
    if ns.z:
        df[ns.z] -= ns.zclib
    if ns.s:
        df[ns.s] -= ns.sclib
    for n, v in ns.clib:
        df[AXIS_CHOICE[n]] -= float(v)
    df = df[(df[ns.x] >= ns.xmin) & (df[ns.x] <= ns.xmax) &
            (df[ns.y] >= ns.ymin) & (df[ns.y] <= ns.ymax) &
            ((df[ns.z] >= ns.zmin) & (df[ns.z] <= ns.zmax) if ns.z else True) &
            ((df[ns.s] >= ns.smin) & (df[ns.s] <= ns.smax) if ns.s else True)]
    return df.sort_values(ns.x).reset_index(drop=True)


def export_fig(fig, fn, ns):
    fig.update_yaxes(showexponent="first", exponentformat="power")
    # pio.full_figure_for_development(fig, warn=False)
    if ns.show:
        fig.show(config=dict(toImageButtonOptions=dict(filename=fn, scale=ns.scale,
                                                       width=ns.width, height=ns.height, format="pdf")))
    if ns.html:
        fig.write_html(fn + ".html")
    for form in ns.format:
        fig.write_image(fn + "." + form, scale=ns.scale, width=ns.width, height=ns.height)


def split_to_buckets(frames: Iterable[tuple[str, pd.DataFrame]], s, k):
    for fn, df in frames:
        buckets = pd.cut(df[s], min(len(set(df[s])), 20))
        df["b"] = buckets
        for bucket in set(buckets):
            d = df[df["b"] == bucket].drop("b", axis=1)
            r = f"{fn}_{d[s].mean():.2g}{k}", d
            yield r


if __name__ == '__main__':
    from analysis_argparse import ns

    frames = ((ns.name or (ns.tables[0][0] + "_CONCAT"),
               pd.concat((df for fn, df in ns.tables))),) if ns.concat else ns.tables
    if ns.s:
        frames = split_to_buckets(frames, ns.s, ns.s_key)
    # t = np.zeros(len(frames))
    # dt = np.zeros_like(t)
    # h = np.zeros_like(t)
    # dh = np.zeros_like(t)
    figs = []
    for i, (fn, df) in enumerate(frames):
        df = filter_and_calibrate(df)
        fig, mean, std, popt, pcov = analyze(ns, fn, df)
        # t[i] = mean["tmp"]
        # dt[i] = std["dtmp"]
        # h[i] = popt[3]
        # dh[i] = pcov[3, 3] ** 0.5
        fig.update_xaxes(title=AXIS_TITLE[ns.x]) \
            .update_yaxes(title=AXIS_TITLE[ns.y])
        figs.append(fig)
        if ns.vline:
            t_c = df[ns.x][np.argmax(np.diff(df[ns.y]))]
            # t_c = max(df[ns.x][df[ns.y] <= 1.1*min(df[ns.y])])
            fig.add_vline(t_c, annotation=dict(align="left", showarrow=False, xanchor='right', x=t_c - 0.01,
                                               text="$ T_{c}=" + fr"{t_c:.0f} \pm 1" + r"\left[ K \right] $"))
        fig.update_annotations(font=dict(size=20))
        export_fig(fig, fn, ns)
    if ns.hister:
        fig = go.Figure(data=tuple((d.update(dict(marker_color=c, name=n, showlegend=True)) for d, c, n in
                                    zip((d for f in figs for d in f.data), ns.color, ns.trace_name)))) \
            .update_layout(showlegend=True, legend=dict(xanchor="left", x=0.05, yanchor="top", y=1 - 0.05)) \
            .update_xaxes(title=AXIS_TITLE[ns.x]) \
            .update_yaxes(title=AXIS_TITLE[ns.y])
        export_fig(fig, ns.name or (ns.tables[0][0] + "_hister"), ns)
    # fig = go.Figure(go.Scatter(y=h, x=t, error_x=dict(array=dt), mode="markers", showlegend=False)) \
    #     .update_xaxes(title=AXIS_TITLE[AXIS_CHOICE["tmp"]]) \
    #     .update_yaxes(title=AXIS_TITLE["H"])
    # export_fig(fig, ns.name, ns)
    # export_fig(fig, ns.name, ns)
