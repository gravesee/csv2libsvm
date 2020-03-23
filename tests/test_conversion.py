import pytest, io, csv, textwrap, tempfile
from csv2libsvm.cli import main
from csv2libsvm import csv2libsvm


@pytest.fixture
def data():
    data = textwrap.dedent("""\
        target,weight,sample,numeric_feature,factor_feature,skip_feature
        1,0.5,dev,0.75,cat,123ABC
        0,1.5,val,1.00,dog,456DEF"""
    )
    return io.StringIO(data)

@pytest.fixture
def data_nas():
    data = textwrap.dedent("""\
        target,weight,sample,numeric_feature,factor_feature,skip_feature
        1,0.5,dev,,cat,123ABC
        0,1.5,val,1.00,,456DEF"""
    )
    return io.StringIO(data)


def test_function_baseline(data):
    csv2libsvm(
        data,
        "tests/test_output",
        target="target",
        weight="weight",
        split="sample",
        factors=["factor_feature"], skip=["skip_feature"]
    )

    with open("tests/test_output/part-dev.libsvm", "r") as dev, \
        open("tests/test_output/part-val.libsvm", "r") as val:
        assert [x.strip() for x in dev.readlines()] == ["1:0.5 1:0.75 2:1"]
        assert [x.strip() for x in val.readlines()] == ["0:1.5 1:1.00 2:2"]

def test_function_missings(data_nas):
    csv2libsvm(
        data_nas,
        "tests/test_output",
        target="target",
        weight="weight",
        split="sample",
        factors=["factor_feature"], skip=["skip_feature"]
    )

    with open("tests/test_output/part-dev.libsvm", "r") as dev, \
        open("tests/test_output/part-val.libsvm", "r") as val:
        assert [x.strip() for x in dev.readlines()] == ["1:0.5 2:1"]
        assert [x.strip() for x in val.readlines()] == ["0:1.5 1:1.00"]

def test_function_no_weight(data):
    csv2libsvm(
        data,
        "tests/test_output",
        target="target",
        #weight="weight",
        split="sample",
        factors=["factor_feature"], skip=["skip_feature", "weight"]
    )

    with open("tests/test_output/part-dev.libsvm", "r") as dev, \
        open("tests/test_output/part-val.libsvm", "r") as val:
        assert [x.strip() for x in dev.readlines()] == ["1 1:0.75 2:1"]
        assert [x.strip() for x in val.readlines()] == ["0 1:1.00 2:2"]
