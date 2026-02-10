"""Integration tests for the validation engine."""

import pytest
from pathlib import Path

from handover_check.engine import ValidationEngine
from handover_check.models import ResultStatus


class TestValidationEngine:
    def test_full_validation(self, tmp_delivery, tmp_linelist, test_profile_yaml):
        """End-to-end test: validate delivery against profile with line list."""
        # Copy line list to delivery root
        import shutil
        shutil.copy(tmp_linelist, tmp_delivery / "line_list.csv")

        engine = ValidationEngine(
            delivery_path=tmp_delivery,
            profile_path=test_profile_yaml,
            cli_vars={"project_code": "TEST2025", "area_code": "RS"},
        )
        report = engine.run()

        assert report.profile_name == "Test_Profile"
        assert report.client == "TestClient"
        assert report.total_files > 0

        # SBP Raw should PASS (3/3 files)
        sbp_raw = next(
            fr for fr in report.folder_results if fr.path == "01_Raw_Data/01_SBP"
        )
        assert sbp_raw.status == ResultStatus.PASS

        # MBES Raw should FAIL (2/3, missing L0002)
        mbes_raw = next(
            fr for fr in report.folder_results if fr.path == "01_Raw_Data/02_MBES"
        )
        assert mbes_raw.status == ResultStatus.FAIL

        # Reports should have FAIL from temp files
        reports = next(
            fr for fr in report.folder_results if fr.path == "04_Reports"
        )
        temp_result = next(
            rr for rr in reports.rule_results if rr.rule_type == "no_temp_files"
        )
        assert temp_result.status == ResultStatus.FAIL

        # Overall should be FAIL
        assert report.overall_status == ResultStatus.FAIL

    def test_folder_filter(self, tmp_delivery, test_profile_yaml):
        """Test --folder filter: only validate specified folder."""
        engine = ValidationEngine(
            delivery_path=tmp_delivery,
            profile_path=test_profile_yaml,
            cli_vars={"project_code": "TEST2025", "area_code": "RS"},
            folder_filter="03_Navigation",
        )
        report = engine.run()

        # Only one folder result
        assert len(report.folder_results) == 1
        assert report.folder_results[0].path == "03_Navigation"

    def test_missing_delivery_path(self, tmp_path, test_profile_yaml):
        """Test error when delivery path doesn't exist."""
        from handover_check.config import ConfigError
        with pytest.raises(ConfigError, match="not found"):
            ValidationEngine(
                delivery_path=tmp_path / "nonexistent",
                profile_path=test_profile_yaml,
            )

    def test_optional_folder_skip(self, tmp_delivery, test_profile_yaml):
        """Test that optional folders produce SKIP when missing."""
        # Remove the optional folder
        import shutil
        misc = tmp_delivery / "05_Miscellaneous"
        if misc.exists():
            shutil.rmtree(misc)

        engine = ValidationEngine(
            delivery_path=tmp_delivery,
            profile_path=test_profile_yaml,
            cli_vars={"project_code": "TEST2025", "area_code": "RS"},
        )
        report = engine.run()

        misc_result = next(
            fr for fr in report.folder_results if fr.path == "05_Miscellaneous"
        )
        assert misc_result.status == ResultStatus.SKIP

    def test_line_coverage_matrix(self, tmp_delivery, tmp_linelist, test_profile_yaml):
        """Test that line coverage matrix is generated."""
        import shutil
        shutil.copy(tmp_linelist, tmp_delivery / "line_list.csv")

        engine = ValidationEngine(
            delivery_path=tmp_delivery,
            profile_path=test_profile_yaml,
            cli_vars={"project_code": "TEST2025", "area_code": "RS"},
        )
        report = engine.run()

        assert report.line_coverage is not None
        assert "L0001" in report.line_coverage["lines"]
        assert "L0002" in report.line_coverage["lines"]

    def test_file_inventory(self, tmp_delivery, test_profile_yaml):
        """Test that file inventory is populated."""
        engine = ValidationEngine(
            delivery_path=tmp_delivery,
            profile_path=test_profile_yaml,
            cli_vars={"project_code": "TEST2025", "area_code": "RS"},
        )
        report = engine.run()
        assert len(report.file_inventory) > 0
        assert all(fi.filename for fi in report.file_inventory)
