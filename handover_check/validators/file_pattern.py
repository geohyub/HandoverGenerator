"""file_pattern validator — check files matching a glob pattern exist."""

import re
from pathlib import Path
from typing import List

from handover_check.models import ResultStatus, RuleResult
from handover_check.validators.base import BaseValidator


class FilePatternValidator(BaseValidator):

    def validate(self, folder_path: Path, context: dict) -> RuleResult:
        pattern = self.config.get("pattern", "*")
        naming_regex = self.config.get("naming_regex")

        if not folder_path.exists():
            return RuleResult(
                rule_type="file_pattern",
                status=ResultStatus.SKIP,
                message=f"Folder not found: {folder_path}",
                folder_path=str(folder_path),
            )

        matched_files = sorted(folder_path.glob(pattern))
        matched_files = [f for f in matched_files if f.is_file()]

        if not matched_files:
            return RuleResult(
                rule_type="file_pattern",
                status=ResultStatus.FAIL,
                message=f"No files matching '{pattern}' found",
                folder_path=str(folder_path),
            )

        # If naming_regex is specified, validate each file against it
        violations: List[str] = []
        if naming_regex:
            compiled = re.compile(naming_regex)
            for f in matched_files:
                if not compiled.match(f.name):
                    violations.append(f.name)
                    # Record naming violation in context
                    context.setdefault("naming_violations", []).append({
                        "folder": str(folder_path),
                        "filename": f.name,
                        "expected_pattern": naming_regex,
                        "issue": "Does not match naming convention",
                    })

            # Store matched files for count_match usage
            context.setdefault("naming_matches", {})
            folder_key = str(folder_path)
            context["naming_matches"].setdefault(folder_key, {})
            context["naming_matches"][folder_key][naming_regex] = matched_files

        if violations:
            return RuleResult(
                rule_type="file_pattern",
                status=ResultStatus.WARNING,
                message=f"{len(matched_files)} files found, {len(violations)} naming violations",
                details=[f"NAMING VIOLATION: {v}" for v in violations],
                folder_path=str(folder_path),
            )

        return RuleResult(
            rule_type="file_pattern",
            status=ResultStatus.PASS,
            message=f"{len(matched_files)} files matching '{pattern}'",
            folder_path=str(folder_path),
        )
