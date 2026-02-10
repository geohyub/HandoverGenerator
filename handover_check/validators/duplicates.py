"""no_duplicate_files validator — detect duplicate filenames across folders."""

from collections import defaultdict
from pathlib import Path

from handover_check.models import ResultStatus, RuleResult
from handover_check.validators.base import BaseValidator


class DuplicateFilesValidator(BaseValidator):

    def validate(self, folder_path: Path, context: dict) -> RuleResult:
        if not folder_path.exists():
            return RuleResult(
                rule_type="no_duplicate_files",
                status=ResultStatus.SKIP,
                message=f"Folder not found: {folder_path}",
                folder_path=str(folder_path),
            )

        # Group files by filename
        name_map = defaultdict(list)
        for f in folder_path.rglob("*"):
            if f.is_file():
                try:
                    rel = str(f.relative_to(folder_path))
                except ValueError:
                    rel = str(f)
                name_map[f.name].append(rel)

        duplicates = {
            name: paths for name, paths in name_map.items() if len(paths) > 1
        }

        if duplicates:
            details = []
            for name, paths in sorted(duplicates.items()):
                details.append(f"'{name}' found in: {', '.join(paths)}")
            return RuleResult(
                rule_type="no_duplicate_files",
                status=ResultStatus.WARNING,
                message=f"{len(duplicates)} duplicate filename(s) found",
                details=details,
                folder_path=str(folder_path),
            )

        return RuleResult(
            rule_type="no_duplicate_files",
            status=ResultStatus.PASS,
            message="No duplicate filenames",
            folder_path=str(folder_path),
        )
