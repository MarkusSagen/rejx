# RejX

Deal with `.rej` files with reasonable pain

The application is designed to work with .rej files generated during patch application failures or from updating git templates using tools s.a. `cookiecutter` or `cruft`

It provides functionality to either fix these files individually or in bulk, view differences, list them, and clean them up.

The rich library is used for better console output formatting, providing a more user-friendly and visually appealing interface.

It's important to use the commands cautiously, especially fix_all and clean, as they perform bulk operations.

This documentation provides a clear guide on how to interact with the rejx Typer application, making it easier for users to understand and utilize its functionalities.

<img width="825" alt="Screenshot 2024-10-12 at 10 08 31" src="https://github.com/user-attachments/assets/25ff2011-74f4-494a-9199-b3fac219185b">

## Installation

```shell
# Pip
pip install rejx

# Poetry
poetry add rejx
```

## Usage

Your Python Typer application, rejx, provides a command line interface (CLI) for managing .rej files, which are typically generated when patches fail to apply cleanly. Below, I'll detail each command, its purpose, and how to use it, including optional arguments.

Most rejx commands support the flags:

- `--all` - Recursively apply the command in subfolders
- `--preview` - Preview what a command would do before applying
- `--show-hidden` - Include hidden files (`.file`) when applying the command
- `--exclude-hidden` - Exclude hidden files from command

For more details, rejx provides help for each commands

```sh
rejx --help
rejx <command> --help
```

### `fix`

Applies the changes from one or more specified `.rej` file to their corresponding original file.

`rejx fix path/to/file1.rej path/to/file2.rej ...`

Passing the optional flag `--all` applies the changes from all .rej files to their corresponding original files.

`rejx fix --all`

### `diff`

Displays the differences between the current file(s) and the changes proposed in the corresponding .rej file(s).

`rejx diff <filename1> <filename2> ...`

If no file name is passed, this displays the difference for all .rej files.

[!NOTE] This command uses a pager for output. Use arrow keys or Vim bindings to navigate, and q to quit.

### `ls`

Lists all .rej files in the current directory and subdirectories. By default, it lists files, but can also display them in a tree structure.
For listing files:

`rejx ls .`

The ls command supports different view modes.
Default view is a list of files, but there's also a tree view mode

For tree view:

`rejx ls . --view tree`
`rejx tree .`

### `clean`

Deletes specified .rej files. It has an optional preview feature.
The preview flag makes it possible to _preview_ which files would be staged for deletion before
applying it.

`rejx clean path/to/file1.rej path/to/file2.rej ...`

With preview:

`rejx clean path/to/file1.rej path/to/file2.rej ... --preview`

By passing the optional `--all` flag, this command deletes all the .rej files in the current directory and subdirectories.

`rejx clean . --all`

This can be combined with the `--preview` option.

`rejx clean . --all --preview`

## Shell Completion

To install shell completion for rejx commands

```sh
rejx --install-completion && exec $SHELL
```

______________________________________________________________________

## Dev

For developers looking to apply changes or contribute changes, install the project with the just
command

This will install the project, pre-commit and the dev dependencies

```sh
just setup
```
