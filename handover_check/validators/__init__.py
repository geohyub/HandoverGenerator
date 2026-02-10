"""Validator registry and loader."""

from handover_check.validators.base import BaseValidator
from handover_check.validators.file_pattern import FilePatternValidator
from handover_check.validators.naming_regex import NamingRegexValidator
from handover_check.validators.count_match import CountMatchValidator
from handover_check.validators.required_files import RequiredFilesValidator
from handover_check.validators.file_size import MinFileSizeValidator
from handover_check.validators.empty_folders import EmptyFoldersValidator
from handover_check.validators.zero_byte import ZeroByteValidator
from handover_check.validators.temp_files import TempFilesValidator
from handover_check.validators.duplicates import DuplicateFilesValidator
from handover_check.validators.segy_check import SegyHeaderCheckValidator
from handover_check.validators.total_size import TotalSizeReportValidator
from handover_check.validators.checksum import ChecksumFileValidator

VALIDATOR_REGISTRY = {
    "file_pattern": FilePatternValidator,
    "naming_regex": NamingRegexValidator,
    "count_match": CountMatchValidator,
    "required_files": RequiredFilesValidator,
    "min_file_size": MinFileSizeValidator,
    "no_empty_folders": EmptyFoldersValidator,
    "no_zero_byte_files": ZeroByteValidator,
    "no_temp_files": TempFilesValidator,
    "no_duplicate_files": DuplicateFilesValidator,
    "segy_header_check": SegyHeaderCheckValidator,
    "total_size_report": TotalSizeReportValidator,
    "checksum_file": ChecksumFileValidator,
}


def get_validator(rule_config: dict) -> BaseValidator:
    """Get a validator instance for the given rule config."""
    rule_type = rule_config.get("type")
    if rule_type not in VALIDATOR_REGISTRY:
        raise ValueError(f"Unknown rule type: {rule_type}")
    return VALIDATOR_REGISTRY[rule_type](rule_config)
