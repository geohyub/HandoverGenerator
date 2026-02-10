"""no_temp_files validator — detect temp/system files."""

from fnmatch import fnmatch
from pathlib import Path
from typing import List

from handover_check.models import ResultStatus, RuleResult
from handover_check.validators.base import BaseValidator

DEFAULT_TEMP_PATTERNS = [
    "~$*",
    "Thumbs.db",
    ".DS_Store",
    "*.tmp",
    "*.bak",
    "desktop.ini",
]


class TempFilesValidator(BaseValidator):

    def validate(self, folder_path: Path, context: dict) -> RuleResult:
        patterns: List[str] = self.config.get("patterns", DEFAULT_TEMP_PATTERNS)

        if not folder_path.exists():
            return RuleResult(
                rule_type="no_temp_files",
                status=ResultStatus.SKIP,
                message=f"Folder not found: {folder_path}",
                folder_path=str(folder_path),
            )

        temp_files = []
        for f in folder_path.rglob("*"):
            if f.is_file():
                for pat in patterns:
                    if fnmatch(f.name, pat):
                        try:
                            rel = f.relative_to(folder_path)
                        except ValueError:
                            rel = f
                        temp_files.append(str(rel))
                        break

        if temp_files:
            return RuleResult(
                rule_type="no_temp_files",
                status=ResultStatus.FAIL,
                message=f"{len(temp_files)} temp/system file(s) found",
                details=temp_files,
                folder_path=str(folder_path),
            )

        return RuleResult(
            rule_type="no_temp_files",
            status=ResultStatus.PASS,
            message="No temp files",
            folder_path=str(folder_path),
        )
