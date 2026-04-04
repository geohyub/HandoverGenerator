#!/usr/bin/env python
"""PySide6 desktop shell for Handover Package Validator."""

from __future__ import annotations

import sys
from pathlib import Path


THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[1]
SOFTWARE_ROOT = THIS_FILE.parents[3]
for candidate in (PROJECT_ROOT, SOFTWARE_ROOT / "_shared"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from PySide6.QtWidgets import QApplication

from desktop.app import HandoverDesktopApp
from desktop.services.validation_service import (
    ProfileBundle,
    ValidationBundle,
    ValidationRequest,
    ValidationWorker,
    prepare_profile_bundle,
    run_validation_sync,
)

__all__ = [
    "HandoverDesktopApp",
    "ProfileBundle",
    "ValidationBundle",
    "ValidationRequest",
    "ValidationWorker",
    "prepare_profile_bundle",
    "run_validation_sync",
]


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Handover Package Validator")
    window = HandoverDesktopApp()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
