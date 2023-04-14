import copy
from typing import Any, cast

import httpx
import orjson
import pytest
import pytest_asyncio

from oes.hook.http import HttpHook
from oes.hook.types import Config, HttpFunc, InvokeOptions


def mock_handler(request: httpx.Request):
    data = orjson.loads(request.read())
    data["test"] = data.get("test", 0) + 1
    return httpx.Response(
        200,
        content=orjson.dumps(data),
        headers={
            "content-type": "application/json",
        },
    )


@pytest_asyncio.fixture
async def client():
    mounts = {"all://": httpx.MockTransport(mock_handler)}
    async with httpx.AsyncClient(mounts=mounts) as client:
        yield client


@pytest.fixture
def http_func(client: httpx.AsyncClient) -> HttpFunc:
    async def http_func(body: dict[str, Any], config: InvokeOptions) -> dict[str, Any]:
        hook = cast(HttpHook, config.hook)
        res = await client.post(
            hook.url,
            json=body,
        )
        json = res.json()
        return json

    return http_func


@pytest.fixture
def config(http_func: HttpFunc):
    return Config(http_func=http_func)


@pytest.mark.asyncio
async def test_http(config: Config):
    hook = HttpHook("https://example.com/hook")
    invoke_config = InvokeOptions(hook=hook, config=config)
    res = await hook.invoke({"test": 1}, invoke_config)
    assert res == {"test": 2}


@pytest.mark.asyncio
async def test_http_sync():
    def http_func(config: InvokeOptions, body: dict[str, Any]) -> dict[str, Any]:
        new_dict = copy.deepcopy(body)
        new_dict["test"] = new_dict.get("test", 0) + 1
        return new_dict

    config = Config(http_func=http_func)

    hook = HttpHook("https://example.com/hook")
    invoke_config = InvokeOptions(hook=hook, config=config)
    res = await hook.invoke({"test": 1}, invoke_config)
    assert res == {"test": 2}
