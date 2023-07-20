# pydal2sql

[![PyPI - Version](https://img.shields.io/pypi/v/pydal2sql.svg)](https://pypi.org/project/pydal2sql)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydal2sql.svg)](https://pypi.org/project/pydal2sql)  
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  
[![su6 checks](https://github.com/robinvandernoord/pydal2sql/actions/workflows/su6.yml/badge.svg?branch=development)](https://github.com/robinvandernoord/pydal2sql/actions)
![coverage.svg](coverage.svg)

-----

Convert pydal define_tables to SQL using pydal's CREATE TABLE logic

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Example

```python
from pydal import DAL, Field
from pydal2sql import generate_sql

db = DAL(None, migrate=False)  # <- without running database or with a different type of database

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
),

print(
    generate_sql(
        db.person, db_type="psql"  # or sqlite, or mysql; Optional with fallback to currently using database type.
    )
)
```

```sql
CREATE TABLE person
(
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      VARCHAR(512),
    age       INTEGER,
    float     NUMERIC(2, 3),
    nicknames TEXT,
    obj       TEXT
);
```

## Installation

```console
pip install pydal2sql
```

## License

`pydal2sql` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
