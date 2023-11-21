"""
Some type magic.
"""

import typing
from typing import Annotated, Optional

from pydal2sql_core import get_typing_args
from pydal2sql_core.types import SUPPORTED_OUTPUT_FORMATS
from typer import Argument, Option

from .typer_support import DB_Types

T = typing.TypeVar("T")

OptionalArgument = Annotated[Optional[T], Argument()]
# usage: (myparam: OptionalArgument[some_type])

OptionalOption = Annotated[Optional[T], Option()]
# usage: (myparam: OptionalOption[some_type])

DBType_Option = Annotated[DB_Types, Option("--db-type", "--dialect", "-d")]

Tables_Option = Annotated[
    Optional[list[str]],
    Option("--table", "--tables", "-t", help="One or more table names, default is all tables."),
]

OutputFormat_Option = Annotated[
    # Optional[SUPPORTED_OUTPUT_FORMATS],
    Optional[str],
    Option("--format", "--fmt", help=f"One of {get_typing_args(SUPPORTED_OUTPUT_FORMATS)}"),
]
