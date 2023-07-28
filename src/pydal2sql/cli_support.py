"""
CLI-Agnostic support.
"""
import contextlib
import io
import os
import select
import string
import sys
import textwrap
import typing
from pathlib import Path
from typing import Optional

import rich
from black.files import find_project_root
from git.objects.blob import Blob
from git.objects.commit import Commit
from git.repo import Repo

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


AnyCallable = typing.Callable[..., typing.Any]


def print_if_interactive(*args: typing.Any, pretty: bool = True, **kwargs: typing.Any) -> None:
    is_interactive = not has_stdin_data()
    _print = typing.cast(AnyCallable, rich.print if pretty else print)  # make mypy happy
    if is_interactive:
        kwargs["file"] = sys.stderr
        _print(
            *args,
            **kwargs,
        )


def find_git_root(at: str = None) -> Optional[Path]:
    folder, reason = find_project_root((at or os.getcwd(),))
    if reason != ".git directory":
        return None
    return folder


def find_git_repo(repo: Repo = None, at: str = None) -> Repo:
    if repo:
        return repo

    root = find_git_root(at)
    return Repo(str(root))


def latest_commit(repo: Repo = None) -> Commit:
    repo = find_git_repo(repo)
    return repo.head.commit


def commit_by_id(commit_hash: str, repo: Repo = None) -> Commit:
    repo = find_git_repo(repo)
    return repo.commit(commit_hash)


@contextlib.contextmanager
def open_blob(file: Blob) -> typing.Generator[io.BytesIO, None, None]:
    yield io.BytesIO(file.data_stream.read())


def read_blob(file: Blob) -> str:
    with open_blob(file) as f:
        return f.read().decode()


def get_file_for_commit(filename: str, commit_version: str = "latest", repo: Repo = None) -> str:
    repo = find_git_repo(repo, at=filename)
    commit = latest_commit(repo) if commit_version == "latest" else commit_by_id(commit_version, repo)

    file_path = str(Path(filename).resolve())
    # relative to the .git folder:
    relative_file_path = file_path.removeprefix(f"{repo.working_dir}/")

    file_at_commit = commit.tree / relative_file_path
    return read_blob(file_at_commit)


def get_file_for_version(filename: str, version: str, prompt_description: str = "") -> str:
    if version == "current":
        return Path(filename).read_text()
    elif version == "stdin":
        print_if_interactive(
            f"[blue]Please paste your define tables ({prompt_description}) code below "
            f"and press ctrl-D when finished.[/blue]",
            file=sys.stderr,
        )
        result = sys.stdin.read()
        print_if_interactive("[blue]---[/blue]", file=sys.stderr)
        return result
    else:
        return get_file_for_commit(filename, version)


def extract_file_version_and_path(file_path_or_git_tag: Optional[str]) -> tuple[str, str | None]:
    """

    Examples:
        myfile.py (implies @current)

        myfile.py@latest
        myfile.py@my-branch
        myfile.py@b3f24091a9

        @latest (implies no path, e.g. in case of ALTER to copy previously defined path)
    """
    if not file_path_or_git_tag or file_path_or_git_tag == "-":
        return "stdin", "-"

    if file_path_or_git_tag.startswith("@"):
        file_version = file_path_or_git_tag.strip("@")
        file_path = None
    elif "@" in file_path_or_git_tag:
        file_path, file_version = file_path_or_git_tag.split("@")
    else:
        file_version = "latest"
        file_path = file_path_or_git_tag

    return file_version, file_path


def extract_file_versions_and_paths(
    filename_before: Optional[str], filename_after: Optional[str]
) -> tuple[tuple[str, str | None], tuple[str, str | None]]:
    version_before, filepath_before = extract_file_version_and_path(filename_before)
    version_after, filepath_after = extract_file_version_and_path(filename_after)

    if not (filepath_before or filepath_after):
        raise ValueError("Please supply at least one file name.")
    elif not filepath_after:
        filepath_after = filepath_before
    elif not filepath_before:
        filepath_before = filepath_after

    return (version_before, filepath_before), (version_after, filepath_after)


def get_absolute_path_info(filename: Optional[str], version: str, git_root: Optional[Path] = None) -> tuple[bool, str]:
    if version == "stdin":
        return True, ""
    elif filename is None:
        # can't deal with this, not stdin and no file should show file missing error later.
        return False, ""

    if git_root is None:
        git_root = find_git_root() or Path(os.getcwd())

    path = Path(filename)
    path_via_git = git_root / filename

    if path.exists():
        exists = True
        absolute_path = str(path.resolve())
    elif path_via_git.exists():
        exists = True
        absolute_path = str(path_via_git.resolve())
    else:
        exists = False
        absolute_path = ""

    return exists, absolute_path


def handle_cli_create(
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
                return

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
