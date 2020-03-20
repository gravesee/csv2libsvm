# libsvm

convert csv files to libsvm format

## About

libsvm is an on-disk format that is used in certain algorithms. Most notably
among these is xgboost. This package provides tools for converting files to
libsvm format for modeling with large datasets on-disk.

## Installation

Coming soon

## Usage

```python
from libsvm import csv_to_libsvm

csv_to_libsvm("titanic.csv", "train.libsvm", "survived", 100)
```

The above function will infer data types on `titanic.csv` using pandas. It will
convert string data to integers and ensure the target variable is output in the
first column.

`csv_to_libsvm` is also memory efficient with an optional `chunksize` parameter.
