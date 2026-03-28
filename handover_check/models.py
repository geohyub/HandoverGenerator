"""Data models for validation results."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class ResultStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIP = "SKIP"
    INFO = "INFO"


@dataclass
class RuleResult:
    """Result of a single validation rule execution."""
    rule_type: str
    status: ResultStatus
    message: str
    details: List[str] = field(default_factory=list)
    folder_path: Optional[str] = None


@dataclass
class FolderResult:
    """Aggregated results for a single folder."""
    path: str
    description: str
    rule_results: List[RuleResult] = field(default_factory=list)
    optional: bool = False

    @property
    def status(self) -> ResultStatus:
        if not self.rule_results:
            return ResultStatus.SKIP
        statuses = [r.status for r in self.rule_results]
        if ResultStatus.FAIL in statuses:
            return ResultStatus.FAIL
        if ResultStatus.WARNING in statuses:
            return ResultStatus.WARNING
        if all(s == ResultStatus.SKIP for s in statuses):
            return ResultStatus.SKIP
        return ResultStatus.PASS


@dataclass
class FileInfo:
    """Information about a single file in the delivery folder."""
    path: Path
    relative_path: str
    folder: str
    filename: str
    size_bytes: int
    modified: str
    naming_ok: Optional[bool] = None
    notes: str = ""


@dataclass
class ValidationReport:
    """Complete validation report."""
    profile_name: str
    client: Optional[str]
    project: Optional[str]
    delivery_path: str
    timestamp: str
    language: str = "en"
    base_profile: Optional[str] = None
    profile_description: Optional[str] = None
    profile_notes: Optional[str] = None
    resolved_variables: Dict[str, str] = field(default_factory=dict)
    line_list_source: Optional[str] = None
    line_id_column: Optional[str] = None
    line_status_column: Optional[str] = None
    line_status_filter: Optional[str] = None
    folder_results: List[FolderResult] = field(default_factory=list)
    global_results: List[RuleResult] = field(default_factory=list)
    file_inventory: List[FileInfo] = field(default_factory=list)
    naming_violations: List[dict] = field(default_factory=list)
    line_coverage: Optional[dict] = None
    total_files: int = 0
    total_size_bytes: int = 0

    @property
    def overall_status(self) -> ResultStatus:
        all_statuses = [fr.status for fr in self.folder_results]
        all_statuses += [gr.status for gr in self.global_results]
        if ResultStatus.FAIL in all_statuses:
            return ResultStatus.FAIL
        if ResultStatus.WARNING in all_statuses:
            return ResultStatus.WARNING
        return ResultStatus.PASS

    @property
    def fail_count(self) -> int:
        count = sum(1 for fr in self.folder_results if fr.status == ResultStatus.FAIL)
        count += sum(1 for gr in self.global_results if gr.status == ResultStatus.FAIL)
        return count

    @property
    def warning_count(self) -> int:
        count = sum(1 for fr in self.folder_results if fr.status == ResultStatus.WARNING)
        count += sum(1 for gr in self.global_results if gr.status == ResultStatus.WARNING)
        return count
