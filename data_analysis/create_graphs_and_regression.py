import argparse
import numpy as np
import pandas as pd
import scipy.constants as const
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from glob import glob
from typing import Any, Sequence
from scipy import optimize

AXIS_CHOICE = {"tmp": "Temperature(K)",
               "sv": "SampVolt(V)",
               "sc": "SampCurr(A)",
               "cc": "CoilCurr(A)",
               "h": "H"}

AXIS_TITLE = {"Temperature(K)": r"$ \text{Temperature} \left[ K \right] $",
              "SampVolt(V)": r"$ \text{Sample Voltage} \left[ V \right] $",
              "SampCurr(A)": r"$ \text{Sample Current} \left[ A \right] $",
              "CoilCurr(A)": r"$ \text{Coil Current} \left[ A \right] $",
              "H": r"$ \text{Applied Magnetic Field} \left[ G \right] $"}


def exp(x, y0, k, b, phi):
    return y0 * np.exp(k * x + phi) + b


def line(x, m, b):
    return x * m + b


def exp_heavy_line(x, y0, k, b0, phi, x0, m):
    return np.where(x < x0, exp(x, y0, k, b0, phi), line(x - x0, m, exp(x0, y0, k, b0, phi)))


FUNCTIONAL_RELATION = {"exp": exp, "line": line, "exp_heavy_line": exp_heavy_line}


def get_H_func():
    df = pd.read_csv("../measurement_data/H_vs_CC.csv")
    popt, pcov = optimize.curve_fit(line, df[AXIS_CHOICE["cc"]], df[AXIS_CHOICE["h"]])
    return lambda cc: cc * popt[0]


H = get_H_func()


class ExtendAction(argparse.Action):
    def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
                 values: Sequence[Any], option_string: str | None = ...) -> None:
        old: list[Any] = getattr(namespace, self.dest)
        if old:
            old.extend(values)
        else:
            setattr(namespace, self.dest, list(values))


class DictAction(argparse.Action):
    def __init__(self, choices: dict[Any, Any] = None, **kwargs):
        if not isinstance(choices, dict):
            raise ValueError("with DictAction _choice_ mast be a dict.")
        self.choices: dict[Any, Any] = choices
        super().__init__(choices=choices, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.choices.get(values))
        setattr(namespace, self.dest + "_key", values)


def file_type(s: str) -> list[tuple[str, pd.DataFrame | Any]]:
    return [(fn[:-4], pd.read_csv(fn).assign(H=lambda x: H(x[AXIS_CHOICE["cc"]]))) for fn in glob(s)]


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='dataView',
        description='This program will generate graphs with regression line.')

    parser.add_argument("-f", action=ExtendAction, type=file_type, required=True, dest="tables",
                        help="csv file path. may contain wildcards.")
    parser.add_argument("-c", action="append", type=str, required=False, dest="color",
                        help="color of the dots in the graph.")
    parser.add_argument("--trace_name", action="append", type=str, required=False,
                        help="name for the trace in the legend.")

    parser.add_argument("-x", action=DictAction, required=True, choices=AXIS_CHOICE,
                        help="the x axis argument")
    parser.add_argument("-y", action=DictAction, required=True, choices=AXIS_CHOICE,
                        help="the y axis argument")
    parser.add_argument("-z", action=DictAction, required=False, choices=AXIS_CHOICE,
                        help="the z axis argument. if set, that output will be heatmap.")

    g = parser.add_mutually_exclusive_group()
    g.add_argument("--concat", action="store_true", help="concat all the tables.")
    g.add_argument("--hister", action="store_true", help="show all the data on the same fig.")

    parser.add_argument("--xmax", action="store", required=False, type=float, default=np.inf,
                        help="max value for x axis")
    parser.add_argument("--xmin", action="store", required=False, type=float, default=-np.inf,
                        help="min value for x axis")
    parser.add_argument("--xclib", action="store", required=False, type=float, default=0,
                        help="calibration for x axis")
    parser.add_argument("--ymax", action="store", required=False, type=float, default=np.inf,
                        help="max value for y axis")
    parser.add_argument("--ymin", action="store", required=False, type=float, default=-np.inf,
                        help="min value for y axis")
    parser.add_argument("--yclib", action="store", required=False, type=float, default=0,
                        help="calibration for y axis")
    parser.add_argument("--zmax", action="store", required=False, type=float, default=np.inf,
                        help="max value for z axis")
    parser.add_argument("--zmin", action="store", required=False, type=float, default=-np.inf,
                        help="min value for z axis")
    parser.add_argument("--zclib", action="store", required=False, type=float, default=0,
                        help="calibration for z axis")

    parser.add_argument("--function", action=DictAction, choices=FUNCTIONAL_RELATION, default=None,
                        help="the function to use in curve_fit", required=False)

    parser.add_argument("-t", "--title", action="store", required=False, default="",
                        help="Title for the figure.")

    parser.add_argument("--height", action="store", default=None, type=int,
                        help="define the height of the figure output.")
    parser.add_argument("--width", action="store", default=None, type=int,
                        help="define the width of the figure output.")
    parser.add_argument("--scale", action="store", default=None, type=float,
                        help="define the scale of the figure output.")
    parser.add_argument("--name", action="store", default=None, type=str,
                        help="the name to save the figure in.")

    parser.add_argument("--show", action="store_true", help="show the figures in the browser.")
    parser.add_argument("--html", action="store_true", help="save the figure to html file.")
    parser.add_argument("--vline", action="store_true", help="add vertical line in the max diff.")
    parser.add_argument("--format", action="append", choices=("svg", 'png', 'jpeg', 'webp', 'pdf', 'eps'),
                        default=["svg"],
                        type=str, help="The format to save the figures in.")

    return parser.parse_args()


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
    ns = get_args()
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
