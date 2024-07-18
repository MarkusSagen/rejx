"""Unittest for rejx."""
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

import rejx
from rejx import app

# Constants
TEST_DATA_DIR = Path(__file__).parent / "data"
SAMPLE_REJ_FILE = TEST_DATA_DIR / "sample.txt.rej"
SAMPLE_CONTENT = """--- sample.txt
+++ sample.txt
@@ -2,3 +2,3 @@
-Line 2
+Line 2 - Modified
Line 3
"""

runner = CliRunner()


@pytest.fixture()
def sample_rej_file():
    return str(TEST_DATA_DIR / "sample.txt.rej")


@pytest.fixture()
def sample_target_file():
    return str(TEST_DATA_DIR / "sample.txt")


@pytest.fixture(autouse=True)
def _setup_sample_rej_file() -> None:
    """Fixture to ensure the sample.txt.rej file is present and properly formatted for each test."""
    # Ensure the test data directory exists
    TEST_DATA_DIR.mkdir(exist_ok=True)

    # Write the content to sample.txt.rej
    with open(SAMPLE_REJ_FILE, "w", encoding="utf-8") as file:
        file.write(SAMPLE_CONTENT)

    # Cleanup (optional, depending on whether you want to keep the file after the test)


def test_find_rej_files():
    os.chdir(TEST_DATA_DIR)  # Change current directory to test data directory
    rej_files = rejx.find_rej_files()
    assert len(rej_files) > 0
    assert all(file.endswith(".rej") for file in rej_files)


def test_parse_rej_file(sample_rej_file: str):
    rej_lines = rejx.parse_rej_file(sample_rej_file)
    assert rej_lines is not None
    assert isinstance(rej_lines, list)


def test_apply_changes(sample_rej_file: str, sample_target_file: str):
    with open(sample_target_file, encoding="utf-8") as f:
        target_lines = f.readlines()
    rej_lines = rejx.parse_rej_file(sample_rej_file)
    modified_lines = rejx.apply_changes(target_lines, rej_lines)

    expected_lines = ["Line 1\n", "Line 2 - Modified\n", "Line 3\n"]

    assert modified_lines == expected_lines
    assert isinstance(modified_lines, list)


def test_process_rej_file(sample_rej_file: str):
    result = rejx.process_rej_file(sample_rej_file)
    assert result


#####################################
#                                   #
#           REJX COMMANDS           #
#                                   #
#####################################
def test_fix(sample_rej_file: str):
    result = runner.invoke(app, ["fix", sample_rej_file])
    assert result.exit_code == 0


def test_fix_all():
    result = runner.invoke(app, ["fix", "--all"])
    assert result.exit_code == 0


def test_ls():
    result = runner.invoke(app, ["ls"])
    assert result.exit_code == 0


def test_ls_list():
    result = runner.invoke(app, ["ls", "--view", "list"])
    assert result.exit_code == 0


def test_ls_tree():
    result = runner.invoke(app, ["ls", "--view", "tree"])
    assert result.exit_code == 0


def test_clean():
    result = runner.invoke(app, ["clean"])
    assert result.exit_code == 0


def test_clean_with_preview():
    result = runner.invoke(app, ["clean", "--preview"], input="y\n")
    assert result.exit_code == 0


def test_diff():
    result = runner.invoke(app, ["diff"])
    assert result.exit_code == 0
