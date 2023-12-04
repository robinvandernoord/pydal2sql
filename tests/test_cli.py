"""
Todo: test with Typer
"""
from pathlib import Path

from contextlib_chdir import chdir
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

        result = runner.invoke(app, ["create", "magic.py@latest"])
        assert result.exit_code == 1
        assert not result.stdout
        assert "missing some variables" in result.stderr

        result = runner.invoke(app, ["create", "magic.py@current"])
        assert result.exit_code == 1
        assert not result.stdout
        assert "db defined in code!" in result.stderr

        result = runner.invoke(app, ["create", "magic.py", "--magic"])
        assert result.exit_code == 0
        assert "success" in result.stderr
        assert "CREATE" in result.stdout

        result = runner.invoke(app, ["--verbosity", "3", "create", "magic.py@latest", "--magic"])
        assert result.exit_code == 0
        assert "generate_sql(" in result.stderr
        assert "empty = Empty()" in result.stderr
        assert "CREATE" in result.stdout

        result = runner.invoke(app, ["create", "magic.py@latest", "--noop"])
        assert result.exit_code == 0
        assert not result.stdout
        assert "empty = Empty()" not in result.stderr
        assert "generate_sql(" in result.stderr


def test_cli_alter():
    with mock_git():
        result = runner.invoke(app, ["alter", "missing.py", "missing2.py"])
        assert result.exit_code == 1
        assert "does not exist" in result.stderr
        assert "missing.py" in result.stderr
        assert "missing2.py" in result.stderr

        Path("empty.py").touch()

        result = runner.invoke(app, ["alter", "empty.py@current", "magic.py"])
        assert result.exit_code == 1
        assert "is empty" in result.stderr

        result = runner.invoke(app, ["alter", "magic.py@latest", "magic.py@latest"])
        assert result.exit_code == 1
        assert "contain the same code" in result.stderr

        result = runner.invoke(app, ["alter", "magic.py", "--magic"])
        print("++ stdout", result.stdout)
        print("++ stderr", result.stderr)
        assert result.exit_code == 0
        assert result.stdout

        syntax_error = Path("syntax.py")
        syntax_error.write_text("0/0")

        result = runner.invoke(app, ["alter", "empty.py", "syntax.py"])
        assert result.exit_code == 1
        assert "alter failed" in result.stderr

        print(result.stderr)


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "pydal2sql version" in result.stdout.lower()


def test_cli_config():
    result = runner.invoke(app, ["--show-config", "--verbosity", "4"])
    assert result.exit_code == 0
    assert "ApplicationState(" in result.stdout
    assert "verbosity=<Verbosity.debug: '4'>" in result.stdout


def test_with_import():
    with chdir("./pytest_examples"):
        result = runner.invoke(app, ["create", "magic_with_import.py", "--no-magic", "--db-type", "sqlite"])
        assert result.exit_code == 1
        assert "Local imports are used in this file" in result.stderr

        result = runner.invoke(app, ["create", "magic_with_import.py", "--magic", "--db-type", "sqlite"])

        assert result.exit_code == 0

        assert 'success' in result.stderr
        assert "CREATE TABLE something" in result.stdout or 'CREATE TABLE "something"' in result.stdout


def test_with_function():
    with chdir("./pytest_examples"):
        # result = runner.invoke(app, ["create", "magic_with_function.py", "--magic", "--function", "define_tables"])
        # assert result.exit_code == 0
        #
        # assert not result.stderr
        # assert "CREATE TABLE empty" in result.stdout

        result = runner.invoke(
            app,
            [
                "create",
                "magic_with_function.py",
                "--magic",
                "--db-type",
                "sqlite",
                "--function",
                "define_tables_multiple_arguments(db, 'empty')",
            ],
        )
        assert result.exit_code == 0

        assert 'success' in result.stderr
        assert "CREATE TABLE empty" in result.stdout or 'CREATE TABLE "empty"' in result.stdout
