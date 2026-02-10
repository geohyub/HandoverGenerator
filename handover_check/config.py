"""YAML profile loader, variable substitution, and profile merging."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ConfigError(Exception):
    """Raised when profile configuration is invalid."""
    pass


def load_yaml(path: Path) -> dict:
    """Load a YAML file and return its contents as a dict."""
    if not path.exists():
        raise ConfigError(f"Profile not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if data is None:
        return {}
    return data


def resolve_base_path(profile_path: Path, base_name: str) -> Path:
    """Resolve the base profile path relative to the profile's directory."""
    # Check in the same directory first
    candidate = profile_path.parent / base_name
    if candidate.exists():
        return candidate
    # Check in profiles/ directory (parent of generated/)
    candidate = profile_path.parent.parent / base_name
    if candidate.exists():
        return candidate
    # Check in the package's profiles directory
    pkg_profiles = Path(__file__).parent.parent / "profiles" / base_name
    if pkg_profiles.exists():
        return pkg_profiles
    raise ConfigError(f"Base profile not found: {base_name}")


def merge_profiles(base: dict, project: dict) -> dict:
    """Merge base and project profiles according to merge rules.

    - folders: project completely overrides base if defined
    - global_rules: base rules kept, project's global_rules_extra appended
    - variables: merged, project takes precedence
    - Other metadata: project overrides base
    """
    merged = {}

    # folders: project overrides base entirely if defined
    if "folders" in project:
        merged["folders"] = project["folders"]
    else:
        merged["folders"] = base.get("folders", [])

    # global_rules: base + project extras
    merged["global_rules"] = list(base.get("global_rules", []))
    if "global_rules_extra" in project:
        merged["global_rules"].extend(project["global_rules_extra"])

    # variables: merge with project taking precedence
    merged["variables"] = {
        **base.get("variables", {}),
        **project.get("variables", {}),
    }

    # Metadata: project overrides
    for key in ["profile_name", "client", "project", "description",
                "line_list", "generated_from", "generated_date", "notes"]:
        merged[key] = project.get(key, base.get(key))

    return merged


def load_and_merge_profile(profile_path: Path) -> dict:
    """Load a project profile and merge with its base profile."""
    project = load_yaml(profile_path)

    base_name = project.get("base")
    if base_name:
        base_path = resolve_base_path(profile_path, base_name)
        base = load_yaml(base_path)
    else:
        base = {}

    return merge_profiles(base, project)


def substitute_variables(text: str, variables: Dict[str, Any]) -> str:
    """Replace {variable_name} placeholders in text with variable values.

    Raises ConfigError if a variable is referenced but has a null/None value.
    """
    def replacer(match):
        var_name = match.group(1)
        value = variables.get(var_name)
        if value is None:
            raise ConfigError(
                f"Variable '{var_name}' is referenced but not provided. "
                f"Use --var {var_name}=VALUE to supply it."
            )
        return str(value)

    # Match {variable_name} but NOT {4} (pure digits used in regex quantifiers like \d{4})
    return re.sub(r"\{([a-zA-Z_]\w*)\}", replacer, text)


def substitute_in_rules(rules: List[dict], variables: Dict[str, Any]) -> List[dict]:
    """Apply variable substitution to all string fields in rule configs."""
    substituted = []
    for rule in rules:
        new_rule = {}
        for key, value in rule.items():
            if isinstance(value, str):
                new_rule[key] = substitute_variables(value, variables)
            elif isinstance(value, list):
                new_rule[key] = [
                    substitute_variables(v, variables) if isinstance(v, str) else v
                    for v in value
                ]
            else:
                new_rule[key] = value
        substituted.append(new_rule)
    return substituted


def resolve_variables(profile: dict, cli_vars: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Resolve variables from profile + CLI overrides.

    Priority: CLI --var > project profile > base profile (already merged).
    """
    variables = dict(profile.get("variables", {}))
    if cli_vars:
        variables.update(cli_vars)
    return variables


def validate_profile(profile: dict) -> List[str]:
    """Validate a merged profile for common issues. Returns list of warnings."""
    warnings = []
    if not profile.get("folders") and not profile.get("global_rules"):
        warnings.append("Profile has no folders and no global_rules defined.")
    for i, folder in enumerate(profile.get("folders", [])):
        if "path" not in folder:
            warnings.append(f"Folder entry {i} is missing 'path' field.")
        if "rules" not in folder or not folder["rules"]:
            warnings.append(f"Folder '{folder.get('path', i)}' has no rules defined.")
    return warnings
