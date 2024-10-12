"""Unittest for rejx."""
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

import rejx.utils
import rejx.cli
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


@pytest.fixture
def non_rej_file(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("This is a test file")
    return str(file)


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
    rej_files = rejx.utils.find_rej_files()
    assert len(rej_files) > 0
    assert all(file.endswith(".rej") for file in rej_files)


def test_parse_rej_file(sample_rej_file: str):
    rej_lines = rejx.utils.parse_rej_file(sample_rej_file)
    assert rej_lines is not None
    assert isinstance(rej_lines, list)


def test_apply_changes(sample_rej_file: str, sample_target_file: str):
    with open(sample_target_file, encoding="utf-8") as f:
        target_lines = f.readlines()
    rej_lines = rejx.utils.parse_rej_file(sample_rej_file)
    modified_lines = rejx.utils.apply_changes(target_lines, rej_lines)

    expected_lines = ["Line 1\n", "Line 2 - Modified\n", "Line 3\n"]

    assert modified_lines == expected_lines
    assert isinstance(modified_lines, list)


def test_process_rej_file(sample_rej_file: str):
    result = rejx.utils.process_rej_file(sample_rej_file)
    assert result


#####################################
#                                   #
#           REJX COMMANDS           #
#                                   #
#####################################

class TestFix:
    def test_fix(self, sample_rej_file: str):
        result = runner.invoke(app, ["fix", sample_rej_file])
        assert result.exit_code == 0

    def test_fix_all(self, tmp_path):
        rej_file = tmp_path / "test.rej"
        rej_file.write_text("Sample content")
        result = runner.invoke(app, ["fix", str(tmp_path), "--all"])
        assert result.exit_code == 0

    def test_fix_invalid_input(self):
        result = runner.invoke(app, ["fix", "non_existent_file.rej"])
        assert result.exit_code == 1

class TestLs:
    def test_ls(self, tmp_path):
        rej_file = tmp_path / "test.rej"
        rej_file.write_text("Sample content")
        result = runner.invoke(app, ["ls", str(tmp_path)])
        assert result.exit_code == 0
        assert "test.rej" in result.output

    def test_ls_all(self, tmp_path):
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        rej_file = subdir / "test.rej"
        rej_file.write_text("Sample content")
        result = runner.invoke(app, ["ls", str(tmp_path), "--all"])
        assert result.exit_code == 0
        assert "test.rej" in result.output

    def test_ls_tree(self, tmp_path):
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        rej_file = subdir / "test.rej"
        rej_file.write_text("Sample content")
        result = runner.invoke(app, ["ls", str(tmp_path), "--all", "--view", "tree"])
        assert result.exit_code == 0
        assert "test.rej" in result.output

class TestClean:
    def test_clean(self, tmp_path):
        rej_file = tmp_path / "test.rej"
        rej_file.write_text("Sample content")
        result = runner.invoke(app, ["clean", str(rej_file)])
        assert result.exit_code == 0
        assert not rej_file.exists()

    def test_clean_all(self, tmp_path):
        rej_file1 = tmp_path / "test1.rej"
        rej_file2 = tmp_path / "test2.rej"
        rej_file1.write_text("Sample content")
        rej_file2.write_text("Sample content")
        result = runner.invoke(app, ["clean", str(tmp_path), "--all"], input="y\n")
        assert result.exit_code == 0
        assert not rej_file1.exists()
        assert not rej_file2.exists()

    def test_clean_with_preview(self, tmp_path):
        rej_file = tmp_path / "test.rej"
        rej_file.write_text("Sample content")
        result = runner.invoke(app, ["clean", str(tmp_path), "--all", "--preview"], input="y\n")
        assert result.exit_code == 0
        assert "test.rej" in result.output
        assert not rej_file.exists()


class TestDiff:
    def test_diff(self):
        result = runner.invoke(app, ["diff"])
        assert result.exit_code == 0


class TestNonRejFile:
    def test_process_rej_file_with_non_rej_file(self, non_rej_file):
        result = rejx.utils.process_rej_file(non_rej_file)
        assert result is False

    @patch('rejx.utils.process_rej_file')
    def test_fix_with_non_rej_file(self, mock_process_rej_file, non_rej_file):
        runner = CliRunner()
        result = runner.invoke(app, ["fix", non_rej_file])
        assert result.exit_code == 0
        mock_process_rej_file.assert_not_called()

    @patch('rejx.utils.find_rej_files')
    @patch('rejx.utils.process_rej_file')
    def test_fix_all_with_mixed_files(self, mock_process_rej_file, mock_find_rej_files, non_rej_file):
        mock_find_rej_files.return_value = ["file1.rej", non_rej_file, "file2.rej"]
        runner = CliRunner()
        result = runner.invoke(app, ["fix", "--all"])
        assert result.exit_code == 0
        assert mock_process_rej_file.call_count == 2
        mock_process_rej_file.assert_any_call("file1.rej")
        mock_process_rej_file.assert_any_call("file2.rej")
