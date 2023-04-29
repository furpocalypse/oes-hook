"""Base types and classes."""
from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any, Union

SyncHook = Callable[[Any], Any]
AsyncHook = Callable[[Any], Coroutine[None, None, Any]]

Hook = Union[SyncHook, AsyncHook]
"""A callable that accepts the hook body as the argument, and returns the result.

May be a coroutine function.
"""

HookFactory = Callable[[Any], Hook]
"""A factory that returns a configured hook.

Takes a configuration object as its argument, and returns a :class:`Hook`.
"""
