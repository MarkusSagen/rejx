# RejX

Deal with `.rej` files with reasonable pain

The application is designed to work with .rej files generated during patch application failures or from updating git templates using tools s.a. `cookiecutter` or `cruft`

It provides functionality to either fix these files individually or in bulk, view differences, list them, and clean them up.

The rich library is used for better console output formatting, providing a more user-friendly and visually appealing interface.

It's important to use the commands cautiously, especially fix_all and clean, as they perform bulk operations.

This documentation provides a clear guide on how to interact with the rejx Typer application, making it easier for users to understand and utilize its functionalities.

## Setup

```shell
# Pip
pip install rejx

# Poetry
poetry add rejx
```

## Usage

Your Python Typer application, rejx, provides a command line interface (CLI) for managing .rej files, which are typically generated when patches fail to apply cleanly. Below, I'll detail each command, its purpose, and how to use it, including optional arguments.

### `fix`

Purpose: Applies the changes from one or more specified .rej file to their corresponding original file.
Usage:

`rejx fix path/to/file1.rej path/to/file2.rej ...`

Passing the optional flag `--all` applies the changes from all .rej files to their corresponding original files. Usage:
`rejx fix --all`

### `diff`

Purpose: Displays the differences between the current file(s) and the changes proposed in the corresponding .rej file(s).
Usage:

`rejx diff <filename1> <filename2> ...`

If no file name is passed, this displays the difference for all .rej files.

Note: This command uses a pager for output. Use arrow keys or Vim bindings to navigate, and q to quit.

### `ls`

Purpose: Lists all .rej files in the current directory and subdirectories. By default, it lists files, but can also display them in a tree structure.
Usage:
For listing files:

`rejx ls`

For tree view:

`rejx ls --view tree`

For list view (default):

`rejx ls --view list`

### `clean`

Purpose: Deletes specified .rej files. It has an optional preview feature.
Usage:

`rejx clean path/to/file1.rej path/to/file2.rej ...`

With preview:

`rejx clean path/to/file1.rej path/to/file2.rej ... --preview`

By passing the optional `--all` flag, this command deletes all the .rej files in the current directory and subdirectories.
Usage:
`rejx clean --all`

This can be combined with the `--preview` option.
Usage:
`rejx clean --all --preview`

______________________________________________________________________
