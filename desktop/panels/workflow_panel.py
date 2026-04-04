from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextCursor
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QHeaderView,
    QCheckBox,
    QComboBox,
)

from geoview_pyside6.constants import Dark, Font

from handover_check.i18n import normalize_lang, severity_text, status_text, tr
from handover_check.insights import (
    build_section_compare_text,
    format_issue_detail_text,
    format_profile_plan_text,
    format_readiness_text,
)

from desktop.services.validation_service import (
    ProfileBundle,
    ValidationBundle,
    ValidationRequest,
    prepare_profile_bundle,
)
from desktop.widgets.variable_row import VariableRow

if TYPE_CHECKING:
    from handover_check.insights import ProfilePlanInsight, ReadinessInsight


def _status_color(status: str) -> str:
    return {
        "PASS": "#a6e3a1",
        "FAIL": "#f38ba8",
        "WARNING": "#fab387",
        "INFO": "#89b4fa",
        "SKIP": "#a6adc8",
    }.get(status, "#cdd6f4")


def _set_view_text(view: QTextEdit | QPlainTextEdit, text: str) -> None:
    view.setPlainText(text)
    cursor = view.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.Start)
    view.setTextCursor(cursor)


class WorkflowPanel(QWidget):
    panel_title = "Workflow"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._lang = "ko"
        self._profile_bundle: ProfileBundle | None = None
        self._bundle: ValidationBundle | None = None
        self._issues: list = []

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        self.title_label = QLabel()
        self.title_label.setStyleSheet(f"font-size: {Font.LG}px; font-weight: 700;")
        self.subtitle_label = QLabel()
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet(f"color: {Dark.DIM};")
        root.addWidget(self.title_label)
        root.addWidget(self.subtitle_label)

        self.tabs = QTabWidget()
        root.addWidget(self.tabs, 1)

        self._build_setup_tab()
        self._build_plan_tab()
        self._build_readiness_tab()
        self._build_issues_tab()
        self._build_compare_tab()
        self._build_preview_tab()
        self._build_console_tab()
        self.refresh_text("ko")

    def _build_setup_tab(self) -> None:
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        left = QVBoxLayout()
        left.setSpacing(10)
        layout.addLayout(left, 3)

        self.paths_group = QGroupBox()
        grid = QGridLayout(self.paths_group)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        self.delivery_edit = QLineEdit()
        self.profile_edit = QLineEdit()
        self.linelist_edit = QLineEdit()
        self.output_edit = QLineEdit()
        self.delivery_btn = QPushButton()
        self.profile_btn = QPushButton()
        self.linelist_btn = QPushButton()
        self.output_btn = QPushButton()
        self.delivery_btn.clicked.connect(self.browse_delivery)
        self.profile_btn.clicked.connect(self.browse_profile)
        self.linelist_btn.clicked.connect(self.browse_linelist)
        self.output_btn.clicked.connect(self.browse_output)
        for row, (prefix, edit, btn) in enumerate([
            ("delivery", self.delivery_edit, self.delivery_btn),
            ("profile", self.profile_edit, self.profile_btn),
            ("line_list", self.linelist_edit, self.linelist_btn),
            ("output_excel", self.output_edit, self.output_btn),
        ]):
            label = QLabel()
            label.setFixedWidth(120)
            setattr(self, f"{prefix}_label", label)
            grid.addWidget(label, row, 0)
            grid.addWidget(edit, row, 1)
            grid.addWidget(btn, row, 2)
        left.addWidget(self.paths_group)

        self.variables_group = QGroupBox()
        vars_layout = QVBoxLayout(self.variables_group)
        vars_layout.setSpacing(6)
        self.var_box = QVBoxLayout()
        self.var_box.setSpacing(6)
        vars_layout.addLayout(self.var_box)
        self.add_var_btn = QPushButton()
        self.add_var_btn.clicked.connect(lambda: self.add_variable_row())
        vars_layout.addWidget(self.add_var_btn, 0, Qt.AlignmentFlag.AlignLeft)
        left.addWidget(self.variables_group)

        self.options_group = QGroupBox()
        options = QFormLayout(self.options_group)
        self.basic_check = QCheckBox()
        self.filter_label = QLabel()
        self.folder_filter_edit = QLineEdit()
        options.addRow(self.basic_check)
        options.addRow(self.filter_label, self.folder_filter_edit)
        left.addWidget(self.options_group)
        left.addStretch(1)

        help_group = QGroupBox()
        help_layout = QVBoxLayout(help_group)
        self.guide_title = QLabel()
        self.guide_title.setStyleSheet(f"font-size: {Font.LG}px; font-weight: 700;")
        self.guide_view = QPlainTextEdit()
        self.guide_view.setReadOnly(True)
        self.guide_view.setFrameShape(QFrame.Shape.NoFrame)
        help_layout.addWidget(self.guide_title)
        help_layout.addWidget(self.guide_view, 1)
        layout.addWidget(help_group, 2)

        self._variable_rows: list[VariableRow] = []
        self.add_variable_row("project_code", "")
        self.add_variable_row("area_code", "")
        self.tabs.addTab(tab, "")
        self.setup_tab = tab

    def _build_plan_tab(self) -> None:
        self.plan_text = QTextEdit()
        self.plan_text.setReadOnly(True)
        self.plan_text.setFrameShape(QFrame.Shape.NoFrame)
        self.tabs.addTab(self.plan_text, "")

    def _build_readiness_tab(self) -> None:
        self.readiness_text = QTextEdit()
        self.readiness_text.setReadOnly(True)
        self.readiness_text.setFrameShape(QFrame.Shape.NoFrame)
        self.tabs.addTab(self.readiness_text, "")

    def _build_issues_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        splitter = QSplitter(Qt.Orientation.Vertical)
        self.issue_table = QTableWidget()
        self.issue_table.setColumnCount(8)
        self.issue_table.verticalHeader().setVisible(False)
        self.issue_table.setAlternatingRowColors(True)
        self.issue_table.horizontalHeader().setStretchLastSection(True)
        self.issue_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.issue_table.itemSelectionChanged.connect(self._sync_issue_detail)
        self.issue_detail = QTextEdit()
        self.issue_detail.setReadOnly(True)
        self.issue_detail.setFrameShape(QFrame.Shape.NoFrame)
        splitter.addWidget(self.issue_table)
        splitter.addWidget(self.issue_detail)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter, 1)
        self.tabs.addTab(tab, "")

    def _build_compare_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        controls = QHBoxLayout()
        controls.setSpacing(8)
        self.left_label = QLabel()
        self.left_combo = QComboBox()
        self.right_label = QLabel()
        self.right_combo = QComboBox()
        self.left_combo.currentTextChanged.connect(self._refresh_compare)
        self.right_combo.currentTextChanged.connect(self._refresh_compare)
        controls.addWidget(self.left_label)
        controls.addWidget(self.left_combo, 1)
        controls.addWidget(self.right_label)
        controls.addWidget(self.right_combo, 1)
        self.compare_text = QTextEdit()
        self.compare_text.setReadOnly(True)
        self.compare_text.setFrameShape(QFrame.Shape.NoFrame)
        layout.addLayout(controls)
        layout.addWidget(self.compare_text, 1)
        self.tabs.addTab(tab, "")

    def _build_preview_tab(self) -> None:
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFrameShape(QFrame.Shape.NoFrame)
        self.tabs.addTab(self.preview_text, "")

    def _build_console_tab(self) -> None:
        self.console_text = QPlainTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setFrameShape(QFrame.Shape.NoFrame)
        self.tabs.addTab(self.console_text, "")

    def refresh_text(self, lang: str) -> None:
        self._lang = normalize_lang(lang)
        self.panel_title = tr("app_title", self._lang)
        self.title_label.setText(tr("app_title", self._lang))
        self.subtitle_label.setText(tr("app_subtitle", self._lang))

        self.tabs.setTabText(0, tr("group_paths", self._lang))
        self.tabs.setTabText(1, tr("tab_validation_plan", self._lang))
        self.tabs.setTabText(2, tr("tab_summary", self._lang))
        self.tabs.setTabText(3, tr("tab_issue_register", self._lang))
        self.tabs.setTabText(4, tr("tab_section_compare", self._lang))
        self.tabs.setTabText(5, tr("tab_report_preview", self._lang))
        self.tabs.setTabText(6, tr("tab_console", self._lang))

        self.paths_group.setTitle(tr("group_paths", self._lang))
        self.variables_group.setTitle(tr("group_variables", self._lang))
        self.options_group.setTitle(tr("group_options", self._lang))
        self.delivery_label.setText(tr("delivery_path", self._lang))
        self.profile_label.setText(tr("profile", self._lang))
        self.line_list_label.setText(tr("line_list", self._lang))
        self.output_excel_label.setText(tr("output_excel", self._lang))
        self.delivery_btn.setText(tr("browse", self._lang))
        self.profile_btn.setText(tr("browse", self._lang))
        self.linelist_btn.setText(tr("browse", self._lang))
        self.output_btn.setText(tr("browse", self._lang))
        self.add_var_btn.setText(tr("add_variable", self._lang))
        self.basic_check.setText(tr("basic_mode", self._lang))
        self.filter_label.setText(tr("folder_filter", self._lang))
        self.delivery_edit.setPlaceholderText(tr("placeholder_delivery", self._lang))
        self.profile_edit.setPlaceholderText(tr("placeholder_profile", self._lang))
        self.linelist_edit.setPlaceholderText(tr("placeholder_linelist", self._lang))
        self.output_edit.setPlaceholderText(tr("placeholder_output", self._lang))
        self.folder_filter_edit.setPlaceholderText(tr("placeholder_filter", self._lang))
        self.guide_title.setText(tr("welcome_text", self._lang).splitlines()[0])
        self.guide_view.setPlainText(tr("welcome_text", self._lang))
        self.left_label.setText(tr("compare_left", self._lang))
        self.right_label.setText(tr("compare_right", self._lang))
        self._refresh_issue_headers()
        self._refresh_compare()
        if not self.plan_text.toPlainText().strip():
            self.plan_text.setPlainText(tr("plan_placeholder", self._lang))
        if not self.readiness_text.toPlainText().strip():
            self.readiness_text.setPlainText(tr("summary_placeholder", self._lang))
        if not self.preview_text.toPlainText().strip():
            self.preview_text.setPlainText(tr("report_preview_placeholder", self._lang))
        if not self.console_text.toPlainText().strip():
            self.console_text.setPlainText(tr("console_header", self._lang))

    def _refresh_issue_headers(self) -> None:
        self.issue_table.setHorizontalHeaderLabels(
            [
                "#",
                tr("col_section", self._lang),
                tr("col_severity", self._lang),
                tr("col_status", self._lang),
                tr("col_check", self._lang),
                tr("col_category", self._lang),
                tr("col_finding", self._lang),
                tr("recommendation", self._lang),
            ]
        )

    def browse_delivery(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, tr("select_delivery_folder", self._lang))
        if folder:
            self.delivery_edit.setText(folder)

    def browse_profile(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, tr("select_profile", self._lang), "", tr("yaml_filter", self._lang))
        if path:
            self.profile_edit.setText(path)

    def browse_linelist(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, tr("select_line_list", self._lang), "", tr("csv_filter", self._lang))
        if path:
            self.linelist_edit.setText(path)

    def browse_output(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, tr("save_excel_report", self._lang), "", tr("excel_filter", self._lang))
        if path:
            if not path.lower().endswith(".xlsx"):
                path += ".xlsx"
            self.output_edit.setText(path)

    def add_variable_row(self, key: str = "", value: str = "") -> VariableRow:
        row = VariableRow(key, value)
        row.removed.connect(self._remove_variable_row)
        self._variable_rows.append(row)
        self.var_box.addWidget(row)
        return row

    def _remove_variable_row(self, row: VariableRow) -> None:
        if row in self._variable_rows:
            self._variable_rows.remove(row)
        row.setParent(None)
        row.deleteLater()

    def clear_variable_rows(self) -> None:
        for row in list(self._variable_rows):
            self._remove_variable_row(row)

    def sync_profile_variables(self, required: list[str], resolved: dict[str, str]) -> None:
        existing = self.collect_variables()
        keys: list[str] = []
        for key in list(required) + list(existing.keys()):
            if key and key not in keys:
                keys.append(key)
        self.clear_variable_rows()
        for key in keys:
            self.add_variable_row(key, resolved.get(key) or existing.get(key, ""))

    def collect_variables(self) -> dict[str, str]:
        variables: dict[str, str] = {}
        for row in self._variable_rows:
            key = row.key_edit.text().strip()
            if not key:
                continue
            variables[key] = row.value_edit.text().strip()
        return variables

    def collect_request(self, language: str) -> ValidationRequest:
        return ValidationRequest(
            delivery_path=self.delivery_edit.text().strip(),
            profile_path=self.profile_edit.text().strip(),
            linelist_path=self.linelist_edit.text().strip(),
            output_path=self.output_edit.text().strip(),
            folder_filter=self.folder_filter_edit.text().strip(),
            basic=self.basic_check.isChecked(),
            variables=self.collect_variables(),
            language=normalize_lang(language),
        )

    def set_profile_plan(self, plan: ProfilePlanInsight, lang: str) -> None:
        self.plan_text.setPlainText(format_profile_plan_text(plan, lang))

    def set_readiness(self, readiness: ReadinessInsight, lang: str) -> None:
        self.readiness_text.setPlainText(format_readiness_text(readiness, lang))

    def set_report(self, bundle: ValidationBundle, lang: str) -> None:
        self._bundle = bundle
        self._issues = list(bundle.readiness.issues)
        self.issue_table.setRowCount(max(1, len(self._issues)))
        if not self._issues:
            self.issue_table.setItem(0, 0, QTableWidgetItem(tr("no_issues_found", lang)))
            self.issue_detail.setPlainText(tr("no_issue_detail", lang))
        else:
            for row, issue in enumerate(self._issues):
                values = [
                    str(row + 1),
                    issue.scope,
                    severity_text(issue.severity, lang),
                    status_text(issue.status.value, lang),
                    issue.check_label,
                    issue.category,
                    issue.message,
                    issue.action_hint,
                ]
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    if column in (2, 3):
                        item.setForeground(QColor(_status_color(issue.status.value)))
                    self.issue_table.setItem(row, column, item)
            self.issue_table.selectRow(0)
            self._sync_issue_detail()

        scopes = [folder.path for folder in bundle.report.folder_results]
        left_current = self.left_combo.currentText()
        right_current = self.right_combo.currentText()
        self.left_combo.blockSignals(True)
        self.right_combo.blockSignals(True)
        self.left_combo.clear()
        self.right_combo.clear()
        self.left_combo.addItems(scopes or [""])
        self.right_combo.addItems(scopes or [""])
        if left_current in scopes:
            self.left_combo.setCurrentText(left_current)
        if right_current in scopes:
            self.right_combo.setCurrentText(right_current)
        elif len(scopes) > 1:
            self.right_combo.setCurrentIndex(1)
        self.left_combo.blockSignals(False)
        self.right_combo.blockSignals(False)
        self._refresh_compare()
        self.preview_text.setPlainText(bundle.preview_text)

    def _sync_issue_detail(self) -> None:
        row = self.issue_table.currentRow()
        if row < 0 or row >= len(self._issues):
            self.issue_detail.setPlainText("")
            return
        self.issue_detail.setPlainText(format_issue_detail_text(self._issues[row], self._lang))

    def _refresh_compare(self) -> None:
        if self._bundle is None:
            self.compare_text.setPlainText(tr("no_compare", self._lang))
            return
        self.compare_text.setPlainText(
            build_section_compare_text(
                self._bundle.report,
                self.left_combo.currentText().strip() or None,
                self.right_combo.currentText().strip() or None,
                self._lang,
            )
        )

    def append_console(self, text: str) -> None:
        current = self.console_text.toPlainText().rstrip()
        if current:
            current += "\n"
        current += text.rstrip()
        self.console_text.setPlainText(current)
        cursor = self.console_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.console_text.setTextCursor(cursor)

    def clear_console(self) -> None:
        self.console_text.clear()

