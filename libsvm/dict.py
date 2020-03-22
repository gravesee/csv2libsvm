import csv
from typing import Optional, List, Union, Dict
import json
from tqdm import tqdm

Converter = Dict[str, str]


class Incrementer(dict):
    """subclass of dict that increments values returned by new keys"""
    def __init__(self, data: Dict[str, str] = {}, locked=False):
        self.locked = locked
        self.update(data)

    def __missing__(self, key):
        if self.locked:
            return 0
        self[key] = str(len(self) + 1)
        return self[key]


def line_count(infile: str, nrows: Optional[int] = None) -> int:
    """quick line count of file"""
    with open(infile, "r") as fin:
        for lc, _ in enumerate(fin):
            pass
    if nrows is not None:
        lc = min(lc, nrows)
    return lc


def make_converters(
    factors: List[str] = [], converters: Dict[str, Converter] = {}
) -> Dict[str, Incrementer]:
    """either create new converters or locked versions from saved meta.json"""
    if len(converters) == 0:
        return {k: Incrementer() for k in factors}
    else:
        return {k: Incrementer(v, True) for k, v in converters.items()}


def make_target_column(
    row: Dict[str, str],
    target: str,
    weight: Optional[str],
    factors: List[str],
    na_strings: List[str],
    convert: Dict[str, Converter],
) -> str:
    """create output str for target column"""

    if target in factors:
        val = convert[target][row[target]]
    else:
        val = row[target]

    if val in na_strings:
        raise ValueError(
            "target variable cannot be in missing_strings: (line: {i}, value: {val})."
        )

    if weight is None:
        return str(val)
    else:
        w = row[weight]
        if row[weight] in na_strings:
            w = "0"
        return f"{val}:{w}"


def csv_to_libsvm(
    infile: str,
    outfile: str,
    target: Optional[str] = None,
    weight: Optional[str] = None,
    factors: List[str] = [],
    converters: Dict[str, Converter] = {},
    skip: List[str] = [],
    na_strings=[""],
    nrows: Optional[int] = None,
    meta: Optional[str] = None,
    locked: bool = False,
    verbose: bool = True,
):
    """Convert csv files to libsvm format
    
    Arguments:
        infile {str} -- Input path to csv file
        outfile {str} -- Output path t        o libsvm file
    
    Keyword Arguments:
        target {Optional[str]} -- Column name of target variable. (default: {None})
        weight {Optional[str]} -- Column name of weight variable. (default: {None})
        factors {List[str]} -- List of columns to be converted to from character values to integers. (default: {[]})
        converters {Dict[str, Dict[str, str]]} -- Mapping from factor levels to integers. Usually not provided by the user. (default: {{}})
        skip {List[str]} -- List of columns to skip in output. (default: {[]})
        na_strings {list} -- List of values to be interpreted as missing and therefore not output. (default: {[""]})
        nrows {Optional[int]} -- Number of rows to porcess. (default: {None})
        meta {Optional[str]} -- Input path to metadata json file produced from another run. [description] (default: {None})
        locked {bool} -- If `True` only use values present in `factor_levels` to produce output. (default: {False})
    
    Raises:
        ValueError: Raised if both target and meta are not provided.
    
    Returns:
        None -- Produces two files. An `outfile` in libsvm format and `outfile.json` that records settings for future usage.
    """

    # check if meta.json was provided. If so, call function again with saved arguments.
    if meta is not None:
        with open(meta, "r") as meta_in:
            opts = json.load(meta_in)
            return csv_to_libsvm(infile, outfile, nrows=nrows, locked=True, **opts)
    else:
        if target is None:
            raise ValueError("target cannot be None if no metadata provided.")

    # if verbose=True, get a quick line count for tqdm
    if verbose:
        lc = line_count(infile, nrows)

    # create converters that will map factor column levels to integers
    convert = make_converters(factors, converters)

    with open(infile, "r") as fin, open(outfile, "w") as fout:

        reader = csv.DictReader(fin)

        for i, row in enumerate(tqdm(reader, total=lc)):
            # if target is in factors, need to replace value with incrementer

            val = make_target_column(row, target, weight, factors, na_strings, convert)
            fout.write(val)

            skipcols = [target] + skip
            if weight is not None:
                skipcols += [weight]

            pos = 1
            for k, v in row.items():
                # if column is in skipcols, skip
                if k in skipcols:
                    continue
                # don't output values that are missing or zeo
                elif v in na_strings + ["0"]:
                    pass
                else:
                    # if column is a factor, replace value with incrementer value
                    val = convert[k][v] if k in factors else v
                    fout.write(f" {pos}:{val}")
                pos += 1

            fout.write(f"\n")

            if nrows is not None:
                if i >= nrows - 1:
                    break

    if not locked:
        with open(outfile + ".json", "w") as meta_out:
            info = {
                "target": target,
                "weight": weight,
                "factors": factors,
                "converters": converters,
                "skip": skip,
                # 'keep': [x for x in reader.fieldnames if x not in skipcols],
                "na_strings": na_strings,
            }
            json.dump(info, meta_out)


if __name__ == "__main__":
    # survived,pclass,sex,age,sibsp,parch,fare,embarked,class,who,adult_male,deck,embark_town,alive,alone
    csv_to_libsvm(
        "titanic.csv",
        "titanic-libsvm.train",
        "survived",
        factors=["pclass", "sex", "embarked"],
        skip=["class", "who", "adult_male", "deck", "embark_town", "alive", "alone"],
    )

    # csv_to_libsvm(
    #     infile="C:\\Projects\\r-dev\\xgboost_neutral\\data\\pt28_mkiv1_2_2.csv",
    #     outfile="pt28_mkiv1_2_2-part2-dict.libsvm",
    #     target="CFPB_Race_Estimate",
    #     weight="bankcard_score",
    #     factors=["CFPB_Race_Estimate", "customer"],
    #     skip=["mergekey"],
    #     # nrows=1947
    # )

    # csv_to_libsvm(
    #     infile="libsvm/iris.csv",
    #     outfile="iris.libsvm",
    #     target="species",
    #     factors=["species"]
    # )

    # csv_to_libsvm(
    #     infile="C:\\Projects\\r-dev\\xgboost_neutral\\data\\pt28_mkiv1_2_2.csv",
    #     outfile="pt28_mkiv1_2_2-part2.libsvm",
    #     meta="pt28_mkiv1_2_2-part2.libsvm.json",

    # )
