import asyncio
import copy
from typing import Any

import pytest

from oes.hook import PythonHookConfig, python_hook_factory


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


def test_module():
    config = PythonHookConfig("tests.test_python:example")
    hook = python_hook_factory(config)
    body = {"test": 1}
    res = hook(body)
    assert res == {"test": 2}


@pytest.mark.asyncio
async def test_module_async():
    config = PythonHookConfig("tests.test_python:async_example")
    hook = python_hook_factory(config)
    body = {"test": 1}
    assert asyncio.iscoroutinefunction(hook)
    res = await hook(body)
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
        python_hook_factory(PythonHookConfig(python=path))
