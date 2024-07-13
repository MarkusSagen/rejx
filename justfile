set shell := ["bash", "-uc"]
set dotenv-load := true

RED := "\\033[31m"
GREEN := "\\033[32m"
PURPLE := "\\033[35m"
YELLOW := "\\033[33m"
BOLD := "\\033[1m"
RESET := "\\033[0m"
NC := "\\033[0m"

setup: _git-init _poetry
    #!/usr/bin/env bash
    # https://github.com/casey/just?tab=readme-ov-file#safer-bash-shebang-recipes
    set -euo pipefail

    poetry env use python
    poetry install
    just _pre-commit

check: _poetry
    poetry check -vvv

pre-commit: _pre-commit
    poetry run pre-commit run --all-files

format: _poetry
    poetry run ruff check --preview --fix .
    poetry run ruff format --preview .

lint: pre-commit
    @just fmt

codespell:
    poetry run pre-commit run codespell --all-files

# TODO: Added in doctest PR
# testdoc: _poetry
#     poetry run pytest -vv --doctest-modules --doctest-glob="*.md" --doctest-mdcodeblocks

testcov:
    @echo "running test coverage"
    @poetry run coverage run \
        --source=src/rejx \
        --omit="*/__init__.py,__main__.py,settings.py" \
        -m pytest -vv --durations=10 --disable-warnings tests
    @echo "building coverage report"
    @poetry run coverage report
    @echo "building coverage html"
    @poetry run coverage html
    @echo "building coverage lcov"
    @poetry run coverage lcov

test: testcov codespell

# TODO: Added in doctest PR
# test: testcov codespell testdoc

docs: _poetry
    poetry run mkdocs build --strict

clean:
    @echo 'cleaning up cached files from python ".pyc, .pyo, __pycache__/"'
    find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
    @echo 'cleaning up the data directory'
    find data -type f ! -name ".gitkeep" ! -path "data/01_raw/tests/*" -delete

# Clean tmp files and .venv folder
deepclean: clean
    @echo 'removing .venv folder'
    rm -rf .venv

################################################################
# Setup
################################################################

_git-init:
    @if [ ! -d ".git" ]; then \
        git init > /dev/null 2>&1; \
    fi

_poetry:
    @poetry --version || echo "Poetry is not installed. Please install poetry"

_pre-commit: _poetry
    poetry run pre-commit install
    poetry run pre-commit install --hook-type commit-msg
    poetry run pre-commit install --install-hooks

################################################################
# Template formatting
################################################################

# Format justfile
fmt check="":
    just --unstable --fmt {{ check }}
