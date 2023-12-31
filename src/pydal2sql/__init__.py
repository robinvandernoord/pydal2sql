"""
Expose methods for the library.
"""

# SPDX-FileCopyrightText: 2023-present Robin van der Noord <robinvandernoord@gmail.com>
#
# SPDX-License-Identifier: MIT

from pydal2sql_core import generate_sql
from pydal2sql_core.helpers import get_typing_args
from pydal2sql_core.types import SUPPORTED_DATABASE_TYPES as _SUPPORTED_DATABASE_TYPES

SUPPORTED_DATABASE_TYPES = get_typing_args(_SUPPORTED_DATABASE_TYPES)

__all__ = [
    "generate_sql",
    "SUPPORTED_DATABASE_TYPES",
]
