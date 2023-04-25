from glob import glob
import argparse
import pandas as pd
from typing import Any, Sequence


def get_args() -> argparse.Namespace:
    def file_type(s):
        return [pd.read_csv(fn) for fn in glob(s)]

    class ExtendAction(argparse.Action):
        # def __init__(self, *args, **kwargs):
        #     """
        #     argparse custom action.
        #     :param check_func: callable to do the real check.
        #     """
        #     super(ExterndAction, self).__init__(*args, **kwargs)

        def __call__(self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
                     values: str | Sequence[Any] | None, option_string: str | None = ...) -> None:
            (getattr(namespace, self.dest) or setattr(namespace, self.dest, []) or getattr(namespace, self.dest))\
                .extend(values)

    parser = argparse.ArgumentParser(
        prog='dataView',
        description='This program will generate graphs with regression line.')

    parser.add_argument("-f", "--files", action=ExtendAction, type=file_type, required=True)

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    pass
