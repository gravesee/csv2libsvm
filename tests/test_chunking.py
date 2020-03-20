import pytest
from libsvm.core import get_conversion_dict, iter_chunks, infer_dtypes_from_csv
import pandas as pd
import seaborn as sns

@pytest.fixture
def data():
    return sns.load_dataset('iris')

def test_chunking_returns_same_results(data):
    d1 = get_conversion_dict(iter_chunks(data, -1))
    d2 = get_conversion_dict(iter_chunks(data, 10))
    assert d1 == d2
    
def test_chunking_returns_same_results_single(data):
    d1 = get_conversion_dict(iter_chunks(data, -1))
    d2 = get_conversion_dict(iter_chunks(data, 1))
    assert d1 == d2

def test_chunking_from_file_matches_memory(data):
    d1 = infer_dtypes_from_csv('libsvm/iris.csv', 10)
    d2 = get_conversion_dict(iter_chunks(data, 10))
    assert d1 == d2