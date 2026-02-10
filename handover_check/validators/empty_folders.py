"""no_empty_folders validator — detect folders with no files."""

from pathlib import Path

from handover_check.models import ResultStatus, RuleResult
from handover_check.validators.base import BaseValidator


class EmptyFoldersValidator(BaseValidator):

    def validate(self, folder_path: Path, context: dict) -> RuleResult:
        if not folder_path.exists():
            return RuleResult(
                rule_type="no_empty_folders",
                status=ResultStatus.SKIP,
                message=f"Folder not found: {folder_path}",
                folder_path=str(folder_path),
            )

        empty_dirs = []
        for d in folder_path.rglob("*"):
            if d.is_dir():
                # A directory is empty if it has no files (even recursively)
                has_files = any(f.is_file() for f in d.rglob("*"))
                if not has_files:
                    try:
                        rel = d.relative_to(folder_path)
                    except ValueError:
                        rel = d
                    empty_dirs.append(str(rel))

        # Also check the folder itself
        has_files = any(f.is_file() for f in folder_path.rglob("*"))
        if not has_files:
            empty_dirs.insert(0, ".")

        if empty_dirs:
            return RuleResult(
                rule_type="no_empty_folders",
                status=ResultStatus.WARNING,
                message=f"{len(empty_dirs)} empty folder(s) found",
                details=empty_dirs,
                folder_path=str(folder_path),
            )

        return RuleResult(
            rule_type="no_empty_folders",
            status=ResultStatus.PASS,
            message="No empty folders",
            folder_path=str(folder_path),
        )
