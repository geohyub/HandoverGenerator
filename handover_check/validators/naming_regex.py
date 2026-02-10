"""naming_regex validator — validate all files match a regex pattern."""

import re
from pathlib import Path

from handover_check.models import ResultStatus, RuleResult
from handover_check.validators.base import BaseValidator


class NamingRegexValidator(BaseValidator):

    def validate(self, folder_path: Path, context: dict) -> RuleResult:
        regex = self.config.get("regex", "")

        if not folder_path.exists():
            return RuleResult(
                rule_type="naming_regex",
                status=ResultStatus.SKIP,
                message=f"Folder not found: {folder_path}",
                folder_path=str(folder_path),
            )

        compiled = re.compile(regex)
        all_files = [f for f in folder_path.iterdir() if f.is_file()]

        if not all_files:
            return RuleResult(
                rule_type="naming_regex",
                status=ResultStatus.SKIP,
                message="No files in folder to validate",
                folder_path=str(folder_path),
            )

        violations = []
        for f in all_files:
            if not compiled.match(f.name):
                violations.append(f.name)
                context.setdefault("naming_violations", []).append({
                    "folder": str(folder_path),
                    "filename": f.name,
                    "expected_pattern": regex,
                    "issue": "Does not match naming convention",
                })

        if violations:
            return RuleResult(
                rule_type="naming_regex",
                status=ResultStatus.WARNING,
                message=f"{len(violations)}/{len(all_files)} files violate naming convention",
                details=[f"VIOLATION: {v}" for v in violations],
                folder_path=str(folder_path),
            )

        return RuleResult(
            rule_type="naming_regex",
            status=ResultStatus.PASS,
            message=f"All {len(all_files)} files match naming convention",
            folder_path=str(folder_path),
        )
