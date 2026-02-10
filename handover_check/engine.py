"""Main validation orchestrator."""

import datetime
from pathlib import Path
from typing import Dict, List, Optional

from handover_check.config import (
    ConfigError,
    load_and_merge_profile,
    load_yaml,
    resolve_variables,
    substitute_in_rules,
)
from handover_check.line_matcher import LineMatcher, LineMatchError
from handover_check.models import (
    FileInfo,
    FolderResult,
    ResultStatus,
    RuleResult,
    ValidationReport,
)
from handover_check.validators import get_validator
from handover_check.validators.total_size import format_size


class ValidationEngine:
    """Orchestrates the validation process."""

    def __init__(
        self,
        delivery_path: Path,
        profile_path: Optional[Path] = None,
        linelist_path: Optional[Path] = None,
        cli_vars: Optional[Dict[str, str]] = None,
        basic: bool = False,
        folder_filter: Optional[str] = None,
    ):
        self.delivery_path = delivery_path.resolve()
        self.profile_path = profile_path
        self.linelist_path = linelist_path
        self.cli_vars = cli_vars or {}
        self.basic = basic
        self.folder_filter = folder_filter

        if not self.delivery_path.exists():
            raise ConfigError(f"Delivery path not found: {self.delivery_path}")
        if not self.delivery_path.is_dir():
            raise ConfigError(f"Delivery path is not a directory: {self.delivery_path}")

    def _load_profile(self) -> dict:
        """Load and merge profile."""
        if self.basic or self.profile_path is None:
            # Use base_geoview.yaml only
            base_path = Path(__file__).parent.parent / "profiles" / "base_geoview.yaml"
            if not base_path.exists():
                raise ConfigError(f"Base profile not found: {base_path}")
            return load_yaml(base_path)
        return load_and_merge_profile(self.profile_path)

    def _load_line_list(self, profile: dict, variables: dict) -> Optional[LineMatcher]:
        """Load line list from CLI override or profile config."""
        ll_config = profile.get("line_list")

        if self.linelist_path:
            csv_path = self.linelist_path
        elif ll_config and ll_config.get("source"):
            source = ll_config["source"]
            csv_path = self.delivery_path / source
            if not csv_path.exists():
                csv_path = Path(source)
        else:
            return None

        if not csv_path.exists():
            return None

        try:
            return LineMatcher(
                csv_path=csv_path,
                line_id_column=ll_config.get("line_id_column", "LineName") if ll_config else "LineName",
                status_column=ll_config.get("status_column") if ll_config else None,
                status_filter=ll_config.get("status_filter") if ll_config else None,
            )
        except LineMatchError:
            return None

    def _build_file_inventory(self) -> List[FileInfo]:
        """Build complete file inventory of the delivery folder."""
        inventory = []
        for f in sorted(self.delivery_path.rglob("*")):
            if f.is_file():
                try:
                    rel = f.relative_to(self.delivery_path)
                    stat = f.stat()
                    parts = rel.parts
                    folder = str(Path(*parts[:-1])) if len(parts) > 1 else "."
                    inventory.append(FileInfo(
                        path=f,
                        relative_path=str(rel),
                        folder=folder,
                        filename=f.name,
                        size_bytes=stat.st_size,
                        modified=datetime.datetime.fromtimestamp(
                            stat.st_mtime
                        ).strftime("%Y-%m-%d %H:%M"),
                    ))
                except (OSError, ValueError):
                    continue
        return inventory

    def _compute_totals(self, inventory: List[FileInfo]):
        """Compute total files and size from inventory."""
        total_files = len(inventory)
        total_size = sum(fi.size_bytes for fi in inventory)
        return total_files, total_size

    def run(self) -> ValidationReport:
        """Execute full validation and return report."""
        profile = self._load_profile()
        variables = resolve_variables(profile, self.cli_vars)
        line_matcher = self._load_line_list(profile, variables)

        # Shared context for validators
        context = {
            "variables": variables,
            "line_list": line_matcher,
            "delivery_root": self.delivery_path,
            "naming_matches": {},
            "naming_violations": [],
        }

        report = ValidationReport(
            profile_name=profile.get("profile_name", "unknown"),
            client=profile.get("client"),
            project=profile.get("project"),
            delivery_path=str(self.delivery_path),
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # --- Folder Validations ---
        folders = profile.get("folders", [])
        for folder_def in folders:
            folder_rel_path = folder_def.get("path", "")

            # Apply folder filter if specified
            if self.folder_filter and folder_rel_path != self.folder_filter:
                continue

            folder_abs_path = self.delivery_path / folder_rel_path
            is_optional = folder_def.get("optional", False)

            folder_result = FolderResult(
                path=folder_rel_path,
                description=folder_def.get("description", ""),
                optional=is_optional,
            )

            if not folder_abs_path.exists():
                if is_optional:
                    folder_result.rule_results.append(RuleResult(
                        rule_type="folder_check",
                        status=ResultStatus.SKIP,
                        message=f"Optional folder not present",
                        folder_path=folder_rel_path,
                    ))
                else:
                    folder_result.rule_results.append(RuleResult(
                        rule_type="folder_check",
                        status=ResultStatus.FAIL,
                        message=f"Required folder not found: {folder_rel_path}",
                        folder_path=folder_rel_path,
                    ))
                report.folder_results.append(folder_result)
                continue

            # Run rules for this folder
            rules = folder_def.get("rules", [])
            try:
                rules = substitute_in_rules(rules, variables)
            except ConfigError as e:
                folder_result.rule_results.append(RuleResult(
                    rule_type="variable_error",
                    status=ResultStatus.FAIL,
                    message=str(e),
                    folder_path=folder_rel_path,
                ))
                report.folder_results.append(folder_result)
                continue

            for rule_config in rules:
                try:
                    validator = get_validator(rule_config)
                    result = validator.validate(folder_abs_path, context)
                    result.folder_path = folder_rel_path
                    folder_result.rule_results.append(result)
                except Exception as e:
                    folder_result.rule_results.append(RuleResult(
                        rule_type=rule_config.get("type", "unknown"),
                        status=ResultStatus.FAIL,
                        message=f"Validator error: {e}",
                        folder_path=folder_rel_path,
                    ))

            report.folder_results.append(folder_result)

        # --- Global Validations ---
        global_rules = profile.get("global_rules", [])
        try:
            global_rules = substitute_in_rules(global_rules, variables)
        except ConfigError as e:
            report.global_results.append(RuleResult(
                rule_type="variable_error",
                status=ResultStatus.FAIL,
                message=str(e),
            ))

        for rule_config in global_rules:
            try:
                validator = get_validator(rule_config)
                result = validator.validate(self.delivery_path, context)
                result.folder_path = "(global)"
                report.global_results.append(result)
            except Exception as e:
                report.global_results.append(RuleResult(
                    rule_type=rule_config.get("type", "unknown"),
                    status=ResultStatus.FAIL,
                    message=f"Validator error: {e}",
                    folder_path="(global)",
                ))

        # --- File Inventory ---
        report.file_inventory = self._build_file_inventory()
        report.total_files, report.total_size_bytes = self._compute_totals(
            report.file_inventory
        )

        # --- Naming Violations ---
        report.naming_violations = context.get("naming_violations", [])

        # --- Line Coverage Matrix ---
        if line_matcher:
            report.line_coverage = self._build_line_coverage(
                profile, context, line_matcher
            )

        return report

    def _build_line_coverage(
        self, profile: dict, context: dict, line_matcher: LineMatcher
    ) -> dict:
        """Build line coverage matrix for the report.

        Returns dict with:
            "lines": sorted list of all line IDs
            "folders": list of folder paths that have count_match rules
            "matrix": {line_id: {folder_path: bool}}
        """
        naming_matches = context.get("naming_matches", {})
        folders_with_count = []

        # Find folders that have count_match rules
        for folder_def in profile.get("folders", []):
            rules = folder_def.get("rules", [])
            has_count = any(r.get("type") == "count_match" for r in rules)
            if has_count:
                folders_with_count.append(folder_def["path"])

        if not folders_with_count:
            return None

        all_lines = sorted(line_matcher.line_ids)
        matrix = {line: {} for line in all_lines}

        for folder_path in folders_with_count:
            abs_path = str(self.delivery_path / folder_path)
            if abs_path in naming_matches and naming_matches[abs_path]:
                regex, files = next(iter(naming_matches[abs_path].items()))
                found_lines = LineMatcher.extract_lines_from_files(files, regex)
                for line in all_lines:
                    matrix[line][folder_path] = line in found_lines
            else:
                for line in all_lines:
                    matrix[line][folder_path] = False

        return {
            "lines": all_lines,
            "folders": folders_with_count,
            "matrix": matrix,
        }
