"""
Todo: test with Typer
"""
from pathlib import Path

from typer.testing import CliRunner

from src.pydal2sql.cli import app
from tests.mock_git import mock_git

# by default, click's cli runner mixes stdout and stderr for some reason...
runner = CliRunner(mix_stderr=False)


def test_cli_create():
    with mock_git():
        result = runner.invoke(app, ["create", "missing.py"])
        assert result.exit_code == 1
        assert "could not be found" in result.stderr

        result = runner.invoke(app, ["create", "magic.py"])
        assert result.exit_code == 1
        assert not result.stdout
        assert "missing some variables" in result.stderr

        result = runner.invoke(app, ["create", "magic.py", "--magic"])
        assert result.exit_code == 0
        assert not result.stderr
        assert "CREATE" in result.stdout

        result = runner.invoke(app, ["--verbosity", "3", "create", "magic.py@latest", '--magic'])
        assert result.exit_code == 0
        assert "generate_sql(" in result.stderr
        assert "empty = Empty()" in result.stderr
        assert "CREATE" in result.stdout

        result = runner.invoke(app, ["create", "magic.py@latest", '--noop'])
        assert result.exit_code == 0
        assert not result.stdout
        assert "empty = Empty()" not in result.stderr
        assert "generate_sql(" in result.stderr

def test_cli_alter():
    with mock_git():
        result = runner.invoke(app, ["alter", "missing.py"])
        assert result.exit_code == 1
        assert "does not exist" in result.stderr

        Path("empty.py").touch()

        result = runner.invoke(app, ["alter", "empty.py@current", "magic.py"])
        assert result.exit_code == 1
        assert "is empty" in result.stderr

        result = runner.invoke(app, ["alter", "magic.py@latest", "magic.py@latest"])
        assert result.exit_code == 1
        assert "contain the same code" in result.stderr

        result = runner.invoke(app, ["alter", "magic.py"])
        assert result.exit_code == 0

def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "pydal2sql version" in result.stdout.lower()


def test_cli_config():
    result = runner.invoke(app, ["--show-config", "--verbosity", "4"])
    assert result.exit_code == 0
    assert "ApplicationState(" in result.stdout
    assert "verbosity=<Verbosity.debug: '4'>" in result.stdout

# import pytest
#
# from src.pydal2sql.cli import handle_cli_create, CliConfig
# from src.pydal2sql.magic import find_missing_variables
#
#
# def test_cli(capsys):
#     code = """
#     db.define_table(
#         "person",
#         Field(
#             "name",
#             "string",
#             notnull=True,
#         ),
#         Field("age", "integer", default=18),
#         Field("float", "decimal(2,3)"),
#         Field("nicknames", "list:string"),
#         Field("obj", "json"),
#     )
#
#     """
#
#     with pytest.raises(ValueError):
#         handle_cli_create(
#             code,
#             None,  # <- not yet set in code so error
#             None,
#         )
#
#     code += 'db_type = "sqlite";'
#
#     handle_cli_create(
#         code,
#         None,  # <- set in code so no error
#         None,
#     )
#     captured = capsys.readouterr()
#
#     assert "InnoDB" not in captured.out
#     assert "CREATE TABLE" in captured.out
#
#     code += 'db_type = "mysql";'
#
#     handle_cli_create(
#         code,
#         None,  # <-  set in code so no error
#         None,
#     )
#     captured = capsys.readouterr()
#
#     assert "CREATE TABLE" in captured.out
#     assert "InnoDB" in captured.out
#     assert "db.define_table(" not in captured.out
#     assert "db.define_table(" not in captured.err
#
#     handle_cli_create(
#         code,
#         None,  # <-  set in code so no error
#         None,
#         verbose=True,
#         noop=True,
#     )
#     captured = capsys.readouterr()
#
#     assert "CREATE TABLE" not in captured.out
#     assert "CREATE TABLE" not in captured.err
#     assert "db.define_table(" in captured.err
#
#
# def test_cli_guess_sqlite(capsys):
#     code = """
#        db = DAL('sqlite://:memory:', migrate=False)
#
#        db.define_table(
#            "person",
#            Field(
#                "name",
#                "string",
#                notnull=True,
#            ),
#            Field("age", "integer", default=18),
#            Field("float", "decimal(2,3)"),
#            Field("nicknames", "list:string"),
#            Field("obj", "json"),
#        )
#        """
#
#     handle_cli_create(
#         code,
#         None,  # <-  set in code so no error
#         None
#     )
#     captured = capsys.readouterr()
#
#     print(captured.err)
#
#     assert "CREATE TABLE" in captured.out
#
#
# def test_magic(capsys):
#     code_with_imports = """
#     # 🪄 ✨
#     import math
#     from math import ceil
#     from typing import *
#
#     # floor should be unkown
#
#     numbers: Iterable = [1,2,3]
#
#     math.ceil(max(numbers))
#     ceil(max(numbers))
#     floor(max(numbers))
#
#     db.define_table('empty')
#
#     db_type = 'pymysql'
#     """
#
#     handle_cli_create(code_with_imports)
#     captured = capsys.readouterr()
#
#     assert "Your code is missing some variables: {'floor'}" in captured.err
#
#     handle_cli_create(code_with_imports, magic=True, verbose=True)
#     captured = capsys.readouterr()
#
#     assert 'CREATE TABLE' in captured.out
#     assert "Empty()" in captured.err
#
#     with_syntax_error = """
#     if true:
#     print('bye'
#     """
#
#     with pytest.raises(SyntaxError):
#         handle_cli_create(with_syntax_error, magic=True)
#     with pytest.raises(SyntaxError):
#         find_missing_variables(with_syntax_error)
#
#     with_del = """
#     del a
#     print(a)
#     """
#
#     # unfixable so magic = False here
#     handle_cli_create(with_del, magic=False)
#     captured = capsys.readouterr()
#
#     assert "{'a'}" in captured.err
#
#
# def test_config():
#     config = CliConfig.load()
#
#     assert 'CliConfig' in repr(config)  # version with colors
#     assert 'CliConfig(' in str(config)  # text-only version
