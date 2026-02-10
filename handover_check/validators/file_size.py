"""min_file_size validator — flag files below minimum byte size."""

from pathlib import Path

from handover_check.models import ResultStatus, RuleResult
from handover_check.validators.base import BaseValidator


class MinFileSizeValidator(BaseValidator):

    def validate(self, folder_path: Path, context: dict) -> RuleResult:
        min_bytes = self.config.get("min_bytes", 0)

        if not folder_path.exists():
            return RuleResult(
                rule_type="min_file_size",
                status=ResultStatus.SKIP,
                message=f"Folder not found: {folder_path}",
                folder_path=str(folder_path),
            )

        all_files = [f for f in folder_path.rglob("*") if f.is_file()]
        small_files = []
        for f in all_files:
            size = f.stat().st_size
            if size < min_bytes:
                rel = f.relative_to(folder_path)
                small_files.append(f"{rel} ({size} bytes)")

        if small_files:
            return RuleResult(
                rule_type="min_file_size",
                status=ResultStatus.WARNING,
                message=f"{len(small_files)} file(s) below {min_bytes} bytes",
                details=small_files,
                folder_path=str(folder_path),
            )

        return RuleResult(
            rule_type="min_file_size",
            status=ResultStatus.PASS,
            message=f"All files >= {min_bytes} bytes",
            folder_path=str(folder_path),
        )
