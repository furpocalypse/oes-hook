"""Python module hook."""
import asyncio
import importlib
from collections.abc import Callable, Coroutine, Sequence
from typing import Any, Optional, Union

from attrs import Factory, field, frozen

from oes.hook.types import Body, Hook, InvokeOptions


@frozen
class PythonHook(Hook):
    """Python function hook."""

    python: str
    """Path to the python object, formatted as module:object."""

    _object: Callable[
        [Body], Union[Optional[Body], Coroutine[None, None, Optional[Body]]]
    ] = field(
        eq=False, default=Factory(lambda h: import_object(h.python), takes_self=True)
    )
    """The imported object."""

    async def invoke(self, body: Body, options: InvokeOptions) -> Body:
        if asyncio.iscoroutinefunction(self._object):
            result = await self._object(body)
        else:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                options.config.executor, self._object, body
            )

        return result if result is not None else {}


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
) -> Callable[[Body], Union[Optional[Body], Coroutine[None, None, Optional[Body]]]]:
    """Import an object by a path."""
    module_name, obj_path = parse_module_path(path)
    module = import_module(module_name)
    obj = get_object(module, obj_path)
    return obj
