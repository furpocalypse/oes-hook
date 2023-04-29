"""Executable hook type."""
import json
import os
import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from attrs import frozen

from oes.hook.types import Hook

Serializer = Callable[[Any], bytes]
Deserializer = Callable[[bytes], Any]


def default_serializer(obj: Any) -> bytes:
    if isinstance(obj, bytes):
        return obj
    else:
        return json.dumps(obj).encode()


def default_deserializer(data: bytes) -> Any:
    return json.loads(data.decode())


@frozen
class ExecutableHookConfig:
    """A hook that invokes an executable."""

    executable: Path
    """The :class:`Path` to the executable."""

    args: Sequence[str] = ()
    """The arguments to pass to the executable.

    These are passed as-is, there is no variable interpolation performed.
    """

    serializer: Serializer = default_serializer
    """Used to serialize the hook body to bytes."""

    deserializer: Deserializer = default_deserializer
    """Used to deserialize the output bytes into a Python object."""

    def __attrs_post_init__(self):
        if not check_executable(self.executable):
            raise ValueError(f"Not executable: {self.executable}")


def executable_hook_factory(config: ExecutableHookConfig) -> Hook:
    """Create an executable hook."""

    def hook(body: Any) -> Any:
        input_bytes = config.serializer(body)
        output_bytes = _run(config.executable, config.args, input_bytes)
        return config.deserializer(output_bytes)

    return hook


def _run(exec: Path, args: Sequence[str], input_: bytes) -> bytes:
    result = subprocess.run(
        [
            str(exec),
            *args,
        ],
        shell=False,
        input=input_,
        check=True,
        capture_output=True,
    )
    return result.stdout


def check_executable(path: Path) -> bool:
    """Check if the given path is executable."""
    if not path.is_file():
        return False

    return os.access(path, os.X_OK)
