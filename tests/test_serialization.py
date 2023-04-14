import copy
from pathlib import Path
from typing import Any

from oes.hook.executable import ExecutableHook
from oes.hook.http import HttpHook
from oes.hook.python import PythonHook
from oes.hook.serialization import default_converter
from oes.hook.types import Hook


def test_parse_http():
    data = {
        "url": "https://example",
    }

    res = default_converter.structure(data, Hook)
    assert isinstance(res, HttpHook)
    assert res.url == "https://example"


class Example:
    @classmethod
    def example(cls, body: dict[str, Any]) -> dict[str, Any]:
        cur = body.get("test", 0)
        new_body = copy.deepcopy(body)
        new_body["test"] = cur + 1
        return new_body


def test_parse_python():
    data = {
        "python": "tests.test_serialization:Example.example",
    }

    res = default_converter.structure(data, Hook)
    assert isinstance(res, PythonHook)


def test_parse_exec():
    data = {"executable": "/bin/sh", "args": ["-c", "echo test"]}

    res = default_converter.structure(data, Hook)
    assert isinstance(res, ExecutableHook)
    assert res.executable == Path("/bin/sh")
