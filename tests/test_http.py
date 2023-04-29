import asyncio
from typing import Any

import httpx
import orjson
import pytest
import pytest_asyncio

from oes.hook import HttpHookConfig, http_hook_factory
from oes.hook.http import HttpFunc


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
async def async_client():
    mounts = {"all://": httpx.MockTransport(mock_handler)}
    async with httpx.AsyncClient(mounts=mounts) as client:
        yield client


@pytest.fixture
def client():
    mounts = {"all://": httpx.MockTransport(mock_handler)}
    with httpx.Client(mounts=mounts) as client:
        yield client


@pytest.fixture
def async_http_func(async_client: httpx.AsyncClient) -> HttpFunc:
    async def http_func(body: dict[str, Any], config: HttpHookConfig) -> dict[str, Any]:
        res = await async_client.post(
            config.url,
            json=body,
        )
        json = res.json()
        return json

    return http_func


@pytest.fixture
def http_func(client: httpx.Client) -> HttpFunc:
    def http_func(body: dict[str, Any], config: HttpHookConfig) -> dict[str, Any]:
        res = client.post(
            config.url,
            json=body,
        )
        json = res.json()
        return json

    return http_func


@pytest.mark.asyncio
async def test_http(async_http_func: HttpFunc):
    config = HttpHookConfig("https://example.com/hook", async_http_func)
    hook = http_hook_factory(config)
    assert asyncio.iscoroutinefunction(hook)
    res = await hook({"test": 1})
    assert res == {"test": 2}


def test_http_sync(http_func: HttpFunc):
    config = HttpHookConfig("https://example.com/hook", http_func)
    hook = http_hook_factory(config)
    res = hook({"test": 1})
    assert res == {"test": 2}
