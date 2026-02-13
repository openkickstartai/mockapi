"""Tests for mockapi.cli module."""

import json
import os
import tempfile

from click.testing import CliRunner

from mockapi.cli import main, _file_size_human, _profile_data


def _write_db(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)


class TestFileSizeHuman:
    def test_bytes(self, tmp_path):
        p = tmp_path / "tiny.json"
        p.write_text('{"a": 1}')
        result = _file_size_human(str(p))
        assert "B" in result

    def test_kilobytes(self, tmp_path):
        p = tmp_path / "medium.json"
        p.write_text("x" * 2048)
        result = _file_size_human(str(p))
        assert "KB" in result


class TestCLIValidation:
    def test_invalid_json_reports_error(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{not json}")
        runner = CliRunner()
        result = runner.invoke(main, ["serve", str(bad)])
        assert result.exit_code != 0
        assert "Invalid JSON" in result.output or "Error" in result.output

    def test_non_object_json_reports_error(self, tmp_path):
        arr = tmp_path / "arr.json"
        arr.write_text("[1, 2, 3]")
        runner = CliRunner()
        result = runner.invoke(main, ["serve", str(arr)])
        assert result.exit_code != 0

    def test_missing_file_reports_error(self):
        runner = CliRunner()
        result = runner.invoke(main, ["serve", "/tmp/does_not_exist_xyz.json"])
        assert result.exit_code != 0
