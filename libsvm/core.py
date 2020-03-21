from typing import List, Optional, Set, Dict, DefaultDict, Iterable
from collections import defaultdict
import pandas as pd
import json
import re
from json import JSONEncoder
import numpy as np
import seaborn as sns
import pprint

MAX_UNIQ = 32

def match(x, table):
    res = np.full_like(table, 0)
    f = pd.isna(table)
    
    if np.all(f):
        return res
    else:
        res[~f] = np.nonzero(x == table[~f, None])[1]
        return res    

class Spec(JSONEncoder):
    def __init__(self, dtype=None, values=None, **kwargs):
        super().__init__(**kwargs)

        if dtype is None:
            dtype: np.dtype = np.dtype("bool")
        if values is None:
            values: Set[str] = set()

        self.dtype = dtype
        self.values = values

    def __add__(self, other):
        self.dtype = max(self.dtype, other.dtype)
        self.values.update(other.values)
        return self

    def __eq__(self, other):
        return (self.dtype == other.dtype) & (self.values == other.values)

    @property
    def is_object(self):
        return self.dtype == np.dtype("O")

    def default(self, o):
        if isinstance(o, Spec):
            return {"dtype": o.dtype.char, "values": list(o.values)}
        else:
            super().default(o)

    @staticmethod
    def object_hook(obj):
        if "dtype" in obj:
            obj["dtype"] = np.dtype(obj["dtype"])
        if "values" in obj:
            obj["values"] = set(obj["values"])
            return Spec(**obj)
        return obj

    def __str__(self):
        return str({"dtype": self.dtype, "values": list(self.values)})

    def __repr__(self):
        return str(self)


def get_conversion_dict(chunker: Iterable[pd.DataFrame]) -> DefaultDict[str, Spec]:
    """collect information about columns keeping track over different chunks"""
    dtypes: DefaultDict[str, Spec] = defaultdict(Spec)

    for chunk in chunker:

        for k, v in chunk.iteritems():
            if isinstance(v.dtype, pd.CategoricalDtype):
                v = v.astype(str)

            if v.dtype == "O":
                uniq = {x for x in v.unique() if x is not np.nan}
                if len(uniq) > MAX_UNIQ:
                    continue
                dtypes[k] += Spec(v.dtype, uniq)
            else:
                dtypes[k] += Spec(v.dtype, set())
    return dtypes


def infer_dtypes_from_csv(file, chunksize, **kwargs) -> DefaultDict[str, Spec]:
    """use pandas to iterate over file in chunks and create conversion dict"""
    chunker = pd.read_csv(file, chunksize=chunksize, **kwargs)
    if chunksize is None:
        chunker = [chunker]
    return get_conversion_dict(chunker)


def apply_dtypes(data: pd.DataFrame, dtypes: Dict[str, Spec]):
    for k, v in dtypes.items():
        if v.is_object:
            data[k] = match(np.array(list(v.values)), data[k].values) + 1
        else:
            data[k] = data[k].astype(v.dtype).fillna(0)

    return data


def csv_to_libsvm(
    infile: str,
    outfile: str,
    target: str,
    weight: Optional[str] = None,
    chunksize: Optional[int] = None,
    dtypes_path: Optional[str] = None,
    **kwargs,
) -> None:
    """write csv file and the dtypes conversion meta data"""
    if dtypes_path is None:
        dtypes = infer_dtypes_from_csv(infile, chunksize, **kwargs)
        with open(outfile + ".meta", "w") as meta:
            json.dump(dtypes, meta, cls=Spec)
    else:
        with open(dtypes_path, "r") as json_in:
            dtypes = json.load(json_in, object_hook=Spec.object_hook)
    
    pprint.pprint(dtypes)

    # chunk over the file and write it out
    chunker = pd.read_csv(infile, chunksize=chunksize, **kwargs)
    if chunksize is None:
        chunker = [chunker]

    with open(outfile, "w") as libsvm:

        for chunk in chunker:
            converted = apply_dtypes(chunk, dtypes)

            # target field is the first column
            if weight is not None:
                cols = [pd.Series([f"{y:g}:{w:g}" for y, w in zip(converted[target], converted[weight])])]
            else:
                cols = [converted[target].astype(str)]

            for i, (k, v) in enumerate(dtypes.items()):
                fmt = [f"{i + 1}:{x:g}" if x != 0 else "" for x in converted[k].values]
                cols.append(fmt)

            libsvm.writelines(
                [re.sub("\\s+", " ", " ".join(x)) + "\n" for x in zip(*cols)]
            )


def iter_chunks(x: pd.DataFrame, chunk_size: int = None):
    """return generator that chunks over dataframe in requested chunk size"""
    if chunk_size is None:
        yield x
    else:
        i = 0
        while True:
            if i > x.shape[0]:
                break
            idx = slice(i, (i + chunk_size))
            yield x.iloc[idx, :]
            i += chunk_size


if __name__ == "__main__":
    ## test chunking and finding dtypes
    # types = get_conversion_dict(iter_chunks(df, -1))
    # print(infer_dtypes_from_csv("libsvm/iris.csv", 10))

    # csv_to_libsvm("libsvm/iris.csv", "a.libsvm", "species", None)
    # csv_to_libsvm(
    #     "C:\\Users\\gravesee\\AppData\\Local\\Temp\\000750fe-c488-4c27-bb1b-8309c976b0b5\\titanic.csv",
    #     "titanic1.libsvm",
    #     "survived",
    #     None,
    # )

    csv_to_libsvm(
        "C:\\Projects\\r-dev\\xgboost_neutral\\data\\pt28_mkiv1_2_2.csv",
        "pt28_mkiv1_2_2.libsvm",
        "CFPB_Race_Estimate",
        "bankcard_score",
        50000,
        nrows=100000

    )