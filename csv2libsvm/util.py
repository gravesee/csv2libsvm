from typing import Optional, Dict

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


