import pytest

from src.pydal2sql.cli import handle_cli, CliConfig
from src.pydal2sql.magic import find_missing_variables


def test_cli(capsys):
    code = """
    db.define_table(
        "person",
        Field(
            "name",
            "string",
            nullable=False,
        ),
        Field("age", "integer", default=18),
        Field("float", "decimal(2,3)"),
        Field("nicknames", "list:string"),
        Field("obj", "json"),
    )
    
    """

    with pytest.raises(ValueError):
        handle_cli(
            code,
            None,  # <- not yet set in code so error
            None,
        )

    code += 'db_type = "sqlite";'

    handle_cli(
        code,
        None,  # <- set in code so no error
        None,
    )
    captured = capsys.readouterr()

    assert "InnoDB" not in captured.out
    assert "CREATE TABLE" in captured.out

    code += 'db_type = "mysql";'

    handle_cli(
        code,
        None,  # <-  set in code so no error
        None,
    )
    captured = capsys.readouterr()

    assert "CREATE TABLE" in captured.out
    assert "InnoDB" in captured.out
    assert "db.define_table(" not in captured.out
    assert "db.define_table(" not in captured.err

    handle_cli(
        code,
        None,  # <-  set in code so no error
        None,
        verbose=True,
        noop=True,
    )
    captured = capsys.readouterr()

    assert "CREATE TABLE" not in captured.out
    assert "CREATE TABLE" not in captured.err
    assert "db.define_table(" in captured.err


def test_cli_guess_sqlite(capsys):
    code = """
       db = DAL('sqlite://:memory:', migrate=False)
    
       db.define_table(
           "person",
           Field(
               "name",
               "string",
               nullable=False,
           ),
           Field("age", "integer", default=18),
           Field("float", "decimal(2,3)"),
           Field("nicknames", "list:string"),
           Field("obj", "json"),
       )
       """

    handle_cli(
        code,
        None,  # <-  set in code so no error
        None
    )
    captured = capsys.readouterr()

    print(captured.err)

    assert "CREATE TABLE" in captured.out


def test_magic(capsys):
    code_with_imports = """
    # 🪄 ✨
    import math
    from math import ceil
    from typing import *
    
    # floor should be unkown
    
    numbers: Iterable = [1,2,3]
    
    math.ceil(max(numbers))
    ceil(max(numbers))
    floor(max(numbers))
    
    db.define_table('empty')
    
    db_type = 'pymysql'
    """

    handle_cli(code_with_imports)
    captured = capsys.readouterr()

    assert "Your code is missing some variables: {'floor'}" in captured.err

    handle_cli(code_with_imports, magic=True, verbose=True)
    captured = capsys.readouterr()

    assert 'CREATE TABLE' in captured.out
    assert "Empty()" in captured.err

    with_syntax_error = """
    if true:
    print('bye'
    """

    with pytest.raises(SyntaxError):
        handle_cli(with_syntax_error, magic=True)
    with pytest.raises(SyntaxError):
        find_missing_variables(with_syntax_error)

    with_del = """
    del a
    print(a)
    """

    # unfixable so magic = False here
    handle_cli(with_del, magic=False)
    captured = capsys.readouterr()

    assert "{'a'}" in captured.err


def test_config():
    config = CliConfig.load()

    assert 'CliConfig' in repr(config)  # version with colors
    assert 'CliConfig(' in str(config)  # text-only version
