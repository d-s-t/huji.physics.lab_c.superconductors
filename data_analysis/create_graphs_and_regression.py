import argparse
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from scipy import optimize
from var_def import AXIS_CHOICE, AXIS_TITLE


def analyze(ns: argparse.Namespace, fn: str, df: pd.DataFrame):
    mean = df.mean()
    mean = {k: mean[v] for k, v in AXIS_CHOICE.items()}
    std = df.std()
    std = {"d" + k: std[v] for k, v in AXIS_CHOICE.items()}
    fig = px.scatter(df, ns.x, ns.y, ns.z).update_layout(title=ns.title.format(**dict(mean, **std)) or fn)
    x = df[[ns.x, ns.y]] if ns.z else df[ns.x]
    y = df[ns.z] if ns.z else df[ns.y]
    popt, pcov = None, None
    if ns.function:
        popt, pcov = optimize.curve_fit(ns.function, x, y, maxfev=100_000, p0=(1e-4, 2, 5e-5, 0, 3, 5e-6))
        fig.add_trace(go.Scatter(x=x, y=ns.function(x, *popt)))

    return fig, mean, std, popt, pcov


def filter_and_calibrate(df: pd.DataFrame) -> pd.DataFrame:
    df[ns.x] -= ns.xclib
    df[ns.y] -= ns.yclib
    if ns.z:
        df[ns.z] -= ns.zclib
    df = df[(df[ns.x] >= ns.xmin) & (df[ns.x] <= ns.xmax) &
            (df[ns.y] >= ns.ymin) & (df[ns.y] <= ns.ymax) &
            ((df[ns.z] >= ns.zmin) & (df[ns.z] <= ns.zmax) if ns.z else True)]
    return df.sort_values(ns.x).reset_index(drop=True)


def export_fig(fig, fn, ns):
    fig.update_yaxes(showexponent="first", exponentformat="power", minexponent=1)
    pio.full_figure_for_development(fig, warn=False)
    if ns.html:
        fig.write_html(fn + ".html")
    for form in ns.format:
        fig.write_image(fn + "." + form, scale=ns.scale, width=ns.width, height=ns.height)


if __name__ == '__main__':
    from analysis_argparse import ns

    frames = ((ns.name or (ns.tables[0][0] + "_CONCAT"),
               pd.concat((df for fn, df in ns.tables))),) if ns.concat else ns.tables
    # t = np.zeros(len(ns.tables))
    # dt = np.zeros_like(t)
    # h = np.zeros_like(t)
    # dh = np.zeros_like(t)
    figs = []
    for fn, df in frames:
        df = filter_and_calibrate(df)
        fig, mean, std, popt, pcov = analyze(ns, fn, df)
        if not ns.hister:
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

    # x = np.linspace(x_min, popt[2])
    # np.append(x, x_max)
    # t[i] = np.mean(tmp)
    # dt[i] = np.std(tmp)
    # h[i] = popt[4]
    # dh[i] = pcov[4, 4]**0.5
