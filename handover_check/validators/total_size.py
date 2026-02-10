"""total_size_report validator — report total file count and size per folder."""

from pathlib import Path

from handover_check.models import ResultStatus, RuleResult
from handover_check.validators.base import BaseValidator


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.1f} GB"


class TotalSizeReportValidator(BaseValidator):

    def validate(self, folder_path: Path, context: dict) -> RuleResult:
        if not folder_path.exists():
            return RuleResult(
                rule_type="total_size_report",
                status=ResultStatus.SKIP,
                message=f"Folder not found: {folder_path}",
                folder_path=str(folder_path),
            )

        total_size = 0
        file_count = 0
        for f in folder_path.rglob("*"):
            if f.is_file():
                total_size += f.stat().st_size
                file_count += 1

        return RuleResult(
            rule_type="total_size_report",
            status=ResultStatus.INFO,
            message=f"{file_count} files, {format_size(total_size)}",
            folder_path=str(folder_path),
        )
