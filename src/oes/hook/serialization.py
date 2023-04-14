"""Serialization module."""
from pathlib import Path

from cattrs import Converter, override
from cattrs.gen import make_dict_structure_fn, make_dict_unstructure_fn
from cattrs.preconf.orjson import make_converter

from oes.hook.executable import ExecutableHook
from oes.hook.http import HttpHook
from oes.hook.python import PythonHook
from oes.hook.types import Hook

default_converter = make_converter()


def structure_hook(converter: Converter, v: object):
    if not isinstance(v, dict):
        raise TypeError(f"Not a dict: {v}")

    if "url" in v:
        return converter.structure(v, HttpHook)
    elif "python" in v:
        return converter.structure(v, PythonHook)
    elif "executable" in v:
        return converter.structure(v, ExecutableHook)
    else:
        raise ValueError(f"Invalid hook: {v}")


default_converter.register_structure_hook(Path, lambda v, t: Path(v))

default_converter.register_unstructure_hook(Path, lambda v: str(v))

default_converter.register_structure_hook_func(
    lambda cls: cls is Hook, lambda v, t: structure_hook(default_converter, v)
)

default_converter.register_structure_hook(
    PythonHook,
    make_dict_structure_fn(
        PythonHook,
        default_converter,
        _object=override(omit=True),
    ),
)

default_converter.register_unstructure_hook(
    PythonHook,
    make_dict_unstructure_fn(
        PythonHook,
        default_converter,
        _object=override(omit=True),
    ),
)
