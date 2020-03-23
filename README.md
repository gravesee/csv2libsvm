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

## Usage

See [example](/examples/example01.ipynb) in examples folder