# csv2libsvm

convert csv files to libsvm format

## About

libsvm is an on-disk format that is used in certain algorithms. Most notably
among these is xgboost. This package provides tools for converting files to
libsvm format for modeling with large datasets on-disk.

## Installation

```python
# using pip
python -m pip install git+https://github.com/Zelazny7/csv2libsvm.git

# using git
clone https://github.com/Zelazny7/csv2libsvm.git
cd csv2libsvm
python -m pip install .
```

## Command Line Usage

`csv2libsvm` also install a utility by the same name that can be run from the command line.

```bash
csv2libsvm -i titanic.csv -o test -t survived -p '{"train": 50, "test": 50}' -k pclass,sibsp,fare,age
```

The cli uses python's `optparse`. The help is displayed below:

```
Usage: csv2libsvm [options]

Options:
  -h, --help            show this help message and exit
  -i INFILE, --infile=INFILE
                        input file name
  -o OUTPATH, --outpath=OUTPATH
                        path to directory for output
  -t TARGET, --target=TARGET
                        string name of target variable
  -w WEIGHT, --weight=WEIGHT
                        string name of weight variable
  -z SPLIT, --split=SPLIT
                        string name of variable with dev/val, etc...
  -p SPLIT, --probs=SPLIT
                        json object of probs to create multiple output files
  -f FACTORS, --factors=FACTORS
                        csv list of strings indicating factor columns
  -s SKIP, --skip=SKIP  csv list of string names to skip
  -k KEEP, --keep=KEEP  csv list of string names to keep
  -n NA_STRINGS, --na_strings=NA_STRINGS
                        csv list of strings representing NULL values
  -N NROWS, --nrows=NROWS
                        number of input file rows to process
  -m META, --meta=META  path to saved meta.json file from previous run
```

## Module Usage

See [example](/examples/example01.ipynb) in examples folder