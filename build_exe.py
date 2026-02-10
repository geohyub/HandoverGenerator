#!/usr/bin/env python
"""Build standalone exe using PyInstaller.

Usage:
    python build_exe.py          # build (default: --onefile)
    python build_exe.py --onedir # build as one-directory bundle
"""

import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build(one_dir=False):
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "HandoverValidator",
        "--windowed",  # no console window
        "--noconfirm",
        # Data files
        "--add-data",
        f"{ROOT / 'profiles'}:profiles",
        # Hidden imports (validators auto-registered)
        "--hidden-import",
        "handover_check.validators.file_pattern",
        "--hidden-import",
        "handover_check.validators.naming_regex",
        "--hidden-import",
        "handover_check.validators.count_match",
        "--hidden-import",
        "handover_check.validators.required_files",
        "--hidden-import",
        "handover_check.validators.file_size",
        "--hidden-import",
        "handover_check.validators.empty_folders",
        "--hidden-import",
        "handover_check.validators.zero_byte",
        "--hidden-import",
        "handover_check.validators.temp_files",
        "--hidden-import",
        "handover_check.validators.duplicates",
        "--hidden-import",
        "handover_check.validators.segy_check",
        "--hidden-import",
        "handover_check.validators.total_size",
        "--hidden-import",
        "handover_check.validators.checksum",
        "--hidden-import",
        "handover_check.reporters.console",
        "--hidden-import",
        "handover_check.reporters.excel",
        "--hidden-import",
        "yaml",
        "--hidden-import",
        "pandas",
        "--hidden-import",
        "openpyxl",
    ]

    if one_dir:
        cmd.append("--onedir")
    else:
        cmd.append("--onefile")

    # Entry point
    cmd.append(str(ROOT / "run_gui.py"))

    print("Building with command:")
    print(" ".join(cmd))
    print()

    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("Build successful!")
        if one_dir:
            print(f"Output: {ROOT / 'dist' / 'HandoverValidator' / 'HandoverValidator'}")
        else:
            exe_name = "HandoverValidator.exe" if sys.platform == "win32" else "HandoverValidator"
            print(f"Output: {ROOT / 'dist' / exe_name}")
        print("=" * 50)
    else:
        print("\nBuild FAILED", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    one_dir = "--onedir" in sys.argv
    build(one_dir=one_dir)
