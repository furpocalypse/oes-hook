"""HTTP hook."""
from __future__ import annotations

import asyncio
import re
from collections.abc import Callable
from typing import Any

from attrs import field, frozen

from oes.hook.types import AsyncHook, Hook, SyncHook


@frozen
class HttpHookConfig:
    """HTTP hook."""

    url: str = field(repr=False)
    """The URL."""

    http_func: HttpFunc
    """The function to call to perform the HTTP request."""

    def __attrs_post_init__(self):
        if not re.match(r"^https?://", self.url, re.I):
            raise ValueError(f"Not a valid URL: {self.url}")


HttpFunc = Callable[[Any, HttpHookConfig], Any]


def _make_sync_hook(config: HttpHookConfig) -> SyncHook:
    def hook(body: Any) -> Any:
        return config.http_func(body, config)

    return hook


def _make_async_hook(config: HttpHookConfig) -> AsyncHook:
    async def hook(body: Any) -> Any:
        return await config.http_func(body, config)

    return hook


def http_hook_factory(config: HttpHookConfig) -> Hook:
    """Create a webhook."""
    if asyncio.iscoroutinefunction(config.http_func):
        return _make_async_hook(config)
    else:
        return _make_sync_hook(config)
