"""HTTP hook."""
import asyncio
import re

from attrs import field, frozen

from oes.hook.types import Body, Hook, InvokeOptions


@frozen
class HttpHook(Hook):
    url: str = field(repr=False)
    """The URL."""

    def __attrs_post_init__(self):
        if not re.match(r"^https?://", self.url, re.I):
            raise ValueError(f"Not a valid URL: {self.url}")

    async def invoke(self, body: Body, options: InvokeOptions) -> Body:
        http_func = options.config.http_func
        if asyncio.iscoroutinefunction(http_func):
            result = await http_func(body, options)
        else:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                options.config.executor, http_func, options, body
            )

        return result if result is not None else {}
