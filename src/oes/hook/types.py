"""Base types and models."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from concurrent.futures import Executor
from typing import Any, Optional, Union

import orjson
from attrs import frozen


@frozen
class InvokeOptions:
    """Options passed when invoking a hook."""

    hook: Hook
    """The hook."""

    config: Config
    """The hook config."""


StrOrBytes = Union[str, bytes]
JsonDumps = Callable[[object], StrOrBytes]
JsonLoads = Callable[[StrOrBytes], object]
Body = dict[str, Any]
SyncHttpFunc = Callable[[Body, InvokeOptions], Optional[Body]]
AsyncHttpFunc = Callable[[Body, InvokeOptions], Coroutine[None, None, Optional[Body]]]
HttpFunc = Union[SyncHttpFunc, AsyncHttpFunc]


def default_json_dumps(obj: object) -> bytes:
    return orjson.dumps(obj)


def default_json_loads(data: StrOrBytes) -> object:
    return orjson.loads(data)


def default_http_func(body: Body, options: InvokeOptions) -> Body:
    raise NotImplementedError


@frozen(kw_only=True)
class Config:
    """Hook configuration."""

    json_dumps: JsonDumps = default_json_dumps
    """JSON ``dumps`` function."""

    json_loads: JsonLoads = default_json_loads
    """JSON ``loads`` function."""

    executor: Optional[Executor] = None
    """Executor for sync functions."""

    http_func: HttpFunc = default_http_func
    """Function to send HTTP requests."""


class Hook(ABC):
    """Base hook type."""

    @abstractmethod
    async def invoke(self, body: Body, options: InvokeOptions) -> Body:
        """Invoke the hook.

        Args:
            body: The hook body.
            options: The :class:`InvokeConfig` instance.

        Returns:
            The result.
        """
        ...
