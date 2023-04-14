from pathlib import Path

import pytest

from oes.hook.executable import ExecutableHook
from oes.hook.types import Config, InvokeOptions


@pytest.fixture
def config():
    return Config(http_func=lambda c, b: b)


@pytest.mark.asyncio
async def test_executable(config: Config):
    hook = ExecutableHook(
        executable=Path("/bin/sh"), args=("-c", 'echo "{\\"test\\": true}"')
    )
    invoke_config = InvokeOptions(hook=hook, config=config)
    res = await hook.invoke({"test": False}, invoke_config)
    assert res == {"test": True}


@pytest.mark.asyncio
async def test_executable_json_parse(config: Config):
    hook = ExecutableHook(executable=Path("/bin/sh"), args=("-c", "cat"))
    invoke_config = InvokeOptions(hook=hook, config=config)
    res = await hook.invoke({"test": 123}, invoke_config)
    assert res == {"test": 123}


@pytest.mark.parametrize(
    "path",
    [
        "/bin/non_existent",
        "/bin",
        "/dev/null",
    ],
)
def test_executable_not_executable(path):
    with pytest.raises(ValueError):
        ExecutableHook(executable=Path(path))
