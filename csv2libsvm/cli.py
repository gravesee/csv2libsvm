from csv2libsvm import csv2libsvm
from optparse import OptionParser, OptionValueError, Option
import copy


def check_csv_str(option, opt, value):
    try:
        return value.split(",")
    except ValueError:
        raise OptionValueError("option %s: invalid csv list value: %s" % (opt, value))


class MyOption(Option):
    TYPES = Option.TYPES + ("csvlist",)
    TYPE_CHECKER = copy.copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["csvlist"] = check_csv_str


parser = OptionParser(option_class=MyOption)  # type: ignore
parser.add_option("-i", "--infile", dest="infile", help="input file name")
parser.add_option(
    "-o", "--outpath", dest="outpath", help="path to directory for output"
)
parser.add_option(
    "-t", "--target", dest="target", help="string name of target variable"
)
parser.add_option(
    "-w", "--weight", dest="weight", help="string name of weight variable"
)
parser.add_option(
    "-z", "--split", dest="split", help="string name of variable with dev/val, etc..."
)
parser.add_option(
    "-f",
    "--factors",
    type="csvlist",
    dest="factors",
    default=[],
    help="csv list of strings indicating factor columns",
)
parser.add_option(
    "-s",
    "--skip",
    type="csvlist",
    dest="skip",
    default=[],
    help="csv list of string names to skip",
)
parser.add_option(
    "-k",
    "--keep",
    type="csvlist",
    dest="keep",
    default=[],
    help="csv list of string names to keep",
)
parser.add_option(
    "-n",
    "--na_strings",
    type="csvlist",
    dest="na_strings",
    default=[""],
    help="csv list of strings representing NULL values",
)
parser.add_option(
    "-N",
    "--nrows",
    type="int",
    dest="nrows",
    help="number of input file rows to process",
)
parser.add_option(
    "-m", "--meta", dest="meta", help="path to saved meta.json file from previous run"
)


def main():
    (options, args) = parser.parse_args()
    csv2libsvm(
        infile=options.infile,
        outpath=options.outpath,
        target=options.target,
        weight=options.weight,
        split=options.split,
        factors=options.factors,
        skip=options.skip,
        keep=options.keep,
        na_strings=options.na_strings,
        nrows=options.nrows,
        meta=options.meta,
    )
