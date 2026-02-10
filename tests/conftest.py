"""Shared test fixtures for handover-check tests."""

import os
import shutil
import textwrap
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def tmp_delivery(tmp_path):
    """Create a realistic test delivery folder structure."""
    root = tmp_path / "delivery"

    # 01_Raw_Data/01_SBP — 3 SEG-Y files
    sbp_raw = root / "01_Raw_Data" / "01_SBP"
    sbp_raw.mkdir(parents=True)
    for i in range(1, 4):
        f = sbp_raw / f"TEST2025_RS_L{i:04d}_SBP_RAW.sgy"
        f.write_bytes(b"\x00" * 2048)  # 2KB dummy

    # 01_Raw_Data/02_MBES — 2 of 3 (L0002 missing)
    mbes_raw = root / "01_Raw_Data" / "02_MBES"
    mbes_raw.mkdir(parents=True)
    for i in [1, 3]:
        f = mbes_raw / f"TEST2025_RS_L{i:04d}_MBES.all"
        f.write_bytes(b"\x00" * 1024)

    # 02_Processed_Data/01_SBP
    sbp_proc = root / "02_Processed_Data" / "01_SBP"
    sbp_proc.mkdir(parents=True)
    for i in range(1, 4):
        f = sbp_proc / f"TEST2025_RS_L{i:04d}_SBP_PROC.sgy"
        f.write_bytes(b"\x00" * 2048)

    # 03_Navigation
    nav = root / "03_Navigation"
    nav.mkdir(parents=True)
    (nav / "TEST2025_Final_Navigation.csv").write_text("lat,lon\n1,2\n")
    (nav / "TEST2025_Track_Chart.pdf").write_bytes(b"%PDF-dummy")

    # 04_Reports
    reports = root / "04_Reports"
    reports.mkdir(parents=True)
    (reports / "TEST2025_Processing_Report_Rev01.docx").write_bytes(b"docx-dummy")
    (reports / "TEST2025_Processing_Report_Rev01.pdf").write_bytes(b"pdf-dummy")

    # Add a temp file for testing
    (reports / "~$Processing_Report.docx").write_bytes(b"temp")

    # 05_Miscellaneous (optional, empty)
    misc = root / "05_Miscellaneous"
    misc.mkdir(parents=True)

    return root


@pytest.fixture
def tmp_linelist(tmp_path):
    """Create a test line list CSV."""
    csv_path = tmp_path / "line_list.csv"
    csv_path.write_text(
        "LineName,Status,StartKP,EndKP\n"
        "L0001,Completed,0.000,1.250\n"
        "L0002,Completed,1.250,2.500\n"
        "L0003,Completed,2.500,3.750\n"
    )
    return csv_path


@pytest.fixture
def test_profile_yaml(tmp_path):
    """Create a test project profile YAML."""
    profile = {
        "profile_name": "Test_Profile",
        "client": "TestClient",
        "project": "Test Project 2025",
        "variables": {
            "project_code": "TEST2025",
            "area_code": "RS",
        },
        "line_list": {
            "source": "line_list.csv",
            "line_id_column": "LineName",
            "status_column": "Status",
            "status_filter": "Completed",
        },
        "folders": [
            {
                "path": "01_Raw_Data/01_SBP",
                "description": "Raw SBP data",
                "rules": [
                    {
                        "type": "file_pattern",
                        "pattern": "*.sgy",
                        "naming_regex": "^{project_code}_{area_code}_(?P<line>L\\d{4})_SBP_RAW\\.sgy$",
                    },
                    {"type": "count_match", "match_to": "line_list"},
                    {"type": "min_file_size", "min_bytes": 1024},
                ],
            },
            {
                "path": "01_Raw_Data/02_MBES",
                "description": "Raw MBES data",
                "rules": [
                    {
                        "type": "file_pattern",
                        "pattern": "*.all",
                        "naming_regex": "^{project_code}_{area_code}_(?P<line>L\\d{4})_MBES\\.all$",
                    },
                    {"type": "count_match", "match_to": "line_list"},
                ],
            },
            {
                "path": "03_Navigation",
                "description": "Navigation data",
                "rules": [
                    {
                        "type": "required_files",
                        "files": [
                            "{project_code}_Final_Navigation.csv",
                            "{project_code}_Track_Chart.pdf",
                        ],
                    },
                ],
            },
            {
                "path": "04_Reports",
                "description": "Project reports",
                "rules": [
                    {
                        "type": "required_files",
                        "files": [
                            "{project_code}_Processing_Report_Rev*.docx",
                            "{project_code}_Processing_Report_Rev*.pdf",
                        ],
                    },
                    {"type": "no_temp_files"},
                ],
            },
            {
                "path": "05_Miscellaneous",
                "description": "Optional",
                "optional": True,
                "rules": [],
            },
        ],
        "global_rules": [
            {"type": "no_empty_folders"},
            {"type": "no_zero_byte_files"},
            {"type": "no_temp_files"},
            {"type": "total_size_report"},
        ],
    }

    profile_path = tmp_path / "test_profile.yaml"
    with open(profile_path, "w") as f:
        yaml.dump(profile, f, default_flow_style=False)
    return profile_path


@pytest.fixture
def base_profile_yaml(tmp_path):
    """Create a minimal base profile for merge testing."""
    base = {
        "profile_name": "Base_Standard",
        "folders": [
            {
                "path": "01_Raw_Data",
                "description": "Raw data",
                "rules": [{"type": "no_zero_byte_files"}],
            },
        ],
        "global_rules": [
            {"type": "no_empty_folders"},
            {"type": "no_temp_files"},
        ],
        "variables": {
            "project_code": None,
        },
    }
    path = tmp_path / "base_geoview.yaml"
    with open(path, "w") as f:
        yaml.dump(base, f, default_flow_style=False)
    return path
