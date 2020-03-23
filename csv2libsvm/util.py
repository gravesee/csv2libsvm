from typing import Optional, Dict
import random

def line_count(infile: str, nrows: Optional[int] = None) -> int:
    """quick line count of file"""
    with open(infile, "r") as fin:
        for lc, _ in enumerate(fin):
            pass
    if nrows is not None:
        lc = min(lc, nrows)
    return lc


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


class RandomFileSplitter:
    def __init__(self, probs: Dict[str, float]):
        tot = 0.0
        for prob in probs.values():
            tot += prob
        # rescale to sum to 1
        self.probs = {k: v / tot for k, v in probs.items()}

    @property
    def random_file(self) -> str:
        res = ""
        q = random.uniform(0, 1)
        cuml_prob = 0.0
        for k, v in self.probs.items():
            cuml_prob += v
            if q <= cuml_prob:
                res = k
                break
        return res
