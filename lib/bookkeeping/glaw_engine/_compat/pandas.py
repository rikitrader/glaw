"""Tiny pandas-like subset for GLAW zero-dependency bookkeeping paths."""
from __future__ import annotations

import csv


def isna(value):
    return value is None or value == ""


class Series(list):
    def __init__(self, data=None, index=None):
        super().__init__(data or [])
        self.index = index

    def map(self, fn):
        return Series([fn(v) for v in self], index=self.index)

    def fillna(self, value=0):
        return Series([value if isna(v) else v for v in self], index=self.index)

    def dropna(self):
        return Series([v for v in self if not isna(v)])

    def astype(self, typ):
        return Series([typ(v) for v in self], index=self.index)

    @property
    def iloc(self):
        return self

    def __sub__(self, other):
        if isinstance(other, Series):
            return Series([(a or 0) - (b or 0) for a, b in zip(self, other)], index=self.index)
        return Series([(a or 0) - other for a in self], index=self.index)


class DataFrame:
    def __init__(self, data=None, index=None, **kwargs):
        if data is None:
            self.rows = []
        elif isinstance(data, dict):
            keys = list(data)
            size = max((len(v) if isinstance(v, list) else 1) for v in data.values()) if data else 0
            self.rows = [{k: (data[k][i] if isinstance(data[k], list) and i < len(data[k]) else data[k]) for k in keys} for i in range(size)]
        else:
            self.rows = [dict(r) for r in data]
        self.index = list(range(len(self.rows))) if index is None else index

    @classmethod
    def from_records(cls, rows):
        return cls(rows)

    @property
    def columns(self):
        cols = []
        for row in self.rows:
            for key in row:
                if key not in cols:
                    cols.append(key)
        return cols

    @property
    def empty(self):
        return not self.rows

    def copy(self):
        return DataFrame(self.rows, index=list(self.index))

    def __len__(self):
        return len(self.rows)

    def __contains__(self, key):
        return key in self.columns

    def __getitem__(self, key):
        return Series([r.get(key) for r in self.rows], index=self.index)

    def __setitem__(self, key, values):
        if not isinstance(values, (list, Series)):
            values = [values] * len(self.rows)
        while len(self.rows) < len(values):
            self.rows.append({})
        for i, value in enumerate(values):
            self.rows[i][key] = value

    def fillna(self, value=None):
        value = value or {}
        rows = []
        for row in self.rows:
            new = dict(row)
            for key, replacement in value.items():
                if isna(new.get(key)):
                    new[key] = replacement
            rows.append(new)
        return DataFrame(rows, index=self.index)

    def to_dict(self, orient="records"):
        if orient != "records":
            raise ValueError("only records orient is supported")
        return [dict(r) for r in self.rows]

    def to_csv(self, path_or_file, index=False, mode="w"):
        close = False
        if isinstance(path_or_file, (str, bytes)):
            f = open(path_or_file, mode, newline="", encoding="utf-8")
            close = True
        else:
            f = path_or_file
        try:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            if mode == "w":
                writer.writeheader()
            writer.writerows(self.rows)
        finally:
            if close:
                f.close()


def read_csv(path, sep=None, engine=None):
    with open(path, newline="", encoding="utf-8") as f:
        return DataFrame(csv.DictReader(f))


def concat(frames):
    rows = []
    for frame in frames:
        rows.extend(frame.to_dict("records"))
    return DataFrame(rows)


class ExcelWriter:
    def __init__(self, filename, engine=None):
        self.filename = filename

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False
