# OES Hooks

A library for configuring and invoking hooks within an application.

This is mostly meant to be used by other OES projects.

## Development Setup

- Install the development environment with [Poetry](https://python-poetry.org/):

      poetry install

- Install [pre-commit](https://pre-commit.com/) and run:

      pre-commit install

  to configure the linting/formatting hooks.

- Run tests with `poetry run pytest`.


## Usage

Webhook:

```python
import asyncio
from oes.hook import HttpHookConfig, http_hook_factory

# Or your favorite http library
import httpx


async def http_func(body, config: HttpHookConfig):
  async with httpx.AsyncClient() as client:
    response = await client.post(config.url, json=body)
    return response.json()


hook = http_hook_factory(
  HttpHookConfig(
    url="https://httpbin.org/post",
    http_func=http_func,
  )
)

async def main():
  res = await hook({"test": "Hello, world!"})
  print(res)

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
```

Executable:

```python
from oes.hook import ExecutableHookConfig, executable_hook_factory

from pathlib import Path

hook = executable_hook_factory(
  ExecutableHookConfig(
    executable=Path("/bin/sh"),
    args=("-c", "cat")
  )
)

print(hook({"test": "Hello, world!"}))

```
