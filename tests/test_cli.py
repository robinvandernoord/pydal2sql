import pytest

from src.pydal2sql.cli import handle_cli


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
