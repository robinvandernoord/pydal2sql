import os
import sys
import typing
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich import print
from rich.prompt import Prompt
from typer import Argument
from typing_extensions import Never

from .__about__ import __version__
from .cli_support import (
    extract_file_versions_and_paths,
    find_git_root,
    get_absolute_path_info,
    get_file_for_version,
    handle_cli_create,
    has_stdin_data,
)
from .typer_support import (
    DEFAULT_VERBOSITY,
    IS_DEBUG,
    ApplicationState,
    Verbosity,
    create_enum_from_literal,
    with_exit_code,
)
from .types import SUPPORTED_DATABASE_TYPES_WITH_ALIASES

## type fuckery:

DB_Types: typing.Any = create_enum_from_literal("DBType", SUPPORTED_DATABASE_TYPES_WITH_ALIASES)

T = typing.TypeVar("T")

OptionalArgument = Annotated[Optional[T], Argument()]
# usage: (myparam: OptionalArgument[some_type])

OptionalOption = Annotated[Optional[T], typer.Option()]
# usage: (myparam: OptionalOption[some_type])

### end typing stuff, start app:

app = typer.Typer(
    no_args_is_help=True,
)
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
@with_exit_code(hide_tb=not IS_DEBUG)
def create(
    filename: OptionalArgument[str] = None,
    tables: Annotated[
        Optional[list[str]],
        typer.Option("--table", "--tables", "-t", help="One or more table names, default is all tables."),
    ] = None,
    db_type: Annotated[DB_Types, typer.Option("--db-type", "--dialect", "-d")] = None,
    magic: Optional[bool] = None,
    noop: Optional[bool] = None,
) -> None:
    """
    todo: docs

    Examples:
        pydal2sql create models.py
        cat models.py | pydal2sql
        pydal2sql # output from stdin
    """
    config = state.update_config(filename=filename, magic=magic, noop=noop, tables=tables)

    load_file_mode = (filename := config.filename) and filename.endswith(".py")

    db_type = db_type.value if db_type else None

    if not (has_stdin_data() or load_file_mode):
        if not db_type:
            db_type = Prompt.ask("Which database type do you want to use?", choices=["sqlite", "postgres", "mysql"])

        print("Please paste your define tables code below and press ctrl-D when finished.", file=sys.stderr)

        # else: data from stdin
        # py code or cli args should define settings.

    if load_file_mode and filename:
        db_type = db_type
        text = Path(filename).read_text()
    else:
        text = sys.stdin.read()
        print("---", file=sys.stderr)

    handle_cli_create(
        text,
        db_type,
        tables=config.tables,
        verbose=state.verbosity > Verbosity.normal,
        noop=config.noop,
        magic=config.magic,
    )


@app.command()
@with_exit_code(hide_tb=not IS_DEBUG)
def alter(
    filename_before: OptionalArgument[str] = None,
    filename_after: OptionalArgument[str] = None,
    db_type: DB_Types = None,
) -> None:
    """
    Todo: docs
    """
    git_root = find_git_root() or Path(os.getcwd())

    before, after = extract_file_versions_and_paths(filename_before, filename_after)

    version_before, filename_before = before
    version_after, filename_after = after

    # either ./file exists or /file exists (seen from git root):

    before_exists, before_absolute_path = get_absolute_path_info(filename_before, version_before, git_root)
    after_exists, after_absolute_path = get_absolute_path_info(filename_after, version_after, git_root)

    if not (before_exists and after_exists):
        message = ""
        message += "" if before_exists else f"Path {filename_before} does not exist! "
        message += "" if after_exists else f"Path {filename_after} does not exist!"
        raise ValueError(message)

    code_before = get_file_for_version(
        before_absolute_path, version_before, prompt_description="current table definition"
    )
    code_after = get_file_for_version(after_absolute_path, version_after, prompt_description="desired table definition")

    if not (code_before and code_after):
        message = ""
        message += "" if code_before else "Before code is empty (Maybe try `pydal2sql create`)! "
        message += "" if code_after else "After code is empty! "
        raise ValueError(message)

    if code_before == code_after:
        print("[red]Both contain the same code![/red]", file=sys.stderr)
        return

    print(len(code_before), len(code_after), db_type)


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
    print(f"pydal2sql Version: {__version__}")

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

    Todo:
        --noop
        --magic

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
