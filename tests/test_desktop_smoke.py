import os
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from desktop.main import HandoverDesktopApp, ValidationRequest, run_validation_sync


@pytest.fixture(scope="session")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_desktop_shell_smoke(qapp, tmp_delivery, tmp_linelist, test_profile_yaml, tmp_path):
    output_path = tmp_path / "handover.xlsx"
    request = ValidationRequest(
        delivery_path=str(tmp_delivery),
        profile_path=str(test_profile_yaml),
        linelist_path=str(tmp_linelist),
        output_path=str(output_path),
        variables={"project_code": "TEST2025", "area_code": "RS"},
        language="en",
    )

    bundle = run_validation_sync(request)
    assert bundle.report.profile_name == "Test_Profile"
    assert bundle.readiness.issues
    assert output_path.exists()

    window = HandoverDesktopApp()
    window.current_bundle = bundle
    window.current_profile_bundle = bundle.profile_bundle
    window.refresh_language("en")
    qapp.processEvents()

    assert "Readiness" in window.panel.readiness_text.toPlainText()
    assert window.panel.issue_table.rowCount() >= len(bundle.readiness.issues)
    assert "Handover readiness report preview" in window.panel.preview_text.toPlainText()
