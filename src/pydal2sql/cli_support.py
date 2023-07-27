"""
CLI-Agnostic support.
"""
import io
import os
import select
import string
import sys
import textwrap
import typing
from pathlib import Path

from typing import Optional, Any

import git
import rich
from black import find_project_root

from .helpers import flatten
from .magic import find_missing_variables, generate_magic_code


def has_stdin_data() -> bool:  # pragma: no cover
    """
    Check if the program starts with cli data (pipe | or redirect ><).

    See Also:
        https://stackoverflow.com/questions/3762881/how-do-i-check-if-stdin-has-some-data
    """
    return any(
        select.select(
            [
                sys.stdin,
            ],
            [],
            [],
            0.0,
        )[0]
    )


def find_git_root() -> Optional[Path]:
    folder, reason = find_project_root(None)
    if reason != ".git directory":
        return None
    return folder


def find_git_repo(repo: git.Repo = None) -> git.Repo:
    if repo:
        return repo

    root = find_git_root()
    return git.Repo(str(root))


def latest_commit(repo: git.Repo = None) -> git.Commit:
    repo = find_git_repo(repo)
    return repo.head.commit


def commit_by_id(commit_hash: str, repo: git.Repo = None) -> git.Commit:
    repo = find_git_repo(repo)
    return repo.commit(commit_hash)


def get_file_for_commit(filename: str, commit_version="latest", repo: git.Repo = None) -> str:
    repo = find_git_repo(repo)
    if commit_version == "latest":
        commit = latest_commit(repo)
    else:
        commit = commit_by_id(commit_version, repo)

    file_path = str(Path(filename).resolve())
    # relative to the .git folder:
    relative_file_path = file_path.removeprefix(f"{repo.working_dir}/")

    file_at_commit: git.objects.blob.Blob = commit.tree / relative_file_path

    with io.BytesIO(file_at_commit.data_stream.read()) as f:
        return f.read().decode('utf-8')


def handle_cli(
    code: str,
    db_type: Optional[str] = None,
    tables: Optional[list[str] | list[list[str]]] = None,
    verbose: Optional[bool] = False,
    noop: Optional[bool] = False,
    magic: Optional[bool] = False,
) -> None:
    """
    Handle user input.
    """
    to_execute = string.Template(
        textwrap.dedent(
            """
        from pydal import *
        from pydal.objects import *
        from pydal.validators import *

        from pydal2sql import generate_sql

        db = database = DAL(None, migrate=False)

        tables = $tables
        db_type = '$db_type'

        $extra

        $code

        if not tables:
            tables = db._tables

        for table in tables:
            print(generate_sql(db[table], db_type=db_type))
    """
        )
    )

    generated_code = to_execute.substitute(
        {"tables": flatten(tables or []), "db_type": db_type or "", "code": textwrap.dedent(code), "extra": ""}
    )
    if verbose or noop:
        rich.print(generated_code, file=sys.stderr)

    if not noop:
        try:
            exec(generated_code)  # nosec: B102
        except NameError:
            # something is missing!
            missing_vars = find_missing_variables(generated_code)
            if not magic:
                rich.print(
                    f"Your code is missing some variables: {missing_vars}. Add these or try --magic", file=sys.stderr
                )
            else:
                extra_code = generate_magic_code(missing_vars)

                generated_code = to_execute.substitute(
                    {
                        "tables": flatten(tables or []),
                        "db_type": db_type or "",
                        "extra": extra_code,
                        "code": textwrap.dedent(code),
                    }
                )

                if verbose:
                    print(generated_code, file=sys.stderr)

                exec(generated_code)  # nosec: B102
