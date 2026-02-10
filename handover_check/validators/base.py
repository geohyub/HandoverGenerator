"""Base validator abstract class."""

from abc import ABC, abstractmethod
from pathlib import Path

from handover_check.models import RuleResult


class BaseValidator(ABC):
    """Abstract base class for all validators."""

    def __init__(self, rule_config: dict):
        self.config = rule_config

    @abstractmethod
    def validate(self, folder_path: Path, context: dict) -> RuleResult:
        """Execute validation.

        Args:
            folder_path: Absolute path to the folder being validated.
            context: Shared context dict containing:
                - "variables": resolved variable dict
                - "line_list": LineMatcher instance (or None)
                - "delivery_root": root path of delivery folder
                - "naming_matches": dict of {folder_path: {regex: [matched_files]}}
        Returns:
            RuleResult with status and details.
        """
        pass
