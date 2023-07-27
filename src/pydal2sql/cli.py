import sys
import typing
from typing import Annotated, Optional

import typer
from rich import print
from typer import Argument
from typing_extensions import Never

from .__about__ import __version__
from .typer_support import (
    DEFAULT_VERBOSITY,
    ApplicationState,
    Verbosity,
    create_enum_from_literal,
)
from .types import SUPPORTED_DATABASE_TYPES_WITH_ALIASES

## type fuckery:

DB_Types: typing.Any = create_enum_from_literal("DBType", SUPPORTED_DATABASE_TYPES_WITH_ALIASES)

T = typing.TypeVar("T")

OptionalArgument = Annotated[Optional[T], Argument()]
# usage: (myparam: OptionalArgument[some_type])

### end typing stuff, start app:

app = typer.Typer()
state = ApplicationState()


def info(*args: str) -> None:
    """
    'print' but with blue text.
    """
    print(f"[blue]{' '.join(args)}[/blue]", file=sys.stderr)


def warn(*args: str) -> None:
    """
    'print' but with yellow text.
    """
    print(f"[yellow]{' '.join(args)}[/yellow]", file=sys.stderr)


def danger(*args: str) -> None:
    """
    'print' but with red text.
    """
    print(f"[red]{' '.join(args)}[/red]", file=sys.stderr)


@app.command()
def create(filename: OptionalArgument[str] = None, db_type: DB_Types = None) -> None:
    """

    Examples:
        pydal2sql create models.py
        cat models.py | pydal2sql
        pydal2sql # output from stdin
    """
    print(filename)
    print(db_type.value if db_type else None)


@app.command()
def alter(
    filename_before: OptionalArgument[str] = None,
    filename_after: OptionalArgument[str] = None,
    db_type: DB_Types = None,
) -> None:
    print(filename_before)
    print(filename_after)
    print(db_type.value if db_type else None)


def show_config_callback() -> Never:
    """
    --show-config requested!
    """
    print(state)
    raise typer.Exit(0)


def version_callback() -> Never:
    """
    --version requested!
    """
    print(f"su6 Version: {__version__}")

    raise typer.Exit(0)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    config: str = None,
    verbosity: Verbosity = DEFAULT_VERBOSITY,
    # stops the program:
    show_config: bool = False,
    version: bool = False,
) -> None:
    """
    This callback will run before every command, setting the right global flags.

    Args:
        ctx: context to determine if a subcommand is passed, etc
        config: path to a different config toml file
        verbosity: level of detail to print out (1 - 3)

        show_config: display current configuration?
        version: display current version?

    """
    state.load_config(config_file=config, verbosity=verbosity)

    if show_config:
        show_config_callback()
    elif version:
        version_callback()
    elif not ctx.invoked_subcommand:
        warn("Missing subcommand. Try `pydal2sql --help` for more info.")
    # else: just continue


if __name__ == "__main__":
    app()
