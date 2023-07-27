"""
CLI-Agnostic support.
"""
import select
import string
import sys
import textwrap
import typing

import rich

from .helpers import flatten
from .magic import find_missing_variables, generate_magic_code


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
    db_type: typing.Optional[str] = None,
    tables: typing.Optional[list[str] | list[list[str]]] = None,
    verbose: typing.Optional[bool] = False,
    noop: typing.Optional[bool] = False,
    magic: typing.Optional[bool] = False,
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
            print(generate_sql(db[table], db_type=db_type))
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
