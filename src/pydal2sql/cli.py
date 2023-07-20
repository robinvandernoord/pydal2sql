"""
CLI tool to generate SQL from PyDAL code.
"""

import argparse
import pathlib
import select
import string
import sys
import textwrap
from typing import IO, Optional

import rich
from rich.prompt import Prompt

from .helpers import flatten
from .magic import find_missing_variables, generate_magic_code


class PrettyParser(argparse.ArgumentParser):  # pragma: no cover
    """
    Add 'rich' to the argparse output.
    """

    def _print_message(self, message: str, file: Optional[IO[str]] = None) -> None:
        rich.print(message, file=file)


def has_stdin_data() -> bool:  # pragma: no cover
    """
    Check if the program starts with cli data (pipe | or redirect ><).

    See Also:
        https://stackoverflow.com/questions/3762881/how-do-i-check-if-stdin-has-some-data
    """
    return any(
        select.select(
            [
                sys.stdin,
            ],
            [],
            [],
            0.0,
        )[0]
    )


def handle_cli(
    code: str,
    db_type: str = None,
    tables: list[list[str]] = None,
    verbose: bool = False,
    noop: bool = False,
    magic: bool = False,
) -> None:
    """
    Handle user input.
    """
    to_execute = string.Template(
        textwrap.dedent(
            """
        from pydal import *
        from pydal.objects import *
        from pydal.validators import *

        from pydal2sql import generate_sql

        db = database = DAL(None, migrate=False)

        tables = $tables
        db_type = '$db_type'

        $extra

        $code

        if not tables:
            tables = db._tables

        for table in tables:
            print(generate_sql(db[table], db_type))
    """
        )
    )

    generated_code = to_execute.substitute(
        {"tables": flatten(tables or []), "db_type": db_type or "", "code": textwrap.dedent(code), "extra": ""}
    )
    if verbose or noop:
        rich.print(generated_code, file=sys.stderr)

    if not noop:
        try:
            exec(generated_code)  # nosec: B102
        except NameError:
            # something is missing!
            missing_vars = find_missing_variables(generated_code)
            if not magic:
                rich.print(
                    f"Your code is missing some variables: {missing_vars}. Add these or try --magic", file=sys.stderr
                )
            else:
                extra_code = generate_magic_code(missing_vars)

                generated_code = to_execute.substitute(
                    {
                        "tables": flatten(tables or []),
                        "db_type": db_type or "",
                        "extra": extra_code,
                        "code": textwrap.dedent(code),
                    }
                )

                if verbose:
                    print(generated_code, file=sys.stderr)

                exec(generated_code)  # nosec: B102


def app() -> None:  # pragma: no cover
    """
    Entrypoint for the pydal2sql cli command.
    """
    parser = PrettyParser(
        prog="pydal2sql",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""[green]CLI tool to generate SQL from PyDAL code.[/green]\n
        Aside from using cli arguments, you can also configure the tool in your code.
        You can set the following variables:

        db_type: str = 'sqlite' # your desired database type;
        tables: list[str] = []  # your desired tables to generate SQL for;""",
        epilog="Example: [i]cat models.py | pydal2sql sqlite[/i]",
    )

    parser.add_argument("filename", nargs="?", help="Which file to load? Can also be done with stdin.")

    parser.add_argument(
        "db_type", nargs="?", help="Which database dialect to generate ([blue]postgres, sqlite, mysql[/blue])"
    )

    parser.add_argument("--verbose", "-v", help="Show more info", action=argparse.BooleanOptionalAction, default=False)

    parser.add_argument(
        "--noop", "-n", help="Only show code, don't run it.", action=argparse.BooleanOptionalAction, default=False
    )

    parser.add_argument(
        "--magic", "-m", help="Perform magic to fix missing vars.", action=argparse.BooleanOptionalAction, default=False
    )

    parser.add_argument(
        "-t",
        "--table",
        "--tables",
        action="append",
        nargs="+",
        help="One or more tables to generate. By default, all tables in the file will be used.",
    )

    args = parser.parse_args()

    db_type = args.db_type or args.filename

    load_file_mode = (filename := args.filename) and filename.endswith(".py")

    if not (has_stdin_data() or load_file_mode):
        if not db_type:
            db_type = Prompt.ask("Which database type do you want to use?", choices=["sqlite", "postgres", "mysql"])

        rich.print("Please paste your define tables code below and press ctrl-D when finished.", file=sys.stderr)

    # else: data from stdin
    # py code or cli args should define settings.
    if load_file_mode:
        db_type = args.db_type
        text = pathlib.Path(filename).read_text()
    else:
        text = sys.stdin.read()

    return handle_cli(text, db_type, args.table, verbose=args.verbose, noop=args.noop, magic=args.magic)
