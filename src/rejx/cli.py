"""CLI commands for rejx."""

from __future__ import annotations

import glob
import logging
import os
import pathlib
import re
from difflib import unified_diff
from typing import Optional

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich.text import Text
from rich.tree import Tree

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

app = typer.Typer()


def find_rej_files() -> list[str]:
    """Finds all .rej files in the current directory and its subdirectories.

    Returns:
    -------
        list[str]: A list of file paths to the found .rej files.

    Example:
    -------
        ```python
        rej_files = find_rej_files()
        print(rej_files)  # Prints paths to all .rej files.
        ```
    """
    return glob.glob("**/*.rej", recursive=True)


def parse_rej_file(rej_file_path: str) -> list[str]:
    """Parses a .rej file and returns its lines.

    Args:
    ----
        rej_file_path (str): The path to the .rej file.

    Returns:
    -------
        list[str]: A list of lines from the .rej file.

    Raises:
    ------
        typer.Exit: If the .rej file is not found.

    Example:
    -------
        ```python
        rej_lines = parse_rej_file("path/to/file.rej")
        print(rej_lines)  # Prints the contents of the .rej file.
        ```
    """
    try:
        with open(rej_file_path, encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        logging.exception(f"File not found: {rej_file_path}")
        raise typer.Exit from FileNotFoundError


def apply_changes(target_lines: list[str], rej_lines: list[str]) -> list[str]:
    """Applies the changes from .rej file lines to the target file's lines.

    Args:
    ----
        target_lines (list[str]): The lines from the target file.
        rej_lines (list[str]): The lines from the .rej file.

    Returns:
    -------
        list[str]: The modified lines after applying the .rej file changes.

    Example:
    -------
        ```python
        target_lines = ["line1", "line2", "line3"]
        rej_lines = ["@@ -1,1 +1,1 @@", "- line1", "+ line1_modified"]
        modified_lines = apply_changes(target_lines, rej_lines)
        print(modified_lines)  # Prints the modified lines.
        ```
    """
    line_info_regex = r"@@ -(\d+),(\d+) \+(\d+),(\d+) @@"
    hunk_start = 0
    new_lines = []
    current_hunk_changes = []
    processing_hunk = False

    for line in rej_lines:
        if line.startswith("@@"):
            # Process the previous hunk
            if processing_hunk:
                # Replace the lines in the target file for this hunk
                new_lines.extend(current_hunk_changes)
                current_hunk_changes = []

            # Parse hunk header
            matches = re.search(line_info_regex, line)
            if matches:
                hunk_start = int(matches.group(1)) - 1
                processing_hunk = True

                # Add lines from the target file up to the start of this hunk
                new_lines.extend(target_lines[len(new_lines) : hunk_start])
                continue

        chunks_not_in_rej_file = len(new_lines) + len(current_hunk_changes) < len(
            target_lines,
        )

        if processing_hunk:
            if line.startswith("+"):
                # Added lines
                current_hunk_changes.append(line[1:].rstrip("\n") + "\n")
            # Context line: keep this line from the original file
            elif not line.startswith("-") and chunks_not_in_rej_file:
                current_hunk_changes.append(
                    target_lines[len(new_lines) + len(current_hunk_changes)],
                )

    # Apply the last hunk
    if processing_hunk:
        new_lines.extend(current_hunk_changes)

    # Add any remaining lines from the original file
    new_lines.extend(target_lines[len(new_lines) :])

    return new_lines


def process_rej_file(rej_file_path: str) -> bool:
    """Processes a .rej file by applying its changes to the corresponding original file.

    Args:
    ----
        rej_file_path (str): The path to the .rej file.

    Returns:
    -------
        bool: True if the process is successful, False otherwise.

    Example:
    -------
        ```python
        success = process_rej_file("path/to/file.rej")
        if success:
            print("Changes applied successfully.")
        else:
            print("Failed to apply changes.")
        ```
    """
    success = False

    try:
        target_file_path = rej_file_path.replace(".rej", "")
        rej_lines = parse_rej_file(rej_file_path)
        with open(target_file_path, encoding="utf-8") as file:
            target_lines = file.readlines()

        modified_lines = apply_changes(target_lines, rej_lines)

        with open(target_file_path, "w", encoding="utf-8") as file:
            file.writelines(modified_lines)

        logging.info(f"Applied changes from {rej_file_path} to {target_file_path}")
        success = True
    except Exception:
        logging.exception(f"Error processing {rej_file_path}")

    return success


@app.command()
def fix(rej_file_path: str) -> None:
    """Applies changes from a specified .rej file to its corresponding original file.

    Args:
    ----
        rej_file_path (str): The path to the .rej file to be processed.

    Example:
    -------
        To fix a specific .rej file, run:
        ```bash
        rejx fix path/to/file.rej
        ```
    """
    process_rej_file(rej_file_path)


@app.command()
def fix_all() -> None:
    """Searches for and applies changes from all .rej files in the current directory and subdirectories.

    Example:
    -------
        To fix all .rej files found in the current and subdirectories, run:
        ```bash
        rejx fix_all
        ```
    """
    for rej_file in find_rej_files():
        process_rej_file(rej_file)


@app.command()
def diff() -> None:
    """Displays the diff of changes proposed by .rej files against their corresponding original files.

    Example:
    -------
        To display diffs for all .rej files, run:
        ```bash
        rejx diff
        ```
    """
    console = Console()
    file_logs = []

    for rej_file in find_rej_files():
        try:
            target_file_path = rej_file.replace(".rej", "")
            rej_lines = parse_rej_file(rej_file)
            with open(target_file_path, encoding="utf-8") as file:
                target_lines = file.readlines()

            modified_lines = apply_changes(target_lines.copy(), rej_lines)
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
            logging.exception(f"Error in previewing {rej_file}")

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


def build_file_tree(rej_files: list) -> Tree:
    """Constructs a tree structure representing the hierarchy of the provided .rej files.

    This tree structure visually organizes the .rej files based on their directory structure.
    It is used primarily for displaying the files in a tree format when using the `ls` command with the `--view tree` option.

    Args:
    ----
        rej_files (list): A list of file paths to .rej files.

    Returns:
    -------
        Tree: A rich Tree object representing the hierarchy of .rej files.

    Example:
    -------
        This function is generally not called directly by the user but used as part of the `ls` command:
        ```bash
        rejx ls --view tree
        ```
        Internally, it would be used as follows:
        ```python
        rej_files = find_rej_files()
        tree = build_file_tree(rej_files)
        console.print(tree)
        ```
    """
    tree = Tree(
        ":open_file_folder: Rejected Files Tree",
        guide_style="bold bright_blue",
    )
    node_dict = {}

    for rej_file in rej_files:
        path_parts = pathlib.Path(rej_file).parts
        current_node = tree

        for part in path_parts:
            key = os.path.join(
                *path_parts[: path_parts.index(part) + 1],
            )
            if key not in node_dict:
                # If part is a directory, color it blue/purple
                is_dir = part != path_parts[-1]
                style = "bold bright_blue" if is_dir else ""
                node_dict[key] = current_node.add(Text(part, style=style))
            current_node = node_dict[key]

    return tree


@app.command()
def ls(
    view: Optional[str] = typer.Option("list", help="View as 'list' or 'tree'"),
) -> None:
    """Lists all .rej files in the current directory and subdirectories.

    Supports different view formats.

    Args:
    ----
        view (Optional[str], optional): The view format. Can be 'list' or 'tree'. Defaults to 'list'.

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
    rej_files = find_rej_files()
    console = Console()

    if not rej_files:
        console.print("> :white_check_mark: No .rej files found")
        return

    if view == "list":
        for file in rej_files:
            console.print(file)
    elif view == "tree":
        tree = build_file_tree(rej_files)
        console.print(tree)
    else:
        console.print(f"[bold red]Invalid view option: {view}.[/bold red]")
        console.print("[bold]Usage: --view list|tree [/bold]")


@app.command()
def clean(
    preview: bool = typer.Option(
        False,
        help="Preview files before deleting",
    ),
) -> None:
    """Deletes all .rej files in the current directory and subdirectories.

    Optional preview before deletion.

    Args:
    ----
        preview (bool): If True, previews the files before deleting. Defaults to False.

    Example:
    -------
        - To delete all .rej files without preview, run:
          ```bash
          rejx clean
          ```
        - To preview files before deletion, run:
          ```bash
          rejx clean --preview
          ```
    """
    rej_files = find_rej_files()
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
