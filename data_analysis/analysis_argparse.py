import argparse
import pandas as pd
from glob import glob
from var_def import *
from scipy import optimize
from typing import Any, Sequence


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

ns = parser.parse_args()
