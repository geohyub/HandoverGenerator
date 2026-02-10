"""no_zero_byte_files validator — detect 0-byte files."""

from pathlib import Path

from handover_check.models import ResultStatus, RuleResult
from handover_check.validators.base import BaseValidator


class ZeroByteValidator(BaseValidator):

    def validate(self, folder_path: Path, context: dict) -> RuleResult:
        if not folder_path.exists():
            return RuleResult(
                rule_type="no_zero_byte_files",
                status=ResultStatus.SKIP,
                message=f"Folder not found: {folder_path}",
                folder_path=str(folder_path),
            )

        zero_files = []
        for f in folder_path.rglob("*"):
            if f.is_file() and f.stat().st_size == 0:
                try:
                    rel = f.relative_to(folder_path)
                except ValueError:
                    rel = f
                zero_files.append(str(rel))

        if zero_files:
            return RuleResult(
                rule_type="no_zero_byte_files",
                status=ResultStatus.FAIL,
                message=f"{len(zero_files)} zero-byte file(s) found",
                details=zero_files,
                folder_path=str(folder_path),
            )

        return RuleResult(
            rule_type="no_zero_byte_files",
            status=ResultStatus.PASS,
            message="No zero-byte files",
            folder_path=str(folder_path),
        )
