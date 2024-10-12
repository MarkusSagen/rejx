"""CLI commands for rejx."""

from __future__ import annotations

import pathlib
from difflib import unified_diff
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich.text import Text

import rejx.utils
from rejx.logger import logger, setup_logger

app = typer.Typer()

setup_logger()


@app.command()
def fix(
    path: str = typer.Argument(default=".", help="Path to start searching for .rej files"),
    apply_to_all_files: Optional[bool] = typer.Option(
        False,
        "--all",
        help="Apply changes to all .rej files in the specified path and its subdirectories.",
        show_default=False,
    ),
    exclude_hidden: Optional[bool] = typer.Option(
        False,
        "--exclude-hidden",
        help="Hide hidden files.",
        show_default=False,
    ),
    ignore: Optional[list[str]] = typer.Option(None, "--ignore", help="Regex patterns to ignore directories"),
) -> None:
    """Applies changes from specified .rej files to their corresponding original files.

    Args:
    ----
        path (str): The path to start searching for .rej files. Defaults to current directory.
        apply_to_all_files (Optional[bool]): Determines whether all files should be fixed. Default: False.
        exclude_hidden (Optional[bool]): Determines whether to hide hidden files from output. Defaults to `False`
        ignore(Optional[List[str]]): List of regex patterns of directories to ignore rej files from.

    Example:
    -------
        To fix a specific .rej file, run:
        ```bash
        rejx fix path/to/file.rej
        ```

        To fix all .rej files in the current directory and subdirectories, run:
        ```bash
        rejx fix --all
        ```

        To fix all .rej files in a specific directory and its subdirectories, run:
        ```bash
        rejx fix path/to/directory --all
        ```
    """
    if pathlib.Path(path).is_file() and not apply_to_all_files:
        rej_files = [path]
    elif pathlib.Path(path).is_dir() and apply_to_all_files:
        rej_files = rejx.utils.find_rej_files(
            path=path,
            exclude_hidden=exclude_hidden,
            ignore=ignore,
        )
    else:
        logger.error("Please specify a file or use --all with a directory path.")
        raise typer.Exit(1)

    if not rej_files:
        logger.error("No .rej files specified or found")
        return

    for rej_file in rej_files:
        if not rej_file.endswith(".rej"):
            logger.error(f"Skipping non-.rej file: {rej_file}")
            continue
        rejx.utils.process_rej_file(rej_file)


@app.command()
@app.command()
def diff(
    path: str = typer.Argument(default=".", help="Path to start searching for .rej files"),
    apply_to_all_files: Optional[bool] = typer.Option(
        False,
        "--all",
        help="Display diff for all .rej files in the specified path and its subdirectories.",
        show_default=False,
    ),
    exclude_hidden: Optional[bool] = typer.Option(
        False,
        "--exclude-hidden",
        help="Hide hidden files.",
        show_default=False,
    ),
    ignore: Optional[list[str]] = typer.Option(None, "--ignore", help="Regex patterns to ignore directories"),
) -> None:
    """Displays the diff of changes proposed by .rej files against their corresponding original files.

    Args:
    ----
        path (str): The path to start searching for .rej files. Defaults to current directory.
        apply_to_all_files (Optional[bool]): Determines whether to show diff for all .rej files recursively. Default: False.
        exclude_hidden (Optional[bool]): Determines whether to hide hidden files from output. Defaults to `False`
        ignore(Optional[List[str]]): List of regex patterns of directories to ignore rej files from.

    Example:
    -------
        To display diff for a specific .rej file:
        ```bash
        rejx diff path/to/file.rej
        ```
        To display diff for all .rej files in the current directory and subdirectories:
        ```bash
        rejx diff --all
        ```
    """
    if pathlib.Path(path).is_file() and not apply_to_all_files:
        rej_files = [path]
    elif pathlib.Path(path).is_dir():
        rej_files = rejx.utils.find_rej_files(
            path=path,
            exclude_hidden=exclude_hidden,
            ignore=ignore,
            recursive=apply_to_all_files,
        )
    else:
        logger.error("Please specify a valid file or directory path.")
        raise typer.Exit(1)

    console = Console()
    file_logs = []

    for rej_file in rej_files:
        try:
            target_file_path = rej_file.replace(".rej", "")
            rej_lines = rejx.utils.parse_rej_file(rej_file)
            with open(target_file_path, encoding="utf-8") as file:
                target_lines = file.readlines()

            modified_lines = rejx.utils.apply_changes(target_lines.copy(), rej_lines)
            diff = "".join(
                unified_diff(
                    target_lines,
                    modified_lines,
                    fromfile=target_file_path,
                    tofile=rej_file,
                    lineterm="",
                ),
            )

            file_logs.append({"filename": rej_file, "diff": diff})

        except Exception:  # noqa: PERF203
            logger.exception(f"Error in previewing {rej_file}")

    # Display diff
    with console.pager(styles=True):
        console.print(
            Text(
                "Diff Preview (use arrow keys or Vim bindings to navigate, q to quit)",
                style="bold blue",
            ),
        )

        for logs in file_logs:
            filename = logs["filename"]

            console.rule(f"\n{filename}\n", align="left")
            console.print(
                Syntax(
                    logs["diff"],
                    "diff",
                    theme="monokai",
                    word_wrap=True,
                    line_numbers=True,
                ),
                style="dim",
            )


@app.command()
@app.command()
def ls(
    path: str = typer.Argument(default=".", help="Path to start searching for .rej files"),
    apply_to_all_files: Optional[bool] = typer.Option(
        False,
        "--all",
        help="List all .rej files in the specified path and its subdirectories.",
        show_default=False,
    ),
    exclude_hidden: Optional[bool] = typer.Option(
        False,
        "--exclude-hidden",
        help="Hide hidden files.",
        show_default=False,
    ),
    ignore: Optional[list[str]] = typer.Option(None, "--ignore", help="Regex patterns to ignore directories"),
    view: Optional[str] = typer.Option("list", help="View as 'list' or 'tree'"),
) -> None:
    """Lists .rej files in the specified path.

    Supports different view formats.

    Args:
    ----
        path (str): The path to start searching for .rej files. Defaults to current directory.
        apply_to_all_files (Optional[bool]): Determines whether to list all .rej files recursively. Default: False.
        exclude_hidden (Optional[bool]): Determines whether to hide hidden files from output. Defaults to `False`
        ignore(Optional[List[str]]): List of regex patterns of directories to ignore rej files from.
        view (Optional[str]): The view format. Can be 'list' or 'tree'. Defaults to 'list'.

    Example:
    -------
        - To list .rej files in the current directory:
          ```bash
          rejx ls
          ```
        - To list all .rej files recursively:
          ```bash
          rejx ls --all
          ```
        - To list .rej files in a specific directory:
          ```bash
          rejx ls path/to/directory
          ```
    """
    if pathlib.Path(path).is_file() and not apply_to_all_files:
        rej_files = [path]
    elif pathlib.Path(path).is_dir():
        rej_files = rejx.utils.find_rej_files(
            path=path,
            exclude_hidden=exclude_hidden,
            ignore=ignore,
            recursive=apply_to_all_files,
        )
    else:
        logger.error("Please specify a valid directory path.")
        raise typer.Exit(1)

    console = Console()

    if not rej_files:
        console.print("> :white_check_mark: No .rej files found")
        return

    if view == "list":
        for file in rej_files:
            console.print(file)
    elif view == "tree":
        tree = rejx.utils.build_file_tree(rej_files)
        console.print(tree)
    else:
        console.print(f"[bold red]Invalid view option: {view}.[/bold red]")
        console.print("[bold]Usage: --view list|tree [/bold]")


@app.command()
def tree(
    path: str = typer.Argument(default=".", help="Path to start searching for .rej files"),
    apply_to_all_files: Optional[bool] = typer.Option(
        True,
        "--all",
        help="List all .rej files in the specified path and its subdirectories.",
        show_default=False,
    ),
    exclude_hidden: Optional[bool] = typer.Option(
        False,
        "--exclude-hidden",
        help="Hide hidden files.",
        show_default=False,
    ),
    ignore: Optional[list[str]] = typer.Option(None, "--ignore", help="Regex patterns to ignore directories"),
) -> None:
    """Displays .rej files in a tree structure.

    This is an alias for `rejx ls --view tree`.

    Args:
    ----
        path (str): The path to start searching for .rej files. Defaults to current directory.
        apply_to_all_files (Optional[bool]): Determines whether to list all .rej files recursively. Default: True.
        exclude_hidden (Optional[bool]): Determines whether to hide hidden files from output. Defaults to `False`
        ignore(Optional[List[str]]): List of regex patterns of directories to ignore rej files from.

    Example:
    -------
        To display .rej files in a tree structure:
        ```bash
        rejx tree
        ```
    """
    rej_files = rejx.utils.find_rej_files(
        path=path,
        exclude_hidden=exclude_hidden,
        ignore=ignore,
        recursive=apply_to_all_files,
    )
    tree = rejx.utils.build_file_tree(rej_files)
    console = Console()
    console.print(tree)


@app.command()
def clean(
    path: str = typer.Argument(default=".", help="Path to start searching for .rej files"),
    apply_to_all_files: Optional[bool] = typer.Option(
        False,
        "--all",
        help="Delete all .rej files in the specified path and its subdirectories.",
        show_default=False,
    ),
    preview: bool = typer.Option(
        False,
        help="Preview files before deleting",
    ),
    exclude_hidden: Optional[bool] = typer.Option(
        False,
        "--exclude-hidden",
        help="Hide hidden files.",
        show_default=False,
    ),
    ignore: Optional[list[str]] = typer.Option(None, "--ignore", help="Regex patterns to ignore directories"),
) -> None:
    """Deletes .rej files in the specified path.

    Optional preview before deletion.

    Args:
    ----
        path (str): The path to start searching for .rej files. Defaults to current directory.
        apply_to_all_files (Optional, bool): determines if all files should be removed. Defaults to "False".
        preview (bool): If True, previews the files before deleting. Defaults to False.
        exclude_hidden (Optional[bool]): Determines whether to hide hidden files from output. Defaults to `False`
        ignore(Optional[List[str]]): List of regex patterns of directories to ignore rej files from.

    Example:
    -------
        - To delete a specific .rej file without preview:
          ```bash
          rejx clean path/to/file.txt.rej
          ```
        - To delete all .rej files in the current directory and subdirectories:
          ```bash
          rejx clean --all
          ```
        - To preview files before deletion in a specific directory:
          ```bash
          rejx clean path/to/directory --all --preview
          ```
    """
    if pathlib.Path(path).is_file() and not apply_to_all_files:
        rej_files = [path]
    elif pathlib.Path(path).is_dir() and apply_to_all_files:
        rej_files = rejx.utils.find_rej_files(
            path=path,
            exclude_hidden=exclude_hidden,
            ignore=ignore,
        )
    else:
        logger.error("Please specify a file or use --all with a directory path.")
        raise typer.Exit(1)

    console = Console()

    if not rej_files:
        console.print("> :white_check_mark: No .rej files found")
        raise typer.Exit

    if preview:
        console.print("[bold red]These files will be deleted:[/bold red]")
        for file in rej_files:
            console.print(f" - {file}")
        if not Confirm.ask(
            "[bold yellow]Do you want to continue with deletion?[/bold yellow]",
        ):
            raise typer.Exit

    try:
        for file in rej_files:
            pathlib.Path(file).unlink()
            console.print(f"[green]Deleted:[/green] {file}")
    except Exception as e:
        console.print(f"[red]Error deleting {file}:[/red] {e}")

    console.print("[bold green]Deletion complete.[/bold green]")


if __name__ == "__main__":
    app()
