from pathlib import Path

import pytest

from oes.hook import ExecutableHookConfig, executable_hook_factory


def test_executable():
    hook = executable_hook_factory(
        ExecutableHookConfig(
            executable=Path("/bin/sh"),
            args=("-c", 'echo "{\\"test\\": true}"'),
        )
    )

    res = hook({"test": False})
    assert res == {"test": True}

    assert res == {"test": True}


def test_executable_json_parse():
    hook = executable_hook_factory(
        ExecutableHookConfig(executable=Path("/bin/sh"), args=("-c", "cat"))
    )
    res = hook({"test": 123})
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
        executable_hook_factory(ExecutableHookConfig(executable=Path(path)))
