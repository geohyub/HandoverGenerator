from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QMessageBox

from geoview_pyside6.app_base import GeoViewApp
from geoview_pyside6.constants import CATEGORY_THEMES, Category

from desktop.panels.workflow_panel import WorkflowPanel
from desktop.services.validation_service import (
    ProfileBundle,
    ValidationBundle,
    ValidationRequest,
    ValidationWorker,
    prepare_profile_bundle,
)
from handover_check.i18n import normalize_lang, tr


class HandoverDesktopApp(GeoViewApp):
    APP_NAME = "Handover Package Validator"
    APP_VERSION = "v1.1.0"
    CATEGORY = Category.MANAGEMENT
    USE_PROJECT_CONTEXT = False

    def setup_panels(self) -> None:
        self.panel = WorkflowPanel()
        self.add_panel("workflow", "🧭", "Workflow", self.panel)
        self.workflow_button = self.sidebar.buttons[-1]
        self.preview_action = self.top_bar.add_action_button(tr("preview_plan", self.lang_manager.lang), self.preview_plan)
        self.validate_action = self.top_bar.add_action_button(tr("validate", self.lang_manager.lang), self.run_validation, primary=True)
        self._panel_label = {"ko": "워크플로우", "en": "Workflow"}
        self.current_bundle: ValidationBundle | None = None
        self.current_profile_bundle: ProfileBundle | None = None
        self.current_request: ValidationRequest | None = None
        self.refresh_language(self.lang_manager.lang)

    def refresh_language(self, lang: str) -> None:
        lang = normalize_lang(lang)
        theme = CATEGORY_THEMES[self.CATEGORY]
        self.setWindowTitle(f"{tr('app_title', lang)} {self.APP_VERSION}")
        self.sidebar.set_brand(tr("app_title", lang), self.APP_VERSION, theme.accent)
        self.workflow_button.setText(self._panel_label[lang])
        self.preview_action.setText(tr("preview_plan", lang))
        self.validate_action.setText(tr("validate", lang))
        self.panel.refresh_text(lang)
        self.panel.panel_title = self._panel_label[lang]
        if self.current_profile_bundle:
            self.panel.sync_profile_variables(
                self.current_profile_bundle.plan.required_variables,
                self.current_profile_bundle.plan.resolved_variables,
            )
            self.panel.set_profile_plan(self.current_profile_bundle.plan, lang)
        if self.current_bundle:
            self._apply_bundle(self.current_bundle, lang)

    def on_language_changed(self, lang: str, force: bool = False) -> None:
        self.refresh_language(lang)

    def _collect_request(self) -> ValidationRequest:
        return self.panel.collect_request(self.lang_manager.lang)

    def preview_plan(self) -> None:
        request = self._collect_request()
        try:
            profile_bundle = prepare_profile_bundle(request)
        except Exception as exc:
            QMessageBox.warning(self, tr("profile_load_failed", self.lang_manager.lang), str(exc))
            return

        self.current_request = request
        self.current_profile_bundle = profile_bundle
        self.panel.sync_profile_variables(
            profile_bundle.plan.required_variables,
            profile_bundle.plan.resolved_variables,
        )
        self.panel.set_profile_plan(profile_bundle.plan, self.lang_manager.lang)
        self.panel.clear_console()
        self.panel.append_console(tr("profile_loaded", self.lang_manager.lang))
        self.panel.append_console(profile_bundle.plan.headline)
        self.sidebar.set_active_panel("workflow")

    def run_validation(self) -> None:
        request = self._collect_request()

        if not request.delivery_path:
            QMessageBox.warning(self, tr("missing_input", self.lang_manager.lang), tr("delivery_required", self.lang_manager.lang))
            return
        if not request.basic and not request.profile_path:
            QMessageBox.warning(self, tr("missing_input", self.lang_manager.lang), tr("profile_required", self.lang_manager.lang))
            return
        if not Path(request.delivery_path).is_dir():
            QMessageBox.warning(self, tr("invalid_path", self.lang_manager.lang), tr("delivery_path_not_found", self.lang_manager.lang, path=request.delivery_path))
            return
        if request.profile_path and not Path(request.profile_path).is_file():
            QMessageBox.warning(self, tr("invalid_file", self.lang_manager.lang), tr("profile_file_not_found", self.lang_manager.lang, path=request.profile_path))
            return

        self.current_request = request
        self.panel.clear_console()
        self.panel.append_console(tr("validating", self.lang_manager.lang))
        self.status_bar.showMessage(tr("validating", self.lang_manager.lang))

        self.worker = ValidationWorker(request)
        self.worker.status.connect(self.panel.append_console)
        self.worker.finished.connect(self._on_validation_done)
        self.worker.failed.connect(self._on_validation_failed)
        self.worker.start()

    def _apply_bundle(self, bundle: ValidationBundle, lang: str) -> None:
        self.panel.sync_profile_variables(bundle.profile_bundle.plan.required_variables, bundle.profile_bundle.plan.resolved_variables)
        self.panel.set_profile_plan(bundle.profile_bundle.plan, lang)
        self.panel.set_readiness(bundle.readiness, lang)
        self.panel.set_report(bundle, lang)
        self.panel.preview_text.setPlainText(bundle.preview_text)
        self.status_bar.showMessage(
            tr("status_with_counts", lang, label=bundle.readiness.readiness_label, failed=bundle.readiness.failed_checks, warning=bundle.readiness.warning_checks)
        )

    def _on_validation_done(self, bundle: ValidationBundle) -> None:
        self.current_bundle = bundle
        self.current_profile_bundle = bundle.profile_bundle
        self._apply_bundle(bundle, self.lang_manager.lang)
        self.sidebar.set_active_panel("workflow")
        if bundle.export_path:
            self.panel.append_console(bundle.export_path)

    def _on_validation_failed(self, message: str) -> None:
        self.panel.append_console(message)
        self.status_bar.showMessage(tr("validation_error", self.lang_manager.lang))
        QMessageBox.critical(self, tr("validation_error", self.lang_manager.lang), message)

    def on_project_context_changed(self, ctx, old_ctx=None) -> None:
        return
