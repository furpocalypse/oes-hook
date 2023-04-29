"""Python module hook."""
import asyncio
import importlib
from collections.abc import Callable, Coroutine, Sequence
from typing import Any

from attrs import frozen

from oes.hook.types import AsyncHook, Hook, SyncHook


@frozen
class PythonHookConfig:
    """Python function hook."""

    python: str
    """Path to the python object, formatted as module:object."""


def _make_async_hook(obj: Callable[[Any], Coroutine[None, None, Any]]) -> AsyncHook:
    async def hook(body: Any) -> Any:
        return await obj(body)

    return hook


def _make_sync_hook(obj: Callable[[Any], Any]) -> SyncHook:
    def hook(body: Any) -> Any:
        return obj(body)

    return hook


def python_hook_factory(config: PythonHookConfig) -> Hook:
    """Create a Python hook."""
    obj = import_object(config.python)
    if asyncio.iscoroutinefunction(obj):
        return _make_async_hook(obj)
    else:
        return _make_sync_hook(obj)


def parse_module_path(path: str) -> tuple[str, Sequence[str]]:
    """Parse a module:object path."""
    module, _, obj_path = path.partition(":")
    if not obj_path:
        raise ValueError(f"Cannot import {path!r}")

    return module, obj_path.split(".")


def import_module(path: str) -> object:
    """Import and return the given module."""
    try:
        result = importlib.import_module(path)
    except ImportError as e:
        raise ValueError(f"Cannot import {path!r}") from e

    return result


def get_object(src: object, path: Sequence[str]) -> Any:
    """Get the object from a module given a sequence of attributes."""
    cur = src

    for p in path:
        try:
            next_ = getattr(cur, p)
        except AttributeError as e:
            raise ValueError(f"Cannot import {'.'.join(path)!r}") from e
        cur = next_

    return cur


def import_object(
    path: str,
) -> Callable[[Any], Any]:
    """Import an object by a path."""
    module_name, obj_path = parse_module_path(path)
    module = import_module(module_name)
    obj = get_object(module, obj_path)
    return obj
