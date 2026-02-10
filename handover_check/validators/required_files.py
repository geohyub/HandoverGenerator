"""required_files validator — check specific files exist."""

from pathlib import Path
from typing import List

from handover_check.models import ResultStatus, RuleResult
from handover_check.validators.base import BaseValidator


class RequiredFilesValidator(BaseValidator):

    def validate(self, folder_path: Path, context: dict) -> RuleResult:
        required: List[str] = self.config.get("files", [])

        if not folder_path.exists():
            return RuleResult(
                rule_type="required_files",
                status=ResultStatus.SKIP,
                message=f"Folder not found: {folder_path}",
                folder_path=str(folder_path),
            )

        missing = []
        for pattern in required:
            matches = list(folder_path.glob(pattern))
            if not matches:
                missing.append(pattern)

        if missing:
            return RuleResult(
                rule_type="required_files",
                status=ResultStatus.FAIL,
                message=f"{len(missing)} required file(s) missing",
                details=[f"MISSING: {m}" for m in missing],
                folder_path=str(folder_path),
            )

        return RuleResult(
            rule_type="required_files",
            status=ResultStatus.PASS,
            message=f"All {len(required)} required files found",
            folder_path=str(folder_path),
        )
