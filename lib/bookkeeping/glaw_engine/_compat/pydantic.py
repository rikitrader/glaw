"""Small subset of pydantic used by the vendored bookkeeping engine."""
from __future__ import annotations

import json
from decimal import Decimal
from dataclasses import asdict, is_dataclass


class ValidationError(ValueError):
    pass


def ConfigDict(**kwargs):
    return dict(kwargs)


def Field(default=None, **kwargs):
    return default


def computed_field(func=None, **kwargs):
    def deco(f):
        return f
    return deco(func) if func else deco


def model_validator(*args, **kwargs):
    def deco(f):
        return f
    return deco


class BaseModel:
    model_config = {}

    def __init__(self, **kwargs):
        annotations = {}
        for cls in reversed(type(self).mro()):
            annotations.update(getattr(cls, "__annotations__", {}))
        for name in annotations:
            if name in kwargs:
                setattr(self, name, kwargs.pop(name))
            elif hasattr(type(self), name):
                setattr(self, name, getattr(type(self), name))
            else:
                setattr(self, name, None)
        for name, value in kwargs.items():
            setattr(self, name, value)
        for attr in dir(self):
            fn = getattr(self, attr)
            if callable(fn) and getattr(fn, "__name__", "") == "_check_non_inverted":
                fn()

    def model_copy(self, update=None):
        data = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        data.update(update or {})
        return type(self)(**data)

    def model_dump(self):
        data = {}
        for key, value in self.__dict__.items():
            if key.startswith("_"):
                continue
            data[key] = _dump(value)
        for name in dir(type(self)):
            attr = getattr(type(self), name)
            if isinstance(attr, property):
                try:
                    data[name] = _dump(getattr(self, name))
                except Exception:
                    pass
        return data

    def model_dump_json(self):
        return json.dumps(self.model_dump(), default=str)


def _dump(value):
    if isinstance(value, BaseModel):
        return value.model_dump()
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, list):
        return [_dump(v) for v in value]
    if isinstance(value, dict):
        return {k: _dump(v) for k, v in value.items()}
    if isinstance(value, Decimal):
        return str(value)
    return value
