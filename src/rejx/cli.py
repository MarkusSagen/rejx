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
from rejx.logger import logger

app = typer.Typer()


@app.command()
def fix(
    rej_files: list[str] = typer.Argument(default=None),
    apply_to_all_files: Optional[bool] = typer.Option(
        False,
        "--all",
        help="Apply changes from all .rej files.",
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
    """Applies changes from a specified .rej file to its corresponding original file.

    Args:
    ----
        rej_file (str): The path to the .rej file to be processed.
        apply_to_all_files (Optional[bool]): Determines whether all files should be fixed. Default: False.
        exclude_hidden (Optional[bool]): Determines whether to hide hidden files from output. Defaults to `False`
        ignore(Optional[List[str]]): List of regex patterns of directories to ignore rej files from.

    Example:
    -------
        To fix a specific .rej file, run:
        ```bash
        rejx fix path/to/file.rej
        ```

        To fix all files, run:
        ```bash
        rejx fix --all
        ```
    """
    if apply_to_all_files:
        for rej_file in rejx.utils.find_rej_files(
            exclude_hidden=exclude_hidden,
            ignore=ignore,
        ):
            rejx.utils.process_rej_file(rej_file)

    elif rej_files is None:
        logger.error("No file name specified")

    else:
        for rej_file in rej_files:
            rejx.utils.process_rej_file(rej_file)


@app.command()
def diff(
    rej_files: list[str] = typer.Argument(default=None),
    exclude_hidden: Optional[bool] = typer.Option(
        False,
        "--exclude-hidden",
        help="Hide hidden files.",
        show_default=False,
    ),
    ignore: Optional[list[str]] = typer.Option(None, "--ignore", help="Regex patterns to ignore directories"),
) -> None:
    """Displays the diff of changes proposed by .rej files against their corresponding original files.

    Displays the diff for all .rej files If no file names are specified.

    Args:
    -----
        rej_files (list[str]): Rej files to apply diff.
        exclude_hidden (Optional[bool]): Determines whether to hide hidden files from output. Defaults to `False`
        ignore(Optional[List[str]]): List of regex patterns of directories to ignore rej files from.

    Example:
    -------
        To display diffs for all .rej files, run:
        ```bash
        rejx diff
        ```
    """
    if rej_files is None:
        rej_files = rejx.utils.find_rej_files(
            exclude_hidden=exclude_hidden,
            ignore=ignore,
        )

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
            console.rule(f"\n{logs['filename']}\n", align="left")
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
def ls(
    exclude_hidden: Optional[bool] = typer.Option(
        False,
        "--exclude-hidden",
        help="Hide hidden files.",
        show_default=False,
    ),
    ignore: Optional[list[str]] = typer.Option(None, "--ignore", help="Regex patterns to ignore directories"),
    view: Optional[str] = typer.Option("list", help="View as 'list' or 'tree'"),
) -> None:
    """Lists all .rej files in the current directory and subdirectories.

    Supports different view formats.

    Args:
    ----
        exclude_hidden (Optional[bool]): Determines whether to hide hidden files from output. Defaults to `False`
        ignore(Optional[List[str]]): List of regex patterns of directories to ignore rej files from.
        view (Optional[str]): The view format. Can be 'list' or 'tree'. Defaults to 'list'.

    Example:
    -------
        - To list .rej files in list format, run:
          ```bash
          rejx ls
          ```
        - To display .rej files in a tree structure, run:
          ```bash
          rejx ls --view tree
          ```
    """
    rej_files = rejx.utils.find_rej_files(
        exclude_hidden=exclude_hidden,
        ignore=ignore,
    )
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
def clean(
    rej_files: list[str] = typer.Argument(default=None),
    apply_to_all_files: Optional[bool] = typer.Option(
        False,
        "--all",
        help="Apply changes from all .rej files.",
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
    """Deletes one or all .rej files in the current directory and subdirectories.

    Optional preview before deletion.

    Args:
    ----
        rej_files (Optional, List[str]): a list of names of files to be deleted.
        apply_to_all_files (Optional, bool): determines if all files should be removed. Defaults to "False".
        preview (bool): If True, previews the files before deleting. Defaults to False.
        exclude_hidden (Optional[bool]): Determines whether to hide hidden files from output. Defaults to `False`
        ignore(Optional[List[str]]): List of regex patterns of directories to ignore rej files from.

    Example:
    -------
        - To delete a file file.txt.rej without preview, run:
        ```bash
        rejx clean file.txt.rej
        ```
        - To delete all .rej files without preview, run:
          ```bash
          rejx clean --all
          ```
        - To preview files before deletion, run:
          ```bash
          rejx clean --all --preview
          ```
    """
    if apply_to_all_files:
        rej_files = rejx.utils.find_rej_files(
            exclude_hidden=exclude_hidden,
            ignore=ignore,
        )

    elif rej_files is None:
        logger.error("No filename specified.")

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
