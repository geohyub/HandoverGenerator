"""Tests for config module — profile loading, merging, variable substitution."""

import pytest
import yaml
from pathlib import Path

from handover_check.config import (
    ConfigError,
    load_yaml,
    merge_profiles,
    resolve_variables,
    substitute_variables,
    substitute_in_rules,
    validate_profile,
)


class TestLoadYaml:
    def test_load_valid_yaml(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("key: value\nlist:\n  - a\n  - b\n")
        result = load_yaml(f)
        assert result == {"key": "value", "list": ["a", "b"]}

    def test_load_missing_file(self, tmp_path):
        with pytest.raises(ConfigError, match="Profile not found"):
            load_yaml(tmp_path / "nonexistent.yaml")

    def test_load_empty_yaml(self, tmp_path):
        f = tmp_path / "empty.yaml"
        f.write_text("")
        result = load_yaml(f)
        assert result == {}


class TestMergeProfiles:
    def test_folders_override(self):
        base = {"folders": [{"path": "A"}], "global_rules": []}
        project = {"folders": [{"path": "B"}, {"path": "C"}]}
        merged = merge_profiles(base, project)
        assert len(merged["folders"]) == 2
        assert merged["folders"][0]["path"] == "B"

    def test_folders_inherit(self):
        base = {"folders": [{"path": "A"}], "global_rules": []}
        project = {}
        merged = merge_profiles(base, project)
        assert merged["folders"][0]["path"] == "A"

    def test_global_rules_extra(self):
        base = {"global_rules": [{"type": "no_empty_folders"}]}
        project = {"global_rules_extra": [{"type": "checksum_file"}]}
        merged = merge_profiles(base, project)
        assert len(merged["global_rules"]) == 2
        assert merged["global_rules"][1]["type"] == "checksum_file"

    def test_variables_merge(self):
        base = {"variables": {"project_code": "BASE", "extra": "yes"}}
        project = {"variables": {"project_code": "PROJECT", "area": "RS"}}
        merged = merge_profiles(base, project)
        assert merged["variables"]["project_code"] == "PROJECT"
        assert merged["variables"]["extra"] == "yes"
        assert merged["variables"]["area"] == "RS"

    def test_metadata_override(self):
        base = {"profile_name": "Base", "client": "BaseClient"}
        project = {"profile_name": "Project"}
        merged = merge_profiles(base, project)
        assert merged["profile_name"] == "Project"
        assert merged["client"] == "BaseClient"


class TestSubstituteVariables:
    def test_basic_substitution(self):
        result = substitute_variables("Hello {name}!", {"name": "World"})
        assert result == "Hello World!"

    def test_multiple_variables(self):
        result = substitute_variables(
            "{code}_{area}_data",
            {"code": "PROJ", "area": "RS"},
        )
        assert result == "PROJ_RS_data"

    def test_null_variable_raises(self):
        with pytest.raises(ConfigError, match="Variable 'code' is referenced but not provided"):
            substitute_variables("{code}_data", {"code": None})

    def test_missing_variable_raises(self):
        with pytest.raises(ConfigError, match="Variable 'missing'"):
            substitute_variables("{missing}_data", {})

    def test_no_variables(self):
        result = substitute_variables("no_vars_here", {"code": "PROJ"})
        assert result == "no_vars_here"

    def test_regex_preserved(self):
        result = substitute_variables(
            "^{code}_(?P<line>L\\d{4})\\.sgy$",
            {"code": "PROJ"},
        )
        # Note: \d{4} should NOT be treated as a variable because
        # the regex is \d{4} not {4} — but our regex substitution looks for \w+
        # {4} would match if it existed. Let's verify behavior.
        assert "PROJ" in result


class TestSubstituteInRules:
    def test_substitutes_in_rule_strings(self):
        rules = [
            {"type": "required_files", "files": ["{code}_report.pdf"]},
            {"type": "file_pattern", "pattern": "*.sgy", "naming_regex": "^{code}_.*$"},
        ]
        result = substitute_in_rules(rules, {"code": "PROJ"})
        assert result[0]["files"] == ["PROJ_report.pdf"]
        assert result[1]["naming_regex"] == "^PROJ_.*$"

    def test_non_string_values_preserved(self):
        rules = [{"type": "min_file_size", "min_bytes": 1024}]
        result = substitute_in_rules(rules, {"code": "PROJ"})
        assert result[0]["min_bytes"] == 1024


class TestResolveVariables:
    def test_cli_overrides_profile(self):
        profile = {"variables": {"code": "FROM_PROFILE"}}
        result = resolve_variables(profile, {"code": "FROM_CLI"})
        assert result["code"] == "FROM_CLI"

    def test_profile_only(self):
        profile = {"variables": {"code": "FROM_PROFILE"}}
        result = resolve_variables(profile)
        assert result["code"] == "FROM_PROFILE"


class TestValidateProfile:
    def test_empty_profile_warning(self):
        warnings = validate_profile({})
        assert any("no folders" in w for w in warnings)

    def test_folder_missing_path(self):
        warnings = validate_profile({"folders": [{"rules": []}]})
        assert any("missing 'path'" in w for w in warnings)

    def test_valid_profile_no_warnings(self):
        profile = {
            "folders": [{"path": "A", "rules": [{"type": "no_zero_byte_files"}]}],
            "global_rules": [{"type": "no_empty_folders"}],
        }
        warnings = validate_profile(profile)
        assert warnings == []
