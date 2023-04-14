import asyncio
import copy
from typing import Any

import pytest

from oes.hook.python import PythonHook
from oes.hook.types import Config, InvokeOptions


def example(body: dict[str, Any]) -> dict[str, Any]:
    cur = body.get("test", 0)
    new_body = copy.deepcopy(body)
    new_body["test"] = cur + 1
    return new_body


async def async_example(body: dict[str, Any]) -> dict[str, Any]:
    await asyncio.sleep(0.1)
    cur = body.get("test", 0)
    new_body = copy.deepcopy(body)
    new_body["test"] = cur + 1
    return new_body


@pytest.fixture
def config():
    return Config(http_func=lambda c, b: b)


@pytest.mark.asyncio
async def test_module(config: Config):
    module = PythonHook("tests.test_python:example")
    body = {"test": 1}
    invoke_config = InvokeOptions(hook=module, config=config)
    res = await module.invoke(body, invoke_config)
    assert res == {"test": 2}


@pytest.mark.asyncio
async def test_module_async(config: Config):
    module = PythonHook("tests.test_python:async_example")
    body = {"test": 1}
    invoke_config = InvokeOptions(hook=module, config=config)
    res = await module.invoke(body, invoke_config)
    assert res == {"test": 2}


@pytest.mark.parametrize(
    "path",
    [
        "oes.hook.non_existent",
        "tests.test_module:non_existent",
        "tests.test_module:example.non_existent",
    ],
)
def test_module_not_found(path):
    with pytest.raises(ValueError):
        PythonHook(python=path)
