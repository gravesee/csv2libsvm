import csv
from typing import Optional, List, Union, Dict, Iterator, Tuple, TextIO, Mapping
import json
from tqdm import tqdm
import os
import io
from .util import line_count, Incrementer


class OutputFileManager(dict):
    def __init__(self, path: str):
        self.path = path

    def __missing__(self, key):
        f = open(f"{self.path}/part-{key}.libsvm", "w")
        self[key] = f
        return self[key]


def init_input(infile: Union[str, TextIO], nrows: Optional[int]) -> Tuple[TextIO, int]:
    if isinstance(infile, str):
        fin = open(infile, "r")
        lc = line_count(infile, nrows)
    elif isinstance(infile, io.StringIO):
        fin = infile
        lc = len(list(fin))
        fin.seek(0)
    else:
        raise ValueError(f"Invalid argument provided for `infile`: {infile}.")

    return fin, lc


def make_converters(
    factors: List[str] = [], converters: Dict[str, Dict[str, str]] = {}
) -> Dict[str, Incrementer]:
    """either create new converters or locked versions from saved meta.json"""
    if len(converters) == 0:
        return {k: Incrementer() for k in factors}
    else:
        return {k: Incrementer(v, True) for k, v in converters.items()}


def make_keepcols(
    target: str,
    weight: Optional[str],
    split: Optional[str],
    skip: List[str],
    keep: List[str],
    reader: csv.DictReader,
) -> List[str]:

    skipcols = skip + [target]

    if weight is not None:
        skipcols.append(weight)
    if split is not None:
        skipcols.append(split)

    keepcols = keep if len(keep) > 0 else reader.fieldnames

    return [k for k in keepcols if k not in skipcols]


def make_target_column(
    row: Dict[str, str],
    target: str,
    weight: Optional[str],
    factors: List[str],
    na_strings: List[str],
    converters: Mapping[str, Dict[str, str]],
) -> str:
    """create output str for target column"""

    if row[target] in na_strings:
        raise ValueError(
            "target value cannot be in missing_strings: (lineno: {i}, value: {val})."
        )

    val = converters[target][row[target]] if target in factors else row[target]

    if weight is None:
        return str(val)
    else:
        return f"{val}:{'0' if row[weight] in na_strings else row[weight]}"


def csv2libsvm(
    infile: Union[str, TextIO],
    outpath: str,
    target: Optional[str] = None,
    weight: Optional[str] = None,
    split: Optional[str] = None,
    factors: List[str] = [],
    skip: List[str] = [],
    keep: List[str] = [],
    na_strings=[""],
    nrows: Optional[int] = None,
    meta: Optional[str] = None,
    _locked: bool = False,
    _converters: Dict[str, Dict[str, str]] = {},
):
    # check if meta.json was provided. If so, call function again with saved arguments.
    if meta is not None:
        with open(meta, "r") as meta_in:
            opts = json.load(meta_in)
            return csv2libsvm(infile, outpath, nrows=nrows, _locked=True, **opts)
    else:
        if target is None:
            raise ValueError("target cannot be None if no metadata provided.")

    if not os.path.exists(outpath):
        os.mkdir(outpath)

    # input output file initialization
    fin, lc = init_input(infile, nrows)
    fm = OutputFileManager(outpath)

    # create converters that will map factor column levels to integers
    converters = make_converters(factors, _converters)

    reader = csv.DictReader(fin)

    # list of columns to skip
    keepcols = make_keepcols(target, weight, split, skip, keep, reader)

    for i, row in enumerate(tqdm(reader, total=lc)):
        # if target is in factors, need to replace value with incrementer

        out = make_target_column(row, target, weight, factors, na_strings, converters)

        pos = 1
        for k in keepcols:
            v = row[k]

            # don't output values that are missing or zero
            if v in na_strings + ["0"]:
                pass
            else:
                # if column is a factor, replace value with incrementer value
                val = converters[k][v] if k in factors else v
                out += f" {pos}:{val}"
            pos += 1

        out += f"\n"

        if split is None:
            fm["full"].write(out)
        else:
            fm[row[split]].write(out)

        if nrows is not None:
            if i >= nrows - 1:
                break

    fin.close()

    for f in fm.values():
        f.close()

    if not _locked:
        with open(outpath + "/meta.json", "w") as meta_out:
            info = {
                "target": target,
                "weight": weight,
                "factors": factors,
                "_converters": converters,
                "skip": skip,
                "keep": keepcols,
                "na_strings": na_strings,
            }
            json.dump(info, meta_out)


# if __name__ == "__main__":
#     # survived,pclass,sex,age,sibsp,parch,fare,embarked,class,who,adult_male,deck,embark_town,alive,alone
#     csv_to_libsvm(
#         "titanic.csv",
#         "titanic",
#         "survived",
#         factors=["pclass" "embarked"],
#         # split="sex",
#         skip=["class", "who", "adult_male", "deck", "embark_town", "alive", "alone"],
#     )

#     csv_to_libsvm("titanic.csv", "output_from_meta", meta="titanic/meta.json")
