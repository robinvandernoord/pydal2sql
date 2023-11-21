"""
Todo: test with Typer
"""
import typing
from pathlib import Path

import pytest

from src.pydal2sql.types import DB_Types
from src.pydal2sql.typer_support import (
    Verbosity,
    create_enum_from_literal,
    get_pydal2sql_config,
)


def test_enum_typer():
    assert "DBType(" in repr(DB_Types)
    assert "'psql'," in repr(DB_Types)

    assert repr(create_enum_from_literal("MyName", typing.Literal["value1", "value2"])) == "MyName('value1', 'value2')"
    assert repr(create_enum_from_literal("MyName", "value")) == "MyName('value')"


def test_verbosity():
    assert Verbosity.normal == "2"
    assert Verbosity.normal > 1
    assert Verbosity.normal > Verbosity.quiet
    assert Verbosity.normal >= Verbosity.quiet
    assert Verbosity.normal < Verbosity.debug
    assert Verbosity.normal <= Verbosity.debug

    with pytest.raises(TypeError):
        assert Verbosity.normal == TypeError


def test_get_pydal2sql_config():
    pytest_examples = Path("./pytest_examples").resolve()

    with pytest.raises(FileNotFoundError):
        get_pydal2sql_config("fake_path.toml", verbosity=Verbosity.debug)

    config = get_pydal2sql_config(str(pytest_examples / "some_config.toml"), verbosity=Verbosity.debug)

    assert config.magic == True
