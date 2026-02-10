"""segy_header_check validator — quick SEG-Y header validation."""

from pathlib import Path

from handover_check.models import ResultStatus, RuleResult
from handover_check.validators.base import BaseValidator


class SegyHeaderCheckValidator(BaseValidator):

    def validate(self, folder_path: Path, context: dict) -> RuleResult:
        try:
            import segyio
        except ImportError:
            return RuleResult(
                rule_type="segy_header_check",
                status=ResultStatus.SKIP,
                message="segyio not installed; skipping SEG-Y header check",
                folder_path=str(folder_path),
            )

        if not folder_path.exists():
            return RuleResult(
                rule_type="segy_header_check",
                status=ResultStatus.SKIP,
                message=f"Folder not found: {folder_path}",
                folder_path=str(folder_path),
            )

        check_coordinates = self.config.get("check_coordinates", False)
        check_sample_rate = self.config.get("check_sample_rate", False)
        expected_sample_rate = self.config.get("expected_sample_rate")

        segy_files = list(folder_path.glob("*.sgy")) + list(folder_path.glob("*.segy"))
        if not segy_files:
            return RuleResult(
                rule_type="segy_header_check",
                status=ResultStatus.SKIP,
                message="No SEG-Y files found in folder",
                folder_path=str(folder_path),
            )

        issues = []
        for sgy_file in segy_files:
            try:
                with segyio.open(sgy_file, ignore_geometry=True) as f:
                    # Check sample rate
                    if check_sample_rate:
                        dt = segyio.tools.dt(f) / 1000.0  # microseconds to milliseconds
                        actual_rate = 1000000.0 / segyio.tools.dt(f)  # Hz
                        if expected_sample_rate and abs(actual_rate - expected_sample_rate) > 1:
                            issues.append(
                                f"{sgy_file.name}: sample rate {actual_rate:.0f} Hz "
                                f"(expected {expected_sample_rate} Hz)"
                            )

                    # Check coordinates
                    if check_coordinates:
                        # Check first trace for coordinates
                        header = f.header[0]
                        sx = header.get(segyio.TraceField.SourceX, 0)
                        sy = header.get(segyio.TraceField.SourceY, 0)
                        if sx == 0 and sy == 0:
                            issues.append(
                                f"{sgy_file.name}: coordinates are zero (SourceX/SourceY)"
                            )
            except Exception as e:
                issues.append(f"{sgy_file.name}: failed to open ({e})")

        if issues:
            return RuleResult(
                rule_type="segy_header_check",
                status=ResultStatus.FAIL,
                message=f"{len(issues)} SEG-Y issue(s) found",
                details=issues,
                folder_path=str(folder_path),
            )

        return RuleResult(
            rule_type="segy_header_check",
            status=ResultStatus.PASS,
            message=f"{len(segy_files)} SEG-Y file(s) checked OK",
            folder_path=str(folder_path),
        )
