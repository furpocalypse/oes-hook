"""Executable hook type."""
import asyncio
import os
import subprocess
from collections.abc import Sequence
from pathlib import Path

from attrs import frozen

from oes.hook.types import Body, Hook, InvokeOptions


@frozen
class ExecutableHook(Hook):
    executable: Path
    args: Sequence[str] = ()

    def __attrs_post_init__(self):
        if not check_executable(self.executable):
            raise ValueError(f"Not executable: {self.executable}")

    async def invoke(self, body: Body, options: InvokeOptions) -> Body:
        loop = asyncio.get_running_loop()
        input_ = options.config.json_dumps(body)

        if isinstance(input_, str):
            input_ = input_.encode()

        output = await loop.run_in_executor(
            options.config.executor, _run, self.executable, self.args, input_
        )
        result = options.config.json_loads(output) if output else {}
        return result


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
