import pydal
import pytest
from pydal import DAL, Field

from src.pydal2sql import SUPPORTED_DATABASE_TYPES, generate_sql
from src.pydal2sql.core import _build_dummy_migrator
from src.pydal2sql.helpers import TempdirOrExistingDir


def test_main():
    # folder = tempfile.TemporaryDirectory.name
    db = pydal.DAL(None, migrate=False)  # <- without running database or with a different type of database

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

    generated = {}

    for database_type in SUPPORTED_DATABASE_TYPES:
        generated[database_type] = sql = generate_sql(db.person, db_type=database_type)

        assert sql

        assert "id INTEGER PRIMARY KEY AUTOINCREMENT" in sql
        assert "name VARCHAR(512)" in sql
        assert "nicknames TEXT" in sql
        assert "age INTEGER" in sql

    # sqlite
    print(generated["sqlite3"])

    # psql
    print(generated["psycopg2"])

    # mysql
    assert "ENGINE=InnoDB CHARACTER SET utf8" in generated["pymysql"]


def test_invalid_dbtype():
    with pytest.raises(ValueError):
        with TempdirOrExistingDir() as temp_dir:
            _build_dummy_migrator("magicdb", db_folder=temp_dir)


def test_guess_db_type():
    with TempdirOrExistingDir() as temp_dir:
        db = DAL("sqlite://:memory:", folder=temp_dir)

        empty = db.define_table("empty")
        sql = generate_sql(empty)

        assert (
            sql.strip()
            == """CREATE TABLE "empty"(
    "id" INTEGER PRIMARY KEY AUTOINCREMENT
);""".strip()
        )
