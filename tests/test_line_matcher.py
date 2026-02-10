"""Tests for line_matcher module."""

import pytest
from pathlib import Path

from handover_check.line_matcher import LineMatcher, LineMatchError


class TestLineMatcher:
    def test_load_csv(self, tmp_linelist):
        lm = LineMatcher(
            csv_path=tmp_linelist,
            line_id_column="LineName",
            status_column="Status",
            status_filter="Completed",
        )
        assert lm.line_ids == {"L0001", "L0002", "L0003"}

    def test_load_csv_no_filter(self, tmp_path):
        csv = tmp_path / "lines.csv"
        csv.write_text(
            "LineName,Status\n"
            "L0001,Completed\n"
            "L0002,Planned\n"
            "L0003,Completed\n"
        )
        lm = LineMatcher(csv_path=csv, line_id_column="LineName")
        assert lm.line_ids == {"L0001", "L0002", "L0003"}

    def test_load_csv_with_filter(self, tmp_path):
        csv = tmp_path / "lines.csv"
        csv.write_text(
            "LineName,Status\n"
            "L0001,Completed\n"
            "L0002,Planned\n"
            "L0003,Completed\n"
        )
        lm = LineMatcher(
            csv_path=csv,
            line_id_column="LineName",
            status_column="Status",
            status_filter="Completed",
        )
        assert lm.line_ids == {"L0001", "L0003"}

    def test_missing_csv_raises(self, tmp_path):
        with pytest.raises(LineMatchError, match="not found"):
            LineMatcher(csv_path=tmp_path / "missing.csv", line_id_column="X")

    def test_missing_column_raises(self, tmp_path):
        csv = tmp_path / "lines.csv"
        csv.write_text("A,B\n1,2\n")
        with pytest.raises(LineMatchError, match="Column 'LineName' not found"):
            LineMatcher(csv_path=csv, line_id_column="LineName")

    def test_compare_all_matched(self, tmp_linelist):
        lm = LineMatcher(
            csv_path=tmp_linelist,
            line_id_column="LineName",
            status_column="Status",
            status_filter="Completed",
        )
        result = lm.compare({"L0001", "L0002", "L0003"})
        assert result["missing"] == []
        assert result["extra"] == []
        assert result["expected_count"] == 3
        assert result["found_count"] == 3

    def test_compare_missing_lines(self, tmp_linelist):
        lm = LineMatcher(
            csv_path=tmp_linelist,
            line_id_column="LineName",
            status_column="Status",
            status_filter="Completed",
        )
        result = lm.compare({"L0001", "L0003"})
        assert result["missing"] == ["L0002"]
        assert result["found_count"] == 2

    def test_compare_extra_lines(self, tmp_linelist):
        lm = LineMatcher(
            csv_path=tmp_linelist,
            line_id_column="LineName",
            status_column="Status",
            status_filter="Completed",
        )
        result = lm.compare({"L0001", "L0002", "L0003", "L0099"})
        assert result["extra"] == ["L0099"]


class TestExtractLinesFromFiles:
    def test_extract_lines(self, tmp_path):
        files = [
            tmp_path / "PROJ_L0001_SBP.sgy",
            tmp_path / "PROJ_L0002_SBP.sgy",
        ]
        for f in files:
            f.write_bytes(b"\x00")
        regex = r"^PROJ_(?P<line>L\d{4})_SBP\.sgy$"
        result = LineMatcher.extract_lines_from_files(files, regex)
        assert result == {"L0001", "L0002"}

    def test_extract_no_match(self, tmp_path):
        files = [tmp_path / "bad_name.sgy"]
        files[0].write_bytes(b"\x00")
        regex = r"^PROJ_(?P<line>L\d{4})_SBP\.sgy$"
        result = LineMatcher.extract_lines_from_files(files, regex)
        assert result == set()
