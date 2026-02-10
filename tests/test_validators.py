"""Tests for individual validators."""

import pytest
from pathlib import Path

from handover_check.models import ResultStatus
from handover_check.validators.file_pattern import FilePatternValidator
from handover_check.validators.naming_regex import NamingRegexValidator
from handover_check.validators.required_files import RequiredFilesValidator
from handover_check.validators.file_size import MinFileSizeValidator
from handover_check.validators.empty_folders import EmptyFoldersValidator
from handover_check.validators.zero_byte import ZeroByteValidator
from handover_check.validators.temp_files import TempFilesValidator
from handover_check.validators.duplicates import DuplicateFilesValidator
from handover_check.validators.total_size import TotalSizeReportValidator
from handover_check.validators.checksum import ChecksumFileValidator


@pytest.fixture
def context():
    return {"variables": {}, "naming_matches": {}, "naming_violations": []}


class TestFilePatternValidator:
    def test_pass_when_files_exist(self, tmp_path, context):
        (tmp_path / "data.sgy").write_bytes(b"\x00" * 100)
        v = FilePatternValidator({"type": "file_pattern", "pattern": "*.sgy"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.PASS

    def test_fail_when_no_files(self, tmp_path, context):
        v = FilePatternValidator({"type": "file_pattern", "pattern": "*.sgy"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.FAIL

    def test_skip_when_folder_missing(self, tmp_path, context):
        v = FilePatternValidator({"type": "file_pattern", "pattern": "*.sgy"})
        result = v.validate(tmp_path / "nonexistent", context)
        assert result.status == ResultStatus.SKIP

    def test_naming_regex_violation(self, tmp_path, context):
        (tmp_path / "good_L0001.sgy").write_bytes(b"\x00" * 100)
        (tmp_path / "bad_file.sgy").write_bytes(b"\x00" * 100)
        v = FilePatternValidator({
            "type": "file_pattern",
            "pattern": "*.sgy",
            "naming_regex": r"^good_L\d{4}\.sgy$",
        })
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.WARNING
        assert len(context["naming_violations"]) == 1

    def test_naming_regex_stores_matches(self, tmp_path, context):
        (tmp_path / "PROJ_L0001.sgy").write_bytes(b"\x00" * 100)
        regex = r"^PROJ_(?P<line>L\d{4})\.sgy$"
        v = FilePatternValidator({
            "type": "file_pattern",
            "pattern": "*.sgy",
            "naming_regex": regex,
        })
        v.validate(tmp_path, context)
        assert str(tmp_path) in context["naming_matches"]


class TestNamingRegexValidator:
    def test_pass_all_match(self, tmp_path, context):
        (tmp_path / "file_001.txt").write_text("a")
        (tmp_path / "file_002.txt").write_text("b")
        v = NamingRegexValidator({"type": "naming_regex", "regex": r"^file_\d{3}\.txt$"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.PASS

    def test_warning_some_violate(self, tmp_path, context):
        (tmp_path / "file_001.txt").write_text("a")
        (tmp_path / "bad.txt").write_text("b")
        v = NamingRegexValidator({"type": "naming_regex", "regex": r"^file_\d{3}\.txt$"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.WARNING


class TestRequiredFilesValidator:
    def test_pass_all_found(self, tmp_path, context):
        (tmp_path / "readme.txt").write_text("hello")
        (tmp_path / "report.pdf").write_bytes(b"pdf")
        v = RequiredFilesValidator({
            "type": "required_files",
            "files": ["readme.txt", "report.pdf"],
        })
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.PASS

    def test_fail_missing(self, tmp_path, context):
        (tmp_path / "readme.txt").write_text("hello")
        v = RequiredFilesValidator({
            "type": "required_files",
            "files": ["readme.txt", "missing.pdf"],
        })
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.FAIL
        assert "MISSING: missing.pdf" in result.details[0]

    def test_wildcard_match(self, tmp_path, context):
        (tmp_path / "Report_Rev01.pdf").write_bytes(b"pdf")
        v = RequiredFilesValidator({
            "type": "required_files",
            "files": ["*Report*Rev*.pdf"],
        })
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.PASS


class TestMinFileSizeValidator:
    def test_pass_all_above(self, tmp_path, context):
        (tmp_path / "big.dat").write_bytes(b"\x00" * 2048)
        v = MinFileSizeValidator({"type": "min_file_size", "min_bytes": 1024})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.PASS

    def test_warning_some_small(self, tmp_path, context):
        (tmp_path / "small.dat").write_bytes(b"\x00" * 10)
        v = MinFileSizeValidator({"type": "min_file_size", "min_bytes": 1024})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.WARNING


class TestEmptyFoldersValidator:
    def test_pass_no_empty(self, tmp_path, context):
        (tmp_path / "file.txt").write_text("data")
        v = EmptyFoldersValidator({"type": "no_empty_folders"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.PASS

    def test_warning_empty_subfolder(self, tmp_path, context):
        (tmp_path / "file.txt").write_text("data")
        (tmp_path / "empty_dir").mkdir()
        v = EmptyFoldersValidator({"type": "no_empty_folders"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.WARNING


class TestZeroByteValidator:
    def test_pass_no_zero(self, tmp_path, context):
        (tmp_path / "file.txt").write_text("data")
        v = ZeroByteValidator({"type": "no_zero_byte_files"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.PASS

    def test_fail_zero_byte(self, tmp_path, context):
        (tmp_path / "empty.txt").write_bytes(b"")
        v = ZeroByteValidator({"type": "no_zero_byte_files"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.FAIL


class TestTempFilesValidator:
    def test_pass_no_temp(self, tmp_path, context):
        (tmp_path / "normal.txt").write_text("data")
        v = TempFilesValidator({"type": "no_temp_files"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.PASS

    def test_fail_temp_found(self, tmp_path, context):
        (tmp_path / "Thumbs.db").write_bytes(b"data")
        v = TempFilesValidator({"type": "no_temp_files"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.FAIL

    def test_fail_tilde_file(self, tmp_path, context):
        (tmp_path / "~$document.docx").write_bytes(b"data")
        v = TempFilesValidator({"type": "no_temp_files"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.FAIL

    def test_custom_patterns(self, tmp_path, context):
        (tmp_path / "cache.dat").write_bytes(b"data")
        v = TempFilesValidator({
            "type": "no_temp_files",
            "patterns": ["cache.*"],
        })
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.FAIL


class TestDuplicateFilesValidator:
    def test_pass_no_duplicates(self, tmp_path, context):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "b.txt").write_text("b")
        v = DuplicateFilesValidator({"type": "no_duplicate_files"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.PASS

    def test_warning_duplicates(self, tmp_path, context):
        sub1 = tmp_path / "sub1"
        sub2 = tmp_path / "sub2"
        sub1.mkdir()
        sub2.mkdir()
        (sub1 / "same.txt").write_text("data")
        (sub2 / "same.txt").write_text("other")
        v = DuplicateFilesValidator({"type": "no_duplicate_files"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.WARNING


class TestTotalSizeReportValidator:
    def test_always_info(self, tmp_path, context):
        (tmp_path / "file.dat").write_bytes(b"\x00" * 1024)
        v = TotalSizeReportValidator({"type": "total_size_report"})
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.INFO
        assert "1 files" in result.message


class TestChecksumFileValidator:
    def test_pass_valid_checksum(self, tmp_path, context):
        import hashlib
        content = b"test data"
        (tmp_path / "test.txt").write_bytes(content)
        md5 = hashlib.md5(content).hexdigest()
        (tmp_path / "checksum.md5").write_text(f"{md5}  test.txt\n")
        v = ChecksumFileValidator({
            "type": "checksum_file",
            "algorithm": "md5",
            "expected_file": "checksum.md5",
        })
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.PASS

    def test_fail_missing_checksum_file(self, tmp_path, context):
        v = ChecksumFileValidator({
            "type": "checksum_file",
            "algorithm": "md5",
            "expected_file": "checksum.md5",
        })
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.FAIL

    def test_fail_checksum_mismatch(self, tmp_path, context):
        (tmp_path / "test.txt").write_bytes(b"actual data")
        (tmp_path / "checksum.md5").write_text("0000000000000000  test.txt\n")
        v = ChecksumFileValidator({
            "type": "checksum_file",
            "algorithm": "md5",
            "expected_file": "checksum.md5",
        })
        result = v.validate(tmp_path, context)
        assert result.status == ResultStatus.FAIL
        assert any("mismatch" in d for d in result.details)
