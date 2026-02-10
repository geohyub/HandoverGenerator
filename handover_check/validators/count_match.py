"""count_match validator — compare file count against line list."""

import re
from pathlib import Path

from handover_check.models import ResultStatus, RuleResult
from handover_check.validators.base import BaseValidator


class CountMatchValidator(BaseValidator):

    def validate(self, folder_path: Path, context: dict) -> RuleResult:
        line_matcher = context.get("line_list")

        if line_matcher is None:
            return RuleResult(
                rule_type="count_match",
                status=ResultStatus.SKIP,
                message="No line list provided, cannot perform count match",
                folder_path=str(folder_path),
            )

        if not folder_path.exists():
            return RuleResult(
                rule_type="count_match",
                status=ResultStatus.SKIP,
                message=f"Folder not found: {folder_path}",
                folder_path=str(folder_path),
            )

        # Find the naming_regex from this folder's rules (stored in context by file_pattern)
        naming_matches = context.get("naming_matches", {})
        folder_key = str(folder_path)

        if folder_key not in naming_matches or not naming_matches[folder_key]:
            # Fallback: try to extract lines from all files using any pattern
            return RuleResult(
                rule_type="count_match",
                status=ResultStatus.SKIP,
                message="No naming_regex found for this folder; cannot extract line IDs",
                folder_path=str(folder_path),
            )

        # Use the first (typically only) naming_regex for this folder
        regex, matched_files = next(iter(naming_matches[folder_key].items()))
        from handover_check.line_matcher import LineMatcher
        found_lines = LineMatcher.extract_lines_from_files(matched_files, regex)

        comparison = line_matcher.compare(found_lines)

        details = []
        if comparison["missing"]:
            details.extend([f"MISSING: {line}" for line in comparison["missing"]])
        if comparison["extra"]:
            details.extend([f"EXTRA: {line}" for line in comparison["extra"]])

        if comparison["missing"]:
            return RuleResult(
                rule_type="count_match",
                status=ResultStatus.FAIL,
                message=(
                    f"{comparison['found_count']}/{comparison['expected_count']} files "
                    f"({len(comparison['missing'])} missing)"
                ),
                details=details,
                folder_path=str(folder_path),
            )

        if comparison["extra"]:
            return RuleResult(
                rule_type="count_match",
                status=ResultStatus.WARNING,
                message=(
                    f"{comparison['found_count']}/{comparison['expected_count']} files "
                    f"({len(comparison['extra'])} extra)"
                ),
                details=details,
                folder_path=str(folder_path),
            )

        return RuleResult(
            rule_type="count_match",
            status=ResultStatus.PASS,
            message=f"{comparison['found_count']}/{comparison['expected_count']} files",
            folder_path=str(folder_path),
        )
