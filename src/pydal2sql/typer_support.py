"""
Cli-specific support.
"""

import contextlib
import functools
import inspect
import operator
import os
import sys
import typing
from dataclasses import dataclass
from enum import Enum, EnumMeta
from pathlib import Path
from typing import Any, Optional

import configuraptor
import dotenv
import rich
import tomli
import typer
from black.files import find_project_root
from configuraptor import alias, postpone
from configuraptor.helpers import find_pyproject_toml
from pydal2sql_core.state import *  # noqa
from pydal2sql_core.types import (
    DEFAULT_OUTPUT_FORMAT,
    SUPPORTED_DATABASE_TYPES_WITH_ALIASES,
    SUPPORTED_OUTPUT_FORMATS,
)
from su6 import find_project_root
from su6.core import (
    EXIT_CODE_ERROR,
    EXIT_CODE_SUCCESS,
    T_Command,
    T_Inner_Wrapper,
    T_Outer_Wrapper,
)
from typing_extensions import Never


def with_exit_code(hide_tb: bool = True) -> T_Outer_Wrapper:
    """
    Convert the return value of an app.command (bool or int) to an typer Exit with return code, \
    Unless the return value is Falsey, in which case the default exit happens (with exit code 0 indicating success).

    Usage:
    > @app.command()
    > @with_exit_code()
    def some_command(): ...

    When calling a command from a different command, _suppress=True can be added to not raise an Exit exception.

    See Also:
        github.com:trialandsuccess/su6-checker
    """

    def outer_wrapper(func: T_Command) -> T_Inner_Wrapper:
        @functools.wraps(func)
        def inner_wrapper(*args: Any, **kwargs: Any) -> Never:
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                result = EXIT_CODE_ERROR
                if hide_tb:
                    rich.print(f"[red]{e}[/red]", file=sys.stderr)
                else:  # pragma: no cover
                    raise e
            finally:
                sys.stdout.flush()
                sys.stderr.flush()

            if isinstance(result, bool):
                if result in (None, True):
                    # assume no issue then
                    result = EXIT_CODE_SUCCESS
                elif result is False:
                    result = EXIT_CODE_ERROR

            raise typer.Exit(code=int(result or 0))

        return inner_wrapper

    return outer_wrapper


def _is_debug() -> bool:  # pragma: no cover
    folder, _ = find_project_root((os.getcwd(),))
    if not folder:
        folder = Path(os.getcwd())
    dotenv.load_dotenv(folder / ".env")

    return os.getenv("IS_DEBUG") == "1"


def is_debug() -> bool:  # pragma: no cover
    """
    Returns whether IS_DEBUG = 1 in the .env.
    """
    with contextlib.suppress(Exception):
        return _is_debug()
    return False


IS_DEBUG = is_debug()
