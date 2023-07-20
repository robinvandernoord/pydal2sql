"""
Main functionality.
"""

import typing

import pydal
from pydal.adapters import MySQL, Postgre, SQLAdapter, SQLite
from pydal.migrator import Migrator
from pydal.objects import Table

from .helpers import TempdirOrExistingDir, get_typing_args
from .types import SUPPORTED_DATABASE_TYPES, SUPPORTED_DATABASE_TYPES_WITH_ALIASES


def _build_dummy_migrator(_driver_name: SUPPORTED_DATABASE_TYPES_WITH_ALIASES, /, db_folder: str) -> Migrator:
    """
    Create a Migrator specific to the sql dialect of _driver_name.
    """
    db = pydal.DAL(None, migrate=False, folder=db_folder)

    aliases = {
        "postgresql": "psycopg2",
        "postgres": "psycopg2",
        "psql": "psycopg2",
        "sqlite": "sqlite3",
        "mysql": "pymysql",
    }

    driver_name = _driver_name.lower()
    driver_name = aliases.get(driver_name, driver_name)

    if driver_name not in get_typing_args(SUPPORTED_DATABASE_TYPES):
        raise ValueError(
            f"Unsupported database type {driver_name}. "
            f"Choose one of {get_typing_args(SUPPORTED_DATABASE_TYPES_WITH_ALIASES)}"
        )

    adapters_per_database: dict[str, typing.Type[SQLAdapter]] = {
        "psycopg2": Postgre,
        "sqlite3": SQLite,
        "pymysql": MySQL,
    }

    adapter = adapters_per_database[driver_name]

    installed_driver = db._drivers_available.get(driver_name)

    if not installed_driver:  # pragma: no cover
        raise ValueError(f"Please install the correct driver for database type {driver_name}")

    class DummyAdaptor(SQLAdapter):  # type: ignore
        types = adapter.types
        driver = installed_driver
        dbengine = adapter.dbengine

    adapter = DummyAdaptor(db, "", adapter_args={"driver": installed_driver})
    return Migrator(adapter)


def generate_sql(
    define_table: Table, db_type: SUPPORTED_DATABASE_TYPES_WITH_ALIASES = None, *, db_folder: str = None
) -> str:
    """
    Given a Table object (result of `db.define_table('mytable')` or simply db.mytable) \
        and a db type (e.g. postgres, sqlite, mysql), generate the `CREATE TABLE` SQL for that dialect.

    If no db_type is supplied, the type is guessed from the specified table.
        However, your db_type can differ from the current database used.
        You can even use a dummy database to generate SQL code with:
        `db = pydal.DAL(None, migrate=False)`

    db_folder is the database folder where migration (`.table`) files are stored.
        By default, a random temporary dir is created.
    """
    if not db_type:
        db_type = getattr(define_table._db, "_dbname", None)

        if db_type is None:
            raise ValueError("Database dialect could not be guessed from code; Please manually define a database type!")

    with TempdirOrExistingDir(db_folder) as db_folder:
        migrator = _build_dummy_migrator(db_type, db_folder=db_folder)

        sql: str = migrator.create_table(
            define_table,
            migrate=True,
            fake_migrate=True,
        )
        return sql
