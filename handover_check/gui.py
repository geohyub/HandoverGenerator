"""Handover Package Validator — Professional GUI (PyQt5)."""

import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QTextCharFormat, QPalette
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QGroupBox,
    QStatusBar,
    QProgressBar,
    QSplitter,
    QComboBox,
    QCheckBox,
    QMessageBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAction,
)

from handover_check.insights import (
    build_profile_plan,
    build_readiness_insight,
    build_report_preview_text,
    build_section_compare_text,
    format_issue_detail_text,
    format_profile_plan_text,
    format_readiness_text,
)
from handover_check.i18n import (
    language_label,
    normalize_lang,
    severity_text,
    status_text,
    tr,
)


# ---------------------------------------------------------------------------
# Colour / style constants
# ---------------------------------------------------------------------------
DARK_BG = "#1e1e2e"
DARK_SURFACE = "#2a2a3c"
DARK_BORDER = "#3a3a4c"
ACCENT = "#89b4fa"
ACCENT_HOVER = "#b4d0fb"
TEXT_PRIMARY = "#cdd6f4"
TEXT_SECONDARY = "#a6adc8"
SUCCESS = "#a6e3a1"
ERROR = "#f38ba8"
WARNING = "#fab387"
INFO = "#89b4fa"
SKIP = "#a6adc8"

STYLESHEET = f"""
QMainWindow {{
    background-color: {DARK_BG};
}}
QWidget {{
    background-color: {DARK_BG};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI", "Noto Sans KR", "Malgun Gothic", sans-serif;
    font-size: 13px;
}}
QGroupBox {{
    border: 1px solid {DARK_BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    font-weight: bold;
    font-size: 13px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: {ACCENT};
}}
QLineEdit {{
    background-color: {DARK_SURFACE};
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    padding: 7px 10px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT};
}}
QLineEdit:focus {{
    border: 1px solid {ACCENT};
}}
QLineEdit:read-only {{
    color: {TEXT_SECONDARY};
}}
QPushButton {{
    background-color: {DARK_SURFACE};
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    padding: 7px 16px;
    color: {TEXT_PRIMARY};
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {DARK_BORDER};
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: {ACCENT};
    color: {DARK_BG};
}}
QPushButton:disabled {{
    color: {TEXT_SECONDARY};
    background-color: {DARK_BG};
    border-color: {DARK_BORDER};
}}
QPushButton#runBtn {{
    background-color: {ACCENT};
    color: {DARK_BG};
    font-size: 14px;
    font-weight: bold;
    padding: 10px 32px;
    border: none;
    border-radius: 8px;
}}
QPushButton#runBtn:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton#runBtn:disabled {{
    background-color: {DARK_BORDER};
    color: {TEXT_SECONDARY};
}}
QPushButton#profileBtn {{
    background-color: transparent;
    border: 1px solid {ACCENT};
    color: {ACCENT};
    padding: 10px 24px;
    font-size: 13px;
    border-radius: 8px;
}}
QPushButton#profileBtn:hover {{
    background-color: {DARK_SURFACE};
}}
QTextEdit {{
    background-color: #181825;
    border: 1px solid {DARK_BORDER};
    border-radius: 8px;
    padding: 8px;
    font-family: "Cascadia Code", "JetBrains Mono", "Consolas", monospace;
    font-size: 12px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT};
}}
QCheckBox {{
    spacing: 6px;
    color: {TEXT_PRIMARY};
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid {DARK_BORDER};
    background-color: {DARK_SURFACE};
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}
QProgressBar {{
    border: none;
    border-radius: 4px;
    background-color: {DARK_SURFACE};
    text-align: center;
    color: {TEXT_PRIMARY};
    font-size: 11px;
    height: 8px;
}}
QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 4px;
}}
QStatusBar {{
    background-color: {DARK_SURFACE};
    color: {TEXT_SECONDARY};
    border-top: 1px solid {DARK_BORDER};
    font-size: 12px;
}}
QTabWidget::pane {{
    border: 1px solid {DARK_BORDER};
    border-radius: 8px;
    background-color: {DARK_BG};
}}
QTabBar::tab {{
    background-color: {DARK_SURFACE};
    color: {TEXT_SECONDARY};
    border: 1px solid {DARK_BORDER};
    border-bottom: none;
    padding: 8px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {DARK_BG};
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
}}
QTableWidget {{
    background-color: #181825;
    border: none;
    gridline-color: {DARK_BORDER};
    color: {TEXT_PRIMARY};
    font-size: 12px;
}}
QTableWidget::item {{
    padding: 4px 8px;
}}
QHeaderView::section {{
    background-color: {DARK_SURFACE};
    color: {ACCENT};
    border: 1px solid {DARK_BORDER};
    padding: 6px 8px;
    font-weight: bold;
    font-size: 12px;
}}
QScrollBar:vertical {{
    background-color: {DARK_BG};
    width: 10px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background-color: {DARK_BORDER};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {TEXT_SECONDARY};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QMenuBar {{
    background-color: {DARK_SURFACE};
    color: {TEXT_PRIMARY};
    border-bottom: 1px solid {DARK_BORDER};
}}
QMenuBar::item:selected {{
    background-color: {DARK_BORDER};
}}
QMenu {{
    background-color: {DARK_SURFACE};
    color: {TEXT_PRIMARY};
    border: 1px solid {DARK_BORDER};
    border-radius: 6px;
    padding: 4px;
}}
QMenu::item:selected {{
    background-color: {ACCENT};
    color: {DARK_BG};
    border-radius: 4px;
}}
"""


# ---------------------------------------------------------------------------
# Worker thread for validation
# ---------------------------------------------------------------------------
class ValidationWorker(QThread):
    """Runs validation in a background thread."""

    log_signal = pyqtSignal(str, str)  # (text, colour)
    done_signal = pyqtSignal(object)  # ValidationReport or None
    error_signal = pyqtSignal(str)

    def __init__(
        self,
        delivery_path,
        profile_path,
        linelist_path,
        output_path,
        variables,
        basic,
        folder_filter,
    ):
        super().__init__()
        self.delivery_path = delivery_path
        self.profile_path = profile_path
        self.linelist_path = linelist_path
        self.output_path = output_path
        self.variables = variables
        self.basic = basic
        self.folder_filter = folder_filter

    def run(self):
        try:
            from handover_check.engine import ValidationEngine

            self.log_signal.emit("Initializing validation engine...", ACCENT)

            engine = ValidationEngine(
                delivery_path=Path(self.delivery_path),
                profile_path=Path(self.profile_path) if self.profile_path else None,
                linelist_path=Path(self.linelist_path) if self.linelist_path else None,
                cli_vars=self.variables,
                basic=self.basic,
                folder_filter=self.folder_filter or None,
            )

            self.log_signal.emit("Running validation...\n", ACCENT)
            report = engine.run()

            # Format console output
            lines = self._format_report(report)
            for text, colour in lines:
                self.log_signal.emit(text, colour)

            # Excel report
            if self.output_path:
                from handover_check.reporters.excel import generate_excel_report

                self.log_signal.emit(
                    f"\nSaving Excel report to: {self.output_path}", ACCENT
                )
                generate_excel_report(report, Path(self.output_path))
                self.log_signal.emit("Excel report saved successfully.", SUCCESS)

            self.done_signal.emit(report)

        except Exception as e:
            self.error_signal.emit(f"{type(e).__name__}: {e}\n{traceback.format_exc()}")

    def _format_report(self, report):
        """Return list of (text, colour) tuples for console display."""
        lines = []
        sep = "=" * 64

        lines.append((sep, TEXT_SECONDARY))
        lines.append(("  Handover Package Validation Report", ACCENT))
        lines.append(
            (
                f"  Project: {report.project or 'N/A'} | "
                f"Client: {report.client or 'N/A'}",
                TEXT_PRIMARY,
            )
        )
        lines.append(
            (f"  Profile: {report.profile_name}", TEXT_PRIMARY)
        )
        lines.append((f"  Path: {self.delivery_path}", TEXT_PRIMARY))
        lines.append(
            (f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", TEXT_PRIMARY)
        )
        lines.append((sep, TEXT_SECONDARY))
        lines.append(("", TEXT_PRIMARY))

        # Folder results
        lines.append(("Folder Checks:", TEXT_PRIMARY))
        for fr in report.folder_results:
            s = fr.status.value if hasattr(fr.status, "value") else str(fr.status)
            colour = _status_colour(s)
            name = fr.path
            dots = "." * max(2, 50 - len(name))
            lines.append((f"  {name} {dots} [{s}]", colour))
            for rr in fr.rule_results:
                rs = rr.status.value if hasattr(rr.status, "value") else str(rr.status)
                if rs in ("FAIL", "WARNING"):
                    lines.append(
                        (f"    └ {rr.message}", _status_colour(rs))
                    )

        # Global results
        lines.append(("", TEXT_PRIMARY))
        lines.append(("Global Checks:", TEXT_PRIMARY))
        for rr in report.global_results:
            rs = rr.status.value if hasattr(rr.status, "value") else str(rr.status)
            colour = _status_colour(rs)
            name = rr.rule_type.replace("_", " ").title()
            dots = "." * max(2, 50 - len(name))
            lines.append((f"  {name} {dots} [{rs}]", colour))
            if rs in ("FAIL", "WARNING") and rr.details:
                for d in rr.details[:5]:
                    lines.append((f"    └ {d}", colour))
                if len(rr.details) > 5:
                    lines.append(
                        (f"    └ ... and {len(rr.details) - 5} more", colour)
                    )
            elif rs == "INFO" and rr.message:
                lines.append((f"    └ {rr.message}", INFO))

        # Summary
        lines.append(("", TEXT_PRIMARY))
        lines.append((sep, TEXT_SECONDARY))
        total_files = len(report.file_inventory) if report.file_inventory else 0
        total_size_str = ""
        if report.file_inventory:
            total_bytes = sum(f.size_bytes for f in report.file_inventory)
            total_size_str = _format_size(total_bytes)

        overall = report.overall_status
        ov = overall.value if hasattr(overall, "value") else str(overall)
        overall_colour = _status_colour(ov)
        fail_count = report.fail_count

        lines.append(
            (
                f"  Total files: {total_files}  |  Total size: {total_size_str}",
                TEXT_PRIMARY,
            )
        )
        if ov == "PASS":
            lines.append((f"  Result: [{ov}] — All checks passed!", overall_colour))
        else:
            lines.append(
                (
                    f"  Result: [{ov}] ({fail_count} issue(s) found)",
                    overall_colour,
                )
            )
        lines.append((sep, TEXT_SECONDARY))

        return lines


def _status_colour(status):
    return {
        "PASS": SUCCESS,
        "FAIL": ERROR,
        "WARNING": WARNING,
        "INFO": INFO,
        "SKIP": SKIP,
    }.get(status, TEXT_PRIMARY)


def _format_size(nbytes):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} PB"


# ---------------------------------------------------------------------------
# Variable row widget
# ---------------------------------------------------------------------------
class VariableRow(QWidget):
    """A key=value pair row with a remove button."""

    removed = pyqtSignal(object)

    def __init__(self, key="", value="", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.key_edit = QLineEdit(key)
        self.key_edit.setPlaceholderText("variable name")
        self.key_edit.setFixedWidth(160)

        eq_label = QLabel("=")
        eq_label.setFixedWidth(12)
        eq_label.setAlignment(Qt.AlignCenter)

        self.val_edit = QLineEdit(value)
        self.val_edit.setPlaceholderText("value")

        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(28, 28)
        self.remove_btn.setStyleSheet(
            f"QPushButton {{ color: {ERROR}; font-size: 16px; border: none; }}"
            f"QPushButton:hover {{ background-color: {DARK_BORDER}; border-radius: 4px; }}"
        )
        self.remove_btn.clicked.connect(lambda: self.removed.emit(self))

        layout.addWidget(self.key_edit)
        layout.addWidget(eq_label)
        layout.addWidget(self.val_edit, 1)
        layout.addWidget(self.remove_btn)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Handover Package Validator")
        self.setMinimumSize(900, 720)
        self.resize(1000, 800)
        self.worker = None
        self.last_report = None

        self._build_menu()
        self._build_ui()
        self._build_statusbar()

    # ---- Menu ----
    def _build_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        open_act = QAction("Open Delivery Folder...", self)
        open_act.setShortcut("Ctrl+O")
        open_act.triggered.connect(self._browse_delivery)
        file_menu.addAction(open_act)

        file_menu.addSeparator()

        exit_act = QAction("Exit", self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        help_menu = menubar.addMenu("Help")
        about_act = QAction("About", self)
        about_act.triggered.connect(self._show_about)
        help_menu.addAction(about_act)

    # ---- UI ----
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 8, 16, 8)
        main_layout.setSpacing(10)

        # --- Title ---
        title_frame = QWidget()
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 4, 0, 4)

        title_label = QLabel("Handover Package Validator")
        title_label.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {ACCENT};"
        )
        subtitle = QLabel("Delivery folder validation tool")
        subtitle.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY};")

        title_left = QVBoxLayout()
        title_left.setSpacing(2)
        title_left.addWidget(title_label)
        title_left.addWidget(subtitle)
        title_layout.addLayout(title_left)
        title_layout.addStretch()

        main_layout.addWidget(title_frame)

        # --- Splitter: top (settings) / bottom (output) ---
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(6)

        # TOP: settings
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)

        # -- Path settings --
        paths_group = QGroupBox("Paths")
        paths_grid = QGridLayout(paths_group)
        paths_grid.setHorizontalSpacing(8)
        paths_grid.setVerticalSpacing(8)

        self.delivery_edit = QLineEdit()
        self.delivery_edit.setPlaceholderText("Select delivery folder to validate...")
        delivery_btn = QPushButton("Browse")
        delivery_btn.setFixedWidth(80)
        delivery_btn.clicked.connect(self._browse_delivery)

        self.profile_edit = QLineEdit()
        self.profile_edit.setPlaceholderText("Select YAML profile...")
        profile_btn = QPushButton("Browse")
        profile_btn.setFixedWidth(80)
        profile_btn.clicked.connect(self._browse_profile)

        self.linelist_edit = QLineEdit()
        self.linelist_edit.setPlaceholderText("(Optional) Select line list CSV...")
        linelist_btn = QPushButton("Browse")
        linelist_btn.setFixedWidth(80)
        linelist_btn.clicked.connect(self._browse_linelist)

        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("(Optional) Excel report output path...")
        output_btn = QPushButton("Browse")
        output_btn.setFixedWidth(80)
        output_btn.clicked.connect(self._browse_output)

        row = 0
        for label_text, edit, btn in [
            ("Delivery Path", self.delivery_edit, delivery_btn),
            ("Profile", self.profile_edit, profile_btn),
            ("Line List", self.linelist_edit, linelist_btn),
            ("Output (.xlsx)", self.output_edit, output_btn),
        ]:
            lbl = QLabel(label_text)
            lbl.setFixedWidth(100)
            lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
            paths_grid.addWidget(lbl, row, 0)
            paths_grid.addWidget(edit, row, 1)
            paths_grid.addWidget(btn, row, 2)
            row += 1

        top_layout.addWidget(paths_group)

        # -- Variables + options row --
        mid_row = QHBoxLayout()
        mid_row.setSpacing(10)

        # Variables
        vars_group = QGroupBox("Variables (--var)")
        vars_layout = QVBoxLayout(vars_group)
        vars_layout.setSpacing(4)

        self.var_rows_layout = QVBoxLayout()
        self.var_rows_layout.setSpacing(4)
        self.var_rows = []

        vars_layout.addLayout(self.var_rows_layout)

        add_var_btn = QPushButton("+ Add Variable")
        add_var_btn.setFixedWidth(140)
        add_var_btn.clicked.connect(lambda: self._add_var_row("", ""))
        vars_layout.addWidget(add_var_btn)

        mid_row.addWidget(vars_group, 2)

        # Options
        opts_group = QGroupBox("Options")
        opts_layout = QVBoxLayout(opts_group)

        self.basic_check = QCheckBox("Basic mode (skip line list matching)")
        opts_layout.addWidget(self.basic_check)

        filter_row = QHBoxLayout()
        filter_lbl = QLabel("Folder filter:")
        filter_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("e.g. 01_Raw_Data")
        filter_row.addWidget(filter_lbl)
        filter_row.addWidget(self.filter_edit)
        opts_layout.addLayout(filter_row)

        opts_layout.addStretch()

        mid_row.addWidget(opts_group, 1)
        top_layout.addLayout(mid_row)

        # -- Action buttons --
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        self.profile_btn = QPushButton("Show Profile")
        self.profile_btn.setObjectName("profileBtn")
        self.profile_btn.clicked.connect(self._show_profile)
        btn_row.addWidget(self.profile_btn)

        self.run_btn = QPushButton("▶  Validate")
        self.run_btn.setObjectName("runBtn")
        self.run_btn.clicked.connect(self._run_validation)
        btn_row.addWidget(self.run_btn)

        btn_row.addStretch()
        top_layout.addLayout(btn_row)

        splitter.addWidget(top_widget)

        # BOTTOM: output tabs
        self.output_tabs = QTabWidget()

        # Console tab
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self._console_welcome()
        self.output_tabs.addTab(self.console, "Console Output")

        # Results table tab
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(
            ["Folder / Rule", "Status", "Type", "Details"]
        )
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet(
            f"QTableWidget {{ alternate-background-color: {DARK_SURFACE}; }}"
        )
        self.output_tabs.addTab(self.results_table, "Results Table")

        splitter.addWidget(self.output_tabs)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter, 1)

        # Progress bar (hidden initially)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        self.progress.hide()
        main_layout.addWidget(self.progress)

    # ---- Status bar ----
    def _build_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")

    # ---- Console helpers ----
    def _console_welcome(self):
        self.console.clear()
        self._append_console(
            "Handover Package Validator\n"
            "─────────────────────────────────────────\n"
            "1. Set delivery path and profile\n"
            "2. Add variables (project_code, area_code, etc.)\n"
            "3. Click [Validate] to run\n",
            TEXT_SECONDARY,
        )

    def _append_console(self, text, colour=TEXT_PRIMARY):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(colour))
        cursor = self.console.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text + "\n", fmt)
        self.console.setTextCursor(cursor)
        self.console.ensureCursorVisible()

    def _clear_console(self):
        self.console.clear()

    # ---- Browse handlers ----
    def _browse_delivery(self):
        path = QFileDialog.getExistingDirectory(self, "Select Delivery Folder")
        if path:
            self.delivery_edit.setText(path)

    def _browse_profile(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Profile", "", "YAML Files (*.yaml *.yml);;All Files (*)"
        )
        if path:
            self.profile_edit.setText(path)

    def _browse_linelist(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Line List", "", "CSV Files (*.csv);;All Files (*)"
        )
        if path:
            self.linelist_edit.setText(path)

    def _browse_output(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Excel Report", "", "Excel Files (*.xlsx)"
        )
        if path:
            if not path.endswith(".xlsx"):
                path += ".xlsx"
            self.output_edit.setText(path)

    # ---- Variable rows ----
    def _add_var_row(self, key="", value=""):
        row = VariableRow(key, value)
        row.removed.connect(self._remove_var_row)
        self.var_rows.append(row)
        self.var_rows_layout.addWidget(row)
        return row

    def _remove_var_row(self, row):
        if row in self.var_rows:
            self.var_rows.remove(row)
            self.var_rows_layout.removeWidget(row)
            row.deleteLater()

    def _get_variables(self):
        result = {}
        for row in self.var_rows:
            key = row.key_edit.text().strip()
            val = row.val_edit.text().strip()
            if key:
                result[key] = val
        return result

    # ---- Validation ----
    def _run_validation(self):
        delivery = self.delivery_edit.text().strip()
        profile = self.profile_edit.text().strip()

        if not delivery:
            QMessageBox.warning(self, "Missing Input", "Delivery path is required.")
            return
        if not profile:
            QMessageBox.warning(self, "Missing Input", "Profile is required.")
            return
        if not os.path.isdir(delivery):
            QMessageBox.warning(
                self, "Invalid Path", f"Delivery path does not exist:\n{delivery}"
            )
            return
        if not os.path.isfile(profile):
            QMessageBox.warning(
                self, "Invalid File", f"Profile file does not exist:\n{profile}"
            )
            return

        self._clear_console()
        self.results_table.setRowCount(0)
        self.output_tabs.setCurrentIndex(0)
        self.run_btn.setEnabled(False)
        self.profile_btn.setEnabled(False)
        self.progress.show()
        self.statusbar.showMessage("Validating...")

        self.worker = ValidationWorker(
            delivery_path=delivery,
            profile_path=profile,
            linelist_path=self.linelist_edit.text().strip(),
            output_path=self.output_edit.text().strip(),
            variables=self._get_variables(),
            basic=self.basic_check.isChecked(),
            folder_filter=self.filter_edit.text().strip(),
        )
        self.worker.log_signal.connect(self._append_console)
        self.worker.done_signal.connect(self._on_validation_done)
        self.worker.error_signal.connect(self._on_validation_error)
        self.worker.start()

    def _on_validation_done(self, report):
        self.last_report = report
        self.progress.hide()
        self.run_btn.setEnabled(True)
        self.profile_btn.setEnabled(True)

        if report:
            overall = report.overall_status
            fails = report.fail_count
            warns = report.warning_count
            self.statusbar.showMessage(
                f"Done — {overall} | {fails} fail(s), {warns} warning(s)"
            )
            self._populate_results_table(report)
        else:
            self.statusbar.showMessage("Done")

    def _on_validation_error(self, msg):
        self.progress.hide()
        self.run_btn.setEnabled(True)
        self.profile_btn.setEnabled(True)
        self._append_console(f"\nERROR:\n{msg}", ERROR)
        self.statusbar.showMessage("Error occurred")

    def _populate_results_table(self, report):
        rows = []
        for fr in report.folder_results:
            for rr in fr.rule_results:
                s = rr.status.value if hasattr(rr.status, "value") else str(rr.status)
                rows.append((fr.path, s, rr.rule_type, rr.message or ""))
        for rr in report.global_results:
            s = rr.status.value if hasattr(rr.status, "value") else str(rr.status)
            rows.append(("(global)", s, rr.rule_type, rr.message or ""))

        self.results_table.setRowCount(len(rows))
        for i, (folder, status, rtype, msg) in enumerate(rows):
            items = [
                QTableWidgetItem(folder),
                QTableWidgetItem(status),
                QTableWidgetItem(rtype),
                QTableWidgetItem(msg),
            ]
            colour = QColor(_status_colour(status))
            items[1].setForeground(colour)
            for j, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.results_table.setItem(i, j, item)

    # ---- Show profile ----
    def _show_profile(self):
        profile = self.profile_edit.text().strip()
        if not profile or not os.path.isfile(profile):
            QMessageBox.warning(
                self, "No Profile", "Select a valid profile file first."
            )
            return

        try:
            from handover_check.config import load_and_merge_profile, resolve_variables

            merged = load_and_merge_profile(profile)
            variables = resolve_variables(merged, self._get_variables())

            self._clear_console()
            self._append_console("Merged Profile (with variables resolved):", ACCENT)
            self._append_console("─" * 50, TEXT_SECONDARY)

            import yaml

            text = yaml.dump(merged, default_flow_style=False, allow_unicode=True)
            self._append_console(text, TEXT_PRIMARY)

            self._append_console("\nResolved Variables:", ACCENT)
            for k, v in variables.items():
                self._append_console(f"  {k} = {v}", TEXT_PRIMARY)

            self.output_tabs.setCurrentIndex(0)
            self.statusbar.showMessage("Profile loaded")

        except Exception as e:
            self._append_console(f"Error loading profile: {e}", ERROR)

    # ---- About ----
    def _show_about(self):
        QMessageBox.about(
            self,
            "About",
            "<h3>Handover Package Validator</h3>"
            "<p>Delivery folder validation tool for geophysical survey projects.</p>"
            "<p>Version 1.0.0</p>"
            "<p>Validates delivery folders against YAML profiles and generates "
            "detailed Excel reports.</p>",
        )


# ---------------------------------------------------------------------------
# Patched interpretation-first UI helpers
# ---------------------------------------------------------------------------
def _set_text_view(view, text):
    view.clear()
    view.setPlainText(text)
    cursor = view.textCursor()
    cursor.movePosition(cursor.Start)
    view.setTextCursor(cursor)


def _patched_worker_format_report(self, report):
    """Return list of (text, colour) tuples for console display."""
    lines = []
    sep = "=" * 64
    insight = build_readiness_insight(report)

    lines.append((sep, TEXT_SECONDARY))
    lines.append(("  Handover Package Validation Report", ACCENT))
    lines.append(
        (
            f"  Project: {report.project or 'N/A'} | "
            f"Client: {report.client or 'N/A'}",
            TEXT_PRIMARY,
        )
    )
    lines.append((f"  Profile: {report.profile_name}", TEXT_PRIMARY))
    lines.append((f"  Path: {self.delivery_path}", TEXT_PRIMARY))
    lines.append(
        (f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", TEXT_PRIMARY)
    )
    lines.append((sep, TEXT_SECONDARY))
    lines.append(("", TEXT_PRIMARY))
    lines.append(
        (
            f"Readiness: {insight.readiness_percent}% - {insight.readiness_label}",
            ACCENT,
        )
    )
    lines.append((f"  {insight.headline}", TEXT_PRIMARY))
    for action in insight.top_actions:
        lines.append((f"  Next: {action}", TEXT_SECONDARY))
    for note in insight.trust_notes:
        lines.append((f"  Note: {note}", TEXT_SECONDARY))

    lines.append(("", TEXT_PRIMARY))
    lines.append(("Folder Checks:", TEXT_PRIMARY))
    for folder_result in report.folder_results:
        status = (
            folder_result.status.value
            if hasattr(folder_result.status, "value")
            else str(folder_result.status)
        )
        colour = _status_colour(status)
        dots = "." * max(2, 50 - len(folder_result.path))
        lines.append((f"  {folder_result.path} {dots} [{status}]", colour))
        for rule_result in folder_result.rule_results:
            rule_status = (
                rule_result.status.value
                if hasattr(rule_result.status, "value")
                else str(rule_result.status)
            )
            if rule_status in ("FAIL", "WARNING"):
                lines.append((f"    - {rule_result.message}", _status_colour(rule_status)))

    lines.append(("", TEXT_PRIMARY))
    lines.append(("Global Checks:", TEXT_PRIMARY))
    for rule_result in report.global_results:
        rule_status = (
            rule_result.status.value
            if hasattr(rule_result.status, "value")
            else str(rule_result.status)
        )
        colour = _status_colour(rule_status)
        name = rule_result.rule_type.replace("_", " ").title()
        dots = "." * max(2, 50 - len(name))
        lines.append((f"  {name} {dots} [{rule_status}]", colour))
        if rule_status in ("FAIL", "WARNING") and rule_result.details:
            for detail in rule_result.details[:5]:
                lines.append((f"    - {detail}", colour))
            if len(rule_result.details) > 5:
                lines.append(
                    (f"    - ... and {len(rule_result.details) - 5} more", colour)
                )
        elif rule_status == "INFO" and rule_result.message:
            lines.append((f"    - {rule_result.message}", INFO))

    total_size = _format_size(sum(file.size_bytes for file in report.file_inventory))
    overall_value = (
        report.overall_status.value
        if hasattr(report.overall_status, "value")
        else str(report.overall_status)
    )
    lines.append(("", TEXT_PRIMARY))
    lines.append((sep, TEXT_SECONDARY))
    lines.append(
        (
            f"  Total files: {len(report.file_inventory)}  |  Total size: {total_size}",
            TEXT_PRIMARY,
        )
    )
    if overall_value == "PASS":
        lines.append((f"  Result: [{overall_value}] All checks passed.", SUCCESS))
    else:
        lines.append(
            (
                f"  Result: [{overall_value}] "
                f"({insight.failed_checks} failed check(s), {insight.warning_checks} warning check(s))",
                _status_colour(overall_value),
            )
        )
    lines.append((sep, TEXT_SECONDARY))
    return lines


def _patched_add_var_row(self, key="", value=""):
    row = VariableRow(key, value)
    row.removed.connect(self._remove_var_row)
    if hasattr(row, "remove_btn"):
        row.remove_btn.setText("x")
    self.var_rows.append(row)
    self.var_rows_layout.addWidget(row)
    return row


def _patched_console_welcome(self):
    self.console.clear()
    self._append_console(
        "Handover Package Validator\n"
        "----------------------------------------\n"
        "1. Select the delivery folder and profile.\n"
        "2. Preview the validation plan so the scope is clear.\n"
        "3. Add variables such as project_code or area_code.\n"
        "4. Run validation and review readiness, issues, and line coverage.\n",
        TEXT_SECONDARY,
    )


def _patched_build_ui(self):
    central = QWidget()
    self.setCentralWidget(central)
    main_layout = QVBoxLayout(central)
    main_layout.setContentsMargins(16, 8, 16, 8)
    main_layout.setSpacing(10)

    title_frame = QWidget()
    title_layout = QHBoxLayout(title_frame)
    title_layout.setContentsMargins(0, 4, 0, 4)

    title_label = QLabel("Handover Package Validator")
    title_label.setStyleSheet(
        f"font-size: 20px; font-weight: bold; color: {ACCENT};"
    )
    subtitle = QLabel("Interpret validation results as delivery readiness, not just log output.")
    subtitle.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY};")

    title_left = QVBoxLayout()
    title_left.setSpacing(2)
    title_left.addWidget(title_label)
    title_left.addWidget(subtitle)
    title_layout.addLayout(title_left)
    title_layout.addStretch()
    main_layout.addWidget(title_frame)

    splitter = QSplitter(Qt.Vertical)
    splitter.setHandleWidth(6)

    top_widget = QWidget()
    top_layout = QVBoxLayout(top_widget)
    top_layout.setContentsMargins(0, 0, 0, 0)
    top_layout.setSpacing(8)

    paths_group = QGroupBox("Paths")
    paths_grid = QGridLayout(paths_group)
    paths_grid.setHorizontalSpacing(8)
    paths_grid.setVerticalSpacing(8)

    self.delivery_edit = QLineEdit()
    self.delivery_edit.setPlaceholderText("Select the delivery folder to validate...")
    delivery_btn = QPushButton("Browse")
    delivery_btn.setFixedWidth(80)
    delivery_btn.clicked.connect(self._browse_delivery)

    self.profile_edit = QLineEdit()
    self.profile_edit.setPlaceholderText("Select a YAML profile...")
    profile_btn = QPushButton("Browse")
    profile_btn.setFixedWidth(80)
    profile_btn.clicked.connect(self._browse_profile)

    self.linelist_edit = QLineEdit()
    self.linelist_edit.setPlaceholderText("(Optional) Select a line list CSV...")
    linelist_btn = QPushButton("Browse")
    linelist_btn.setFixedWidth(80)
    linelist_btn.clicked.connect(self._browse_linelist)

    self.output_edit = QLineEdit()
    self.output_edit.setPlaceholderText("(Optional) Choose where to save the Excel report...")
    output_btn = QPushButton("Browse")
    output_btn.setFixedWidth(80)
    output_btn.clicked.connect(self._browse_output)

    for row_index, (label_text, edit, button) in enumerate(
        [
            ("Delivery Path", self.delivery_edit, delivery_btn),
            ("Profile", self.profile_edit, profile_btn),
            ("Line List", self.linelist_edit, linelist_btn),
            ("Output (.xlsx)", self.output_edit, output_btn),
        ]
    ):
        label = QLabel(label_text)
        label.setFixedWidth(100)
        label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
        paths_grid.addWidget(label, row_index, 0)
        paths_grid.addWidget(edit, row_index, 1)
        paths_grid.addWidget(button, row_index, 2)

    top_layout.addWidget(paths_group)

    mid_row = QHBoxLayout()
    mid_row.setSpacing(10)

    vars_group = QGroupBox("Variables (--var)")
    vars_layout = QVBoxLayout(vars_group)
    vars_layout.setSpacing(4)

    self.var_rows_layout = QVBoxLayout()
    self.var_rows_layout.setSpacing(4)
    self.var_rows = []
    vars_layout.addLayout(self.var_rows_layout)

    add_var_btn = QPushButton("+ Add Variable")
    add_var_btn.setFixedWidth(140)
    add_var_btn.clicked.connect(lambda: self._add_var_row("", ""))
    vars_layout.addWidget(add_var_btn)
    mid_row.addWidget(vars_group, 2)

    opts_group = QGroupBox("Options")
    opts_layout = QVBoxLayout(opts_group)

    self.basic_check = QCheckBox("Basic mode (use the base profile only)")
    opts_layout.addWidget(self.basic_check)

    filter_row = QHBoxLayout()
    filter_label = QLabel("Folder filter:")
    filter_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
    self.filter_edit = QLineEdit()
    self.filter_edit.setPlaceholderText("Example: 01_Raw_Data/01_SBP")
    filter_row.addWidget(filter_label)
    filter_row.addWidget(self.filter_edit)
    opts_layout.addLayout(filter_row)
    opts_layout.addStretch()

    mid_row.addWidget(opts_group, 1)
    top_layout.addLayout(mid_row)

    button_row = QHBoxLayout()
    button_row.setSpacing(12)
    button_row.addStretch()

    self.profile_btn = QPushButton("Preview Plan")
    self.profile_btn.setObjectName("profileBtn")
    self.profile_btn.clicked.connect(self._show_profile)
    button_row.addWidget(self.profile_btn)

    self.run_btn = QPushButton("Validate")
    self.run_btn.setObjectName("runBtn")
    self.run_btn.clicked.connect(self._run_validation)
    button_row.addWidget(self.run_btn)

    button_row.addStretch()
    top_layout.addLayout(button_row)

    splitter.addWidget(top_widget)

    self.output_tabs = QTabWidget()

    self.summary_view = QTextEdit()
    self.summary_view.setReadOnly(True)
    self.output_tabs.addTab(self.summary_view, "Readiness Summary")

    self.results_table = QTableWidget()
    self.results_table.setColumnCount(8)
    self.results_table.setHorizontalHeaderLabels(
        [
            "Section",
            "Severity",
            "Status",
            "Check",
            "Category",
            "Finding",
            "Next Step",
            "Evidence",
        ]
    )
    self.results_table.horizontalHeader().setStretchLastSection(True)
    self.results_table.horizontalHeader().setSectionResizeMode(
        0, QHeaderView.ResizeToContents
    )
    self.results_table.verticalHeader().setVisible(False)
    self.results_table.setAlternatingRowColors(True)
    self.results_table.setStyleSheet(
        f"QTableWidget {{ alternate-background-color: {DARK_SURFACE}; }}"
    )
    self.results_table.itemSelectionChanged.connect(
        self._update_issue_detail_view_from_selection
    )
    self.output_tabs.addTab(self.results_table, "Issue Register")

    self.issue_detail_view = QTextEdit()
    self.issue_detail_view.setReadOnly(True)
    self.output_tabs.addTab(self.issue_detail_view, "Issue Detail")

    self.line_coverage_table = QTableWidget()
    self.line_coverage_table.verticalHeader().setVisible(False)
    self.line_coverage_table.setAlternatingRowColors(True)
    self.line_coverage_table.setStyleSheet(
        f"QTableWidget {{ alternate-background-color: {DARK_SURFACE}; }}"
    )
    self.output_tabs.addTab(self.line_coverage_table, "Line Coverage")

    compare_widget = QWidget()
    compare_layout = QVBoxLayout(compare_widget)
    compare_layout.setContentsMargins(8, 8, 8, 8)
    compare_layout.setSpacing(8)
    compare_controls = QHBoxLayout()
    compare_controls.setSpacing(8)
    compare_controls.addWidget(QLabel("Left section"))
    self.compare_left_combo = QComboBox()
    self.compare_left_combo.currentTextChanged.connect(self._refresh_compare_view)
    compare_controls.addWidget(self.compare_left_combo, 1)
    compare_controls.addWidget(QLabel("Right section"))
    self.compare_right_combo = QComboBox()
    self.compare_right_combo.currentTextChanged.connect(self._refresh_compare_view)
    compare_controls.addWidget(self.compare_right_combo, 1)
    compare_layout.addLayout(compare_controls)
    self.compare_view = QTextEdit()
    self.compare_view.setReadOnly(True)
    compare_layout.addWidget(self.compare_view, 1)
    self.output_tabs.addTab(compare_widget, "Section Compare")

    self.report_preview_view = QTextEdit()
    self.report_preview_view.setReadOnly(True)
    self.output_tabs.addTab(self.report_preview_view, "Report Preview")

    self.plan_view = QTextEdit()
    self.plan_view.setReadOnly(True)
    self.output_tabs.addTab(self.plan_view, "Validation Plan")

    self.console = QTextEdit()
    self.console.setReadOnly(True)
    self.output_tabs.addTab(self.console, "Console Output")

    splitter.addWidget(self.output_tabs)
    splitter.setStretchFactor(0, 0)
    splitter.setStretchFactor(1, 1)
    main_layout.addWidget(splitter, 1)

    self.progress = QProgressBar()
    self.progress.setRange(0, 0)
    self.progress.setFixedHeight(4)
    self.progress.setTextVisible(False)
    self.progress.hide()
    main_layout.addWidget(self.progress)

    self._console_welcome()
    _set_text_view(
        self.summary_view,
        "Run validation to see readiness, grouped issues, and next actions.",
    )
    _set_text_view(
        self.issue_detail_view,
        "Select an issue in Issue Register to see detail, evidence, and next action.",
    )
    _set_text_view(
        self.plan_view,
        "Use Preview Plan to inspect the profile-driven validation scope before running.",
    )
    _set_text_view(
        self.compare_view,
        "Run validation, then choose two sections to compare their readiness and issue load.",
    )
    _set_text_view(
        self.report_preview_view,
        "Run validation to preview the narrative that will be exported to the report.",
    )
    self._populate_line_coverage_table(None)


def _populate_line_coverage_table(self, report):
    if not report or not report.line_coverage:
        self.line_coverage_table.clear()
        self.line_coverage_table.setColumnCount(1)
        self.line_coverage_table.setRowCount(1)
        self.line_coverage_table.setHorizontalHeaderLabels(["Line Coverage"])
        message = QTableWidgetItem(
            "No line coverage matrix is available for this run."
        )
        message.setFlags(message.flags() & ~Qt.ItemIsEditable)
        self.line_coverage_table.setItem(0, 0, message)
        self.line_coverage_table.horizontalHeader().setStretchLastSection(True)
        return

    coverage = report.line_coverage
    folders = coverage.get("folders", [])
    lines = coverage.get("lines", [])
    matrix = coverage.get("matrix", {})

    self.line_coverage_table.clear()
    self.line_coverage_table.setColumnCount(1 + len(folders))
    self.line_coverage_table.setRowCount(len(lines))
    self.line_coverage_table.setHorizontalHeaderLabels(["Line"] + folders)
    self.line_coverage_table.horizontalHeader().setStretchLastSection(True)

    for row_index, line in enumerate(lines):
        line_item = QTableWidgetItem(line)
        line_item.setFlags(line_item.flags() & ~Qt.ItemIsEditable)
        self.line_coverage_table.setItem(row_index, 0, line_item)

        for column_index, folder in enumerate(folders, 1):
            found = bool(matrix.get(line, {}).get(folder, False))
            value = "OK" if found else "Missing"
            item = QTableWidgetItem(value)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setForeground(QColor(SUCCESS if found else ERROR))
            self.line_coverage_table.setItem(row_index, column_index, item)


def _populate_compare_options(self, report):
    self.compare_left_combo.blockSignals(True)
    self.compare_right_combo.blockSignals(True)
    self.compare_left_combo.clear()
    self.compare_right_combo.clear()

    scopes = [folder_result.path for folder_result in report.folder_results] if report else []
    if scopes:
        self.compare_left_combo.addItems(scopes)
        self.compare_right_combo.addItems(scopes)
        if len(scopes) > 1:
            self.compare_right_combo.setCurrentIndex(1)
    else:
        self.compare_left_combo.addItem("")
        self.compare_right_combo.addItem("")

    self.compare_left_combo.blockSignals(False)
    self.compare_right_combo.blockSignals(False)
    self._refresh_compare_view()


def _refresh_compare_view(self):
    report = getattr(self, "last_report", None)
    if not report:
        _set_text_view(
            self.compare_view,
            "Run validation, then choose two sections to compare their readiness and issue load.",
        )
        return

    text = build_section_compare_text(
        report,
        self.compare_left_combo.currentText().strip() or None,
        self.compare_right_combo.currentText().strip() or None,
    )
    _set_text_view(self.compare_view, text)


def _update_issue_detail_view_from_selection(self):
    issues = getattr(self, "current_issues", [])
    selected_row = self.results_table.currentRow()
    if not issues or selected_row < 0 or selected_row >= len(issues):
        _set_text_view(
            self.issue_detail_view,
            format_issue_detail_text(None),
        )
        return
    _set_text_view(
        self.issue_detail_view,
        format_issue_detail_text(issues[selected_row]),
    )


def _patched_run_validation(self):
    delivery = self.delivery_edit.text().strip()
    profile = self.profile_edit.text().strip()

    if not delivery:
        QMessageBox.warning(self, "Missing Input", "Delivery path is required.")
        return
    if not profile:
        QMessageBox.warning(self, "Missing Input", "Profile is required.")
        return
    if not os.path.isdir(delivery):
        QMessageBox.warning(
            self, "Invalid Path", f"Delivery path does not exist:\n{delivery}"
        )
        return
    if not os.path.isfile(profile):
        QMessageBox.warning(
            self, "Invalid File", f"Profile file does not exist:\n{profile}"
        )
        return

    self._clear_console()
    _set_text_view(self.summary_view, "Validation is running. Readiness summary will appear here.")
    _set_text_view(
        self.issue_detail_view,
        "Validation is running. Issue detail will appear after results are loaded.",
    )
    _set_text_view(
        self.compare_view,
        "Validation is running. Section comparison will appear after results are loaded.",
    )
    _set_text_view(
        self.report_preview_view,
        "Validation is running. Report preview will appear after results are loaded.",
    )
    self._populate_results_table(None)
    self._populate_line_coverage_table(None)
    self._populate_compare_options(None)
    self.output_tabs.setCurrentWidget(self.summary_view)
    self.run_btn.setEnabled(False)
    self.profile_btn.setEnabled(False)
    self.progress.show()
    self.statusbar.showMessage("Validating package...")

    self.worker = ValidationWorker(
        delivery_path=delivery,
        profile_path=profile,
        linelist_path=self.linelist_edit.text().strip(),
        output_path=self.output_edit.text().strip(),
        variables=self._get_variables(),
        basic=self.basic_check.isChecked(),
        folder_filter=self.filter_edit.text().strip(),
    )
    self.worker.log_signal.connect(self._append_console)
    self.worker.done_signal.connect(self._on_validation_done)
    self.worker.error_signal.connect(self._on_validation_error)
    self.worker.start()


def _patched_on_validation_done(self, report):
    self.last_report = report
    self.progress.hide()
    self.run_btn.setEnabled(True)
    self.profile_btn.setEnabled(True)

    if not report:
        self.statusbar.showMessage("Validation finished.")
        return

    insight = build_readiness_insight(report)
    _set_text_view(self.summary_view, format_readiness_text(insight))
    self._populate_results_table(report)
    self._populate_line_coverage_table(report)
    self._populate_compare_options(report)
    _set_text_view(self.report_preview_view, build_report_preview_text(report))
    self.output_tabs.setCurrentWidget(self.summary_view)
    self.statusbar.showMessage(
        f"{insight.readiness_label} | "
        f"{insight.failed_checks} failed check(s), {insight.warning_checks} warning check(s)"
    )


def _patched_on_validation_error(self, msg):
    self.progress.hide()
    self.run_btn.setEnabled(True)
    self.profile_btn.setEnabled(True)
    self._append_console(f"\nERROR:\n{msg}", ERROR)
    _set_text_view(
        self.summary_view,
        "Validation failed before a readiness summary could be generated.\n\nCheck the Console Output tab for details.",
    )
    _set_text_view(
        self.issue_detail_view,
        "Validation failed before issue detail could be generated.",
    )
    _set_text_view(
        self.compare_view,
        "Validation failed before section comparison could be generated.",
    )
    _set_text_view(
        self.report_preview_view,
        "Validation failed before the report preview could be generated.",
    )
    self.statusbar.showMessage("Validation error")


def _patched_populate_results_table(self, report):
    self.results_table.clearContents()
    self.current_issues = []
    if not report:
        self.results_table.setColumnCount(8)
        self.results_table.setRowCount(1)
        self.results_table.setHorizontalHeaderLabels(
            [
                "Section",
                "Severity",
                "Status",
                "Check",
                "Category",
                "Finding",
                "Next Step",
                "Evidence",
            ]
        )
        placeholder = QTableWidgetItem("No validation results yet.")
        placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEditable)
        self.results_table.setItem(0, 0, placeholder)
        self._update_issue_detail_view_from_selection()
        return

    issues = build_readiness_insight(report).issues
    self.current_issues = issues
    self.results_table.setRowCount(max(1, len(issues)))
    if not issues:
        placeholder = QTableWidgetItem("No issues found.")
        placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEditable)
        self.results_table.setItem(0, 0, placeholder)
        self._update_issue_detail_view_from_selection()
        return

    for row_index, issue in enumerate(issues):
        evidence_text = "\n".join(issue.details[:5]) if issue.details else ""
        if len(issue.details) > 5:
            evidence_text += f"\n... +{len(issue.details) - 5} more"

        items = [
            QTableWidgetItem(issue.scope),
            QTableWidgetItem(issue.severity),
            QTableWidgetItem(issue.status.value),
            QTableWidgetItem(issue.check_label),
            QTableWidgetItem(issue.category),
            QTableWidgetItem(issue.message),
            QTableWidgetItem(issue.action_hint),
            QTableWidgetItem(evidence_text or "See finding"),
        ]
        items[1].setForeground(QColor(ERROR if issue.severity == "Blocker" else WARNING))
        items[2].setForeground(QColor(_status_colour(issue.status.value)))
        for column_index, item in enumerate(items):
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row_index, column_index, item)

    self.results_table.selectRow(0)
    self._update_issue_detail_view_from_selection()


def _patched_show_profile(self):
    profile = self.profile_edit.text().strip()
    if not profile or not os.path.isfile(profile):
        QMessageBox.warning(
            self, "No Profile", "Select a valid profile file first."
        )
        return

    try:
        import yaml

        from handover_check.config import load_and_merge_profile, resolve_variables

        merged = load_and_merge_profile(Path(profile))
        variables = resolve_variables(merged, self._get_variables())
        plan = build_profile_plan(
            merged,
            variables,
            basic=self.basic_check.isChecked(),
            folder_filter=self.filter_edit.text().strip() or None,
            linelist_override=self.linelist_edit.text().strip() or None,
        )

        _set_text_view(self.plan_view, format_profile_plan_text(plan))
        self.output_tabs.setCurrentWidget(self.plan_view)
        self.statusbar.showMessage("Validation plan loaded")

        self._clear_console()
        self._append_console("Merged Profile (for reference):", ACCENT)
        self._append_console("-" * 50, TEXT_SECONDARY)
        text = yaml.dump(merged, default_flow_style=False, allow_unicode=True, sort_keys=False)
        self._append_console(text, TEXT_PRIMARY)

    except Exception as e:
        self._append_console(f"Error loading profile: {e}", ERROR)
        self.statusbar.showMessage("Failed to load profile")


ValidationWorker._format_report = _patched_worker_format_report
MainWindow._add_var_row = _patched_add_var_row
MainWindow._console_welcome = _patched_console_welcome
MainWindow._build_ui = _patched_build_ui
MainWindow._populate_line_coverage_table = _populate_line_coverage_table
MainWindow._populate_compare_options = _populate_compare_options
MainWindow._refresh_compare_view = _refresh_compare_view
MainWindow._update_issue_detail_view_from_selection = _update_issue_detail_view_from_selection
MainWindow._run_validation = _patched_run_validation
MainWindow._on_validation_done = _patched_on_validation_done
MainWindow._on_validation_error = _patched_on_validation_error
MainWindow._populate_results_table = _patched_populate_results_table
MainWindow._show_profile = _patched_show_profile


def _ui_lang(self):
    return normalize_lang(getattr(self, "current_language", "ko"))


def _set_results_headers_v2(self):
    lang = _ui_lang(self)
    self.results_table.setHorizontalHeaderLabels(
        [
            tr("col_section", lang),
            tr("col_severity", lang),
            tr("col_status", lang),
            tr("col_check", lang),
            tr("col_category", lang),
            tr("col_finding", lang),
            tr("col_next_step", lang),
            tr("col_evidence", lang),
        ]
    )


def _refresh_views_for_language_v2(self):
    lang = _ui_lang(self)
    report = getattr(self, "last_report", None)
    plan = getattr(self, "current_profile_plan", None)

    if report:
        insight = build_readiness_insight(report, lang)
        _set_text_view(self.summary_view, format_readiness_text(insight, lang))
        self._populate_results_table(report)
        self._populate_line_coverage_table(report)
        self._populate_compare_options(report)
        _set_text_view(self.report_preview_view, build_report_preview_text(report, lang))
    else:
        _set_text_view(self.summary_view, tr("summary_placeholder", lang))
        self._populate_results_table(None)
        self._populate_line_coverage_table(None)
        self._populate_compare_options(None)
        _set_text_view(self.issue_detail_view, tr("issue_detail_placeholder", lang))
        _set_text_view(self.compare_view, tr("compare_placeholder", lang))
        _set_text_view(self.report_preview_view, tr("report_preview_placeholder", lang))

    if plan:
        _set_text_view(self.plan_view, format_profile_plan_text(plan, lang))
    else:
        _set_text_view(self.plan_view, tr("plan_placeholder", lang))

    if not report:
        self._update_issue_detail_view_from_selection()


def _apply_language_v2(self, announce=False):
    lang = _ui_lang(self)

    self.setWindowTitle(tr("app_title", lang))

    if hasattr(self, "file_menu"):
        self.file_menu.setTitle(tr("file_menu", lang))
    if hasattr(self, "help_menu"):
        self.help_menu.setTitle(tr("help_menu", lang))
    if hasattr(self, "open_act"):
        self.open_act.setText(tr("open_delivery_folder", lang))
    if hasattr(self, "exit_act"):
        self.exit_act.setText(tr("exit", lang))
    if hasattr(self, "about_act"):
        self.about_act.setText(tr("about", lang))

    self.title_label.setText(tr("app_title", lang))
    self.subtitle_label.setText(tr("app_subtitle", lang))
    self.language_text_label.setText(tr("language", lang))

    self.paths_group.setTitle(tr("group_paths", lang))
    self.vars_group.setTitle(tr("group_variables", lang))
    self.opts_group.setTitle(tr("group_options", lang))

    self.delivery_label.setText(tr("delivery_path", lang))
    self.profile_label.setText(tr("profile", lang))
    self.linelist_label.setText(tr("line_list", lang))
    self.output_label.setText(tr("output_excel", lang))

    self.delivery_edit.setPlaceholderText(tr("placeholder_delivery", lang))
    self.profile_edit.setPlaceholderText(tr("placeholder_profile", lang))
    self.linelist_edit.setPlaceholderText(tr("placeholder_linelist", lang))
    self.output_edit.setPlaceholderText(tr("placeholder_output", lang))

    for button in (
        self.delivery_btn,
        self.profile_browse_btn,
        self.linelist_btn,
        self.output_btn,
    ):
        button.setText(tr("browse", lang))

    self.add_var_btn.setText(tr("add_variable", lang))
    for row in getattr(self, "var_rows", []):
        row.key_edit.setPlaceholderText(tr("variable_name", lang))
        row.val_edit.setPlaceholderText(tr("variable_value", lang))

    self.basic_check.setText(tr("basic_mode", lang))
    self.filter_label.setText(f"{tr('folder_filter', lang)}:")
    self.filter_edit.setPlaceholderText(tr("placeholder_filter", lang))

    self.profile_btn.setText(tr("preview_plan", lang))
    self.run_btn.setText(tr("validate", lang))

    self.compare_left_label.setText(tr("left_section", lang))
    self.compare_right_label.setText(tr("right_section", lang))

    self.output_tabs.setTabText(self.summary_tab_index, tr("tab_summary", lang))
    self.output_tabs.setTabText(self.issue_register_tab_index, tr("tab_issue_register", lang))
    self.output_tabs.setTabText(self.issue_detail_tab_index, tr("tab_issue_detail", lang))
    self.output_tabs.setTabText(self.line_coverage_tab_index, tr("tab_line_coverage", lang))
    self.output_tabs.setTabText(self.section_compare_tab_index, tr("tab_section_compare", lang))
    self.output_tabs.setTabText(self.report_preview_tab_index, tr("tab_report_preview", lang))
    self.output_tabs.setTabText(self.validation_plan_tab_index, tr("tab_validation_plan", lang))
    self.output_tabs.setTabText(self.console_tab_index, tr("tab_console", lang))
    self._set_results_headers()
    self._refresh_views_for_language()

    if hasattr(self, "statusbar"):
        if announce:
            self.statusbar.showMessage(tr("language_changed", lang))
        elif not getattr(self, "last_report", None):
            self.statusbar.showMessage(tr("ready", lang))


def _on_language_changed_v2(self):
    selected = self.language_combo.currentData() or "ko"
    self.current_language = normalize_lang(selected)
    self._apply_language(announce=True)


def _patched_build_menu_v2(self):
    self.current_language = normalize_lang(getattr(self, "current_language", "ko"))
    self.current_profile_plan = None
    self.current_issues = []
    menubar = self.menuBar()
    menubar.clear()

    self.file_menu = menubar.addMenu("")
    self.open_act = QAction("", self)
    self.open_act.setShortcut("Ctrl+O")
    self.open_act.triggered.connect(self._browse_delivery)
    self.file_menu.addAction(self.open_act)
    self.file_menu.addSeparator()

    self.exit_act = QAction("", self)
    self.exit_act.setShortcut("Ctrl+Q")
    self.exit_act.triggered.connect(self.close)
    self.file_menu.addAction(self.exit_act)

    self.help_menu = menubar.addMenu("")
    self.about_act = QAction("", self)
    self.about_act.triggered.connect(self._show_about)
    self.help_menu.addAction(self.about_act)

    lang = self.current_language
    self.file_menu.setTitle(tr("file_menu", lang))
    self.open_act.setText(tr("open_delivery_folder", lang))
    self.exit_act.setText(tr("exit", lang))
    self.help_menu.setTitle(tr("help_menu", lang))
    self.about_act.setText(tr("about", lang))


def _patched_build_statusbar_v2(self):
    self.statusbar = QStatusBar()
    self.setStatusBar(self.statusbar)
    self.statusbar.showMessage(tr("ready", _ui_lang(self)))


def _patched_browse_delivery_v2(self):
    lang = _ui_lang(self)
    path = QFileDialog.getExistingDirectory(self, tr("select_delivery_folder", lang))
    if path:
        self.delivery_edit.setText(path)


def _patched_browse_profile_v2(self):
    lang = _ui_lang(self)
    path, _ = QFileDialog.getOpenFileName(
        self,
        tr("select_profile", lang),
        "",
        f"{tr('yaml_filter', lang)};;{tr('all_files', lang)}",
    )
    if path:
        self.profile_edit.setText(path)


def _patched_browse_linelist_v2(self):
    lang = _ui_lang(self)
    path, _ = QFileDialog.getOpenFileName(
        self,
        tr("select_line_list", lang),
        "",
        f"{tr('csv_filter', lang)};;{tr('all_files', lang)}",
    )
    if path:
        self.linelist_edit.setText(path)


def _patched_browse_output_v2(self):
    lang = _ui_lang(self)
    path, _ = QFileDialog.getSaveFileName(
        self,
        tr("save_excel_report", lang),
        "",
        tr("excel_filter", lang),
    )
    if path:
        if not path.endswith(".xlsx"):
            path += ".xlsx"
        self.output_edit.setText(path)


def _patched_show_about_v2(self):
    lang = _ui_lang(self)
    QMessageBox.about(self, tr("about_title", lang), tr("about_html", lang))


def _localized_worker_init(
    self,
    delivery_path,
    profile_path,
    linelist_path,
    output_path,
    variables,
    basic,
    folder_filter,
    language="ko",
):
    QThread.__init__(self)
    self.delivery_path = delivery_path
    self.profile_path = profile_path
    self.linelist_path = linelist_path
    self.output_path = output_path
    self.variables = variables
    self.basic = basic
    self.folder_filter = folder_filter
    self.language = normalize_lang(language)


def _localized_worker_run(self):
    try:
        from handover_check.engine import ValidationEngine

        self.log_signal.emit(tr("initializing_engine", self.language), ACCENT)
        engine = ValidationEngine(
            delivery_path=Path(self.delivery_path),
            profile_path=Path(self.profile_path) if self.profile_path else None,
            linelist_path=Path(self.linelist_path) if self.linelist_path else None,
            cli_vars=self.variables,
            basic=self.basic,
            folder_filter=self.folder_filter or None,
            language=self.language,
        )

        self.log_signal.emit(f"{tr('running_validation', self.language)}\n", ACCENT)
        report = engine.run()

        for text, colour in self._format_report(report):
            self.log_signal.emit(text, colour)

        if self.output_path:
            from handover_check.reporters.excel import generate_excel_report

            self.log_signal.emit(
                f"\n{tr('saving_excel_report', self.language, path=self.output_path)}",
                ACCENT,
            )
            generate_excel_report(report, Path(self.output_path))
            self.log_signal.emit(tr("excel_report_saved", self.language), SUCCESS)

        self.done_signal.emit(report)
    except Exception as e:
        self.error_signal.emit(f"{type(e).__name__}: {e}\n{traceback.format_exc()}")


def _localized_worker_format_report(self, report):
    lang = normalize_lang(getattr(report, "language", getattr(self, "language", "en")))
    insight = build_readiness_insight(report, lang)
    lines = []
    sep = "=" * 64

    lines.append((sep, TEXT_SECONDARY))
    lines.append((f"  {tr('console_header', lang)}", ACCENT))
    if report.project or report.client:
        parts = []
        if report.project:
            parts.append(f"{tr('project', lang)}: {report.project}")
        if report.client:
            parts.append(f"{tr('client', lang)}: {report.client}")
        lines.append((f"  {' | '.join(parts)}", TEXT_PRIMARY))
    lines.append((f"  {tr('profile', lang)}: {report.profile_name}", TEXT_PRIMARY))
    lines.append((f"  {tr('delivery_path', lang)}: {self.delivery_path}", TEXT_PRIMARY))
    lines.append((f"  {tr('validated_on', lang)}: {report.timestamp}", TEXT_PRIMARY))
    lines.append((sep, TEXT_SECONDARY))
    lines.append(("", TEXT_PRIMARY))
    lines.append(
        (
            f"{tr('readiness_label', lang)}: "
            f"{insight.readiness_percent}% - {insight.readiness_label}",
            ACCENT,
        )
    )
    lines.append((f"  {insight.headline}", TEXT_PRIMARY))
    for action in insight.top_actions:
        lines.append((f"  {tr('next_label', lang)}: {action}", TEXT_SECONDARY))
    for note in insight.trust_notes:
        lines.append((f"  {tr('trust_note_label', lang)}: {note}", TEXT_SECONDARY))

    lines.append(("", TEXT_PRIMARY))
    lines.append((f"{tr('folder_checks', lang)}:", TEXT_PRIMARY))
    for folder_result in report.folder_results:
        status_value = folder_result.status.value
        colour = _status_colour(status_value)
        dots = "." * max(2, 50 - len(folder_result.path))
        lines.append(
            (
                f"  {folder_result.path} {dots} "
                f"[{status_text(status_value, lang)}]",
                colour,
            )
        )
        for rule_result in folder_result.rule_results:
            if rule_result.status.value in ("FAIL", "WARNING"):
                lines.append(
                    (
                        f"    - {rule_result.message}",
                        _status_colour(rule_result.status.value),
                    )
                )

    lines.append(("", TEXT_PRIMARY))
    lines.append((f"{tr('global_checks_console', lang)}:", TEXT_PRIMARY))
    for rule_result in report.global_results:
        rule_status = rule_result.status.value
        colour = _status_colour(rule_status)
        name = rule_result.rule_type.replace("_", " ").title()
        dots = "." * max(2, 50 - len(name))
        lines.append((f"  {name} {dots} [{status_text(rule_status, lang)}]", colour))
        if rule_status in ("FAIL", "WARNING") and rule_result.details:
            for detail in rule_result.details[:5]:
                lines.append((f"    - {detail}", colour))
            if len(rule_result.details) > 5:
                lines.append((f"    - ... +{len(rule_result.details) - 5}", colour))
        elif rule_status == "INFO" and rule_result.message:
            lines.append((f"    - {rule_result.message}", INFO))

    overall_value = report.overall_status.value
    total_size = _format_size(sum(file.size_bytes for file in report.file_inventory))
    lines.append(("", TEXT_PRIMARY))
    lines.append((sep, TEXT_SECONDARY))
    lines.append(
        (
            f"  {tr('total_files', lang)}: {len(report.file_inventory)}  |  "
            f"{tr('total_size', lang)}: {total_size}",
            TEXT_PRIMARY,
        )
    )
    if overall_value == "PASS":
        lines.append(
            (
                f"  {tr('result_label', lang)}: "
                f"[{status_text(overall_value, lang)}] {tr('all_checks_passed', lang)}",
                SUCCESS,
            )
        )
    else:
        lines.append(
            (
                f"  {tr('result_label', lang)}: "
                f"[{status_text(overall_value, lang)}] "
                f"({tr('issues_found_count', lang, count=insight.failed_checks + insight.warning_checks)})",
                _status_colour(overall_value),
            )
        )
    lines.append((sep, TEXT_SECONDARY))
    return lines


def _patched_console_welcome_v2(self):
    self.console.clear()
    self._append_console(tr("welcome_text", _ui_lang(self)), TEXT_SECONDARY)


def _patched_add_var_row_v2(self, key="", value=""):
    row = VariableRow(key, value)
    row.removed.connect(self._remove_var_row)
    row.key_edit.setPlaceholderText(tr("variable_name", _ui_lang(self)))
    row.val_edit.setPlaceholderText(tr("variable_value", _ui_lang(self)))
    if hasattr(row, "remove_btn"):
        row.remove_btn.setText("x")
    self.var_rows.append(row)
    self.var_rows_layout.addWidget(row)
    return row


def _patched_build_ui_v2(self):
    central = QWidget()
    self.setCentralWidget(central)
    main_layout = QVBoxLayout(central)
    main_layout.setContentsMargins(16, 8, 16, 8)
    main_layout.setSpacing(10)

    title_frame = QWidget()
    title_layout = QHBoxLayout(title_frame)
    title_layout.setContentsMargins(0, 4, 0, 4)

    self.title_label = QLabel()
    self.title_label.setStyleSheet(
        f"font-size: 20px; font-weight: bold; color: {ACCENT};"
    )
    self.subtitle_label = QLabel()
    self.subtitle_label.setStyleSheet(f"font-size: 12px; color: {TEXT_SECONDARY};")

    title_left = QVBoxLayout()
    title_left.setSpacing(2)
    title_left.addWidget(self.title_label)
    title_left.addWidget(self.subtitle_label)
    title_layout.addLayout(title_left)
    title_layout.addStretch()

    lang_layout = QHBoxLayout()
    lang_layout.setSpacing(8)
    self.language_text_label = QLabel()
    self.language_text_label.setStyleSheet(
        f"color: {TEXT_SECONDARY}; font-size: 12px;"
    )
    self.language_combo = QComboBox()
    self.language_combo.setFixedWidth(120)
    self.language_combo.addItem(language_label("ko"), "ko")
    self.language_combo.addItem(language_label("en"), "en")
    current_index = self.language_combo.findData(_ui_lang(self))
    self.language_combo.setCurrentIndex(0 if current_index < 0 else current_index)
    self.language_combo.currentIndexChanged.connect(self._on_language_changed)
    lang_layout.addWidget(self.language_text_label)
    lang_layout.addWidget(self.language_combo)
    title_layout.addLayout(lang_layout)
    main_layout.addWidget(title_frame)

    splitter = QSplitter(Qt.Vertical)
    splitter.setHandleWidth(6)

    top_widget = QWidget()
    top_layout = QVBoxLayout(top_widget)
    top_layout.setContentsMargins(0, 0, 0, 0)
    top_layout.setSpacing(8)

    self.paths_group = QGroupBox()
    paths_grid = QGridLayout(self.paths_group)
    paths_grid.setHorizontalSpacing(8)
    paths_grid.setVerticalSpacing(8)

    self.delivery_edit = QLineEdit()
    self.delivery_btn = QPushButton()
    self.delivery_btn.setFixedWidth(80)
    self.delivery_btn.clicked.connect(self._browse_delivery)

    self.profile_edit = QLineEdit()
    self.profile_browse_btn = QPushButton()
    self.profile_browse_btn.setFixedWidth(80)
    self.profile_browse_btn.clicked.connect(self._browse_profile)

    self.linelist_edit = QLineEdit()
    self.linelist_btn = QPushButton()
    self.linelist_btn.setFixedWidth(80)
    self.linelist_btn.clicked.connect(self._browse_linelist)

    self.output_edit = QLineEdit()
    self.output_btn = QPushButton()
    self.output_btn.setFixedWidth(80)
    self.output_btn.clicked.connect(self._browse_output)

    self.delivery_label = QLabel()
    self.profile_label = QLabel()
    self.linelist_label = QLabel()
    self.output_label = QLabel()
    for label in (
        self.delivery_label,
        self.profile_label,
        self.linelist_label,
        self.output_label,
    ):
        label.setFixedWidth(100)
        label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")

    for row_index, (label, edit, button) in enumerate(
        [
            (self.delivery_label, self.delivery_edit, self.delivery_btn),
            (self.profile_label, self.profile_edit, self.profile_browse_btn),
            (self.linelist_label, self.linelist_edit, self.linelist_btn),
            (self.output_label, self.output_edit, self.output_btn),
        ]
    ):
        paths_grid.addWidget(label, row_index, 0)
        paths_grid.addWidget(edit, row_index, 1)
        paths_grid.addWidget(button, row_index, 2)

    top_layout.addWidget(self.paths_group)

    mid_row = QHBoxLayout()
    mid_row.setSpacing(10)

    self.vars_group = QGroupBox()
    vars_layout = QVBoxLayout(self.vars_group)
    vars_layout.setSpacing(4)
    self.var_rows_layout = QVBoxLayout()
    self.var_rows_layout.setSpacing(4)
    self.var_rows = []
    vars_layout.addLayout(self.var_rows_layout)
    self.add_var_btn = QPushButton()
    self.add_var_btn.setFixedWidth(140)
    self.add_var_btn.clicked.connect(lambda: self._add_var_row("", ""))
    vars_layout.addWidget(self.add_var_btn)
    mid_row.addWidget(self.vars_group, 2)

    self.opts_group = QGroupBox()
    opts_layout = QVBoxLayout(self.opts_group)
    self.basic_check = QCheckBox()
    opts_layout.addWidget(self.basic_check)
    filter_row = QHBoxLayout()
    self.filter_label = QLabel()
    self.filter_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px;")
    self.filter_edit = QLineEdit()
    filter_row.addWidget(self.filter_label)
    filter_row.addWidget(self.filter_edit)
    opts_layout.addLayout(filter_row)
    opts_layout.addStretch()
    mid_row.addWidget(self.opts_group, 1)
    top_layout.addLayout(mid_row)

    button_row = QHBoxLayout()
    button_row.setSpacing(12)
    button_row.addStretch()
    self.profile_btn = QPushButton()
    self.profile_btn.setObjectName("profileBtn")
    self.profile_btn.clicked.connect(self._show_profile)
    button_row.addWidget(self.profile_btn)
    self.run_btn = QPushButton()
    self.run_btn.setObjectName("runBtn")
    self.run_btn.clicked.connect(self._run_validation)
    button_row.addWidget(self.run_btn)
    button_row.addStretch()
    top_layout.addLayout(button_row)

    splitter.addWidget(top_widget)
    self.output_tabs = QTabWidget()

    self.summary_view = QTextEdit()
    self.summary_view.setReadOnly(True)
    self.summary_tab_index = self.output_tabs.addTab(self.summary_view, "")

    self.results_table = QTableWidget()
    self.results_table.setColumnCount(8)
    self.results_table.horizontalHeader().setStretchLastSection(True)
    self.results_table.horizontalHeader().setSectionResizeMode(
        0, QHeaderView.ResizeToContents
    )
    self.results_table.verticalHeader().setVisible(False)
    self.results_table.setAlternatingRowColors(True)
    self.results_table.setStyleSheet(
        f"QTableWidget {{ alternate-background-color: {DARK_SURFACE}; }}"
    )
    self.results_table.itemSelectionChanged.connect(
        self._update_issue_detail_view_from_selection
    )
    self.issue_register_tab_index = self.output_tabs.addTab(self.results_table, "")

    self.issue_detail_view = QTextEdit()
    self.issue_detail_view.setReadOnly(True)
    self.issue_detail_tab_index = self.output_tabs.addTab(self.issue_detail_view, "")

    self.line_coverage_table = QTableWidget()
    self.line_coverage_table.verticalHeader().setVisible(False)
    self.line_coverage_table.setAlternatingRowColors(True)
    self.line_coverage_table.setStyleSheet(
        f"QTableWidget {{ alternate-background-color: {DARK_SURFACE}; }}"
    )
    self.line_coverage_tab_index = self.output_tabs.addTab(self.line_coverage_table, "")

    compare_widget = QWidget()
    compare_layout = QVBoxLayout(compare_widget)
    compare_layout.setContentsMargins(8, 8, 8, 8)
    compare_layout.setSpacing(8)
    compare_controls = QHBoxLayout()
    compare_controls.setSpacing(8)
    self.compare_left_label = QLabel()
    self.compare_left_combo = QComboBox()
    self.compare_left_combo.currentTextChanged.connect(self._refresh_compare_view)
    self.compare_right_label = QLabel()
    self.compare_right_combo = QComboBox()
    self.compare_right_combo.currentTextChanged.connect(self._refresh_compare_view)
    compare_controls.addWidget(self.compare_left_label)
    compare_controls.addWidget(self.compare_left_combo, 1)
    compare_controls.addWidget(self.compare_right_label)
    compare_controls.addWidget(self.compare_right_combo, 1)
    compare_layout.addLayout(compare_controls)
    self.compare_view = QTextEdit()
    self.compare_view.setReadOnly(True)
    compare_layout.addWidget(self.compare_view, 1)
    self.section_compare_tab_index = self.output_tabs.addTab(compare_widget, "")

    self.report_preview_view = QTextEdit()
    self.report_preview_view.setReadOnly(True)
    self.report_preview_tab_index = self.output_tabs.addTab(
        self.report_preview_view, ""
    )

    self.plan_view = QTextEdit()
    self.plan_view.setReadOnly(True)
    self.validation_plan_tab_index = self.output_tabs.addTab(self.plan_view, "")

    self.console = QTextEdit()
    self.console.setReadOnly(True)
    self.console_tab_index = self.output_tabs.addTab(self.console, "")

    splitter.addWidget(self.output_tabs)
    splitter.setStretchFactor(0, 0)
    splitter.setStretchFactor(1, 1)
    main_layout.addWidget(splitter, 1)

    self.progress = QProgressBar()
    self.progress.setRange(0, 0)
    self.progress.setFixedHeight(4)
    self.progress.setTextVisible(False)
    self.progress.hide()
    main_layout.addWidget(self.progress)

    self._set_results_headers()
    self._console_welcome()
    self._apply_language()


def _populate_line_coverage_table_v2(self, report):
    lang = _ui_lang(self)
    if not report or not report.line_coverage:
        self.line_coverage_table.clear()
        self.line_coverage_table.setColumnCount(1)
        self.line_coverage_table.setRowCount(1)
        self.line_coverage_table.setHorizontalHeaderLabels([tr("tab_line_coverage", lang)])
        message = QTableWidgetItem(tr("no_line_coverage", lang))
        message.setFlags(message.flags() & ~Qt.ItemIsEditable)
        self.line_coverage_table.setItem(0, 0, message)
        self.line_coverage_table.horizontalHeader().setStretchLastSection(True)
        return

    coverage = report.line_coverage
    folders = coverage.get("folders", [])
    lines = coverage.get("lines", [])
    matrix = coverage.get("matrix", {})

    self.line_coverage_table.clear()
    self.line_coverage_table.setColumnCount(1 + len(folders))
    self.line_coverage_table.setRowCount(len(lines))
    self.line_coverage_table.setHorizontalHeaderLabels([tr("col_line", lang)] + folders)
    self.line_coverage_table.horizontalHeader().setStretchLastSection(True)

    for row_index, line in enumerate(lines):
        line_item = QTableWidgetItem(line)
        line_item.setFlags(line_item.flags() & ~Qt.ItemIsEditable)
        self.line_coverage_table.setItem(row_index, 0, line_item)

        for column_index, folder in enumerate(folders, 1):
            found = bool(matrix.get(line, {}).get(folder, False))
            value = tr("ok", lang) if found else tr("missing", lang)
            item = QTableWidgetItem(value)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setForeground(QColor(SUCCESS if found else ERROR))
            self.line_coverage_table.setItem(row_index, column_index, item)


def _populate_compare_options_v2(self, report):
    left_selected = self.compare_left_combo.currentText()
    right_selected = self.compare_right_combo.currentText()
    self.compare_left_combo.blockSignals(True)
    self.compare_right_combo.blockSignals(True)
    self.compare_left_combo.clear()
    self.compare_right_combo.clear()

    scopes = [folder_result.path for folder_result in report.folder_results] if report else []
    if scopes:
        self.compare_left_combo.addItems(scopes)
        self.compare_right_combo.addItems(scopes)
        left_index = self.compare_left_combo.findText(left_selected)
        right_index = self.compare_right_combo.findText(right_selected)
        self.compare_left_combo.setCurrentIndex(0 if left_index < 0 else left_index)
        if right_index >= 0:
            self.compare_right_combo.setCurrentIndex(right_index)
        elif len(scopes) > 1:
            self.compare_right_combo.setCurrentIndex(1)
    else:
        self.compare_left_combo.addItem("")
        self.compare_right_combo.addItem("")

    self.compare_left_combo.blockSignals(False)
    self.compare_right_combo.blockSignals(False)
    self._refresh_compare_view()


def _refresh_compare_view_v2(self):
    report = getattr(self, "last_report", None)
    lang = _ui_lang(self)
    if not report:
        _set_text_view(self.compare_view, tr("compare_placeholder", lang))
        return

    _set_text_view(
        self.compare_view,
        build_section_compare_text(
            report,
            self.compare_left_combo.currentText().strip() or None,
            self.compare_right_combo.currentText().strip() or None,
            lang,
        ),
    )


def _update_issue_detail_view_from_selection_v2(self):
    lang = _ui_lang(self)
    issues = getattr(self, "current_issues", [])
    selected_row = self.results_table.currentRow()
    if not issues or selected_row < 0 or selected_row >= len(issues):
        _set_text_view(self.issue_detail_view, format_issue_detail_text(None, lang))
        return
    _set_text_view(
        self.issue_detail_view,
        format_issue_detail_text(issues[selected_row], lang),
    )


def _patched_run_validation_v2(self):
    lang = _ui_lang(self)
    delivery = self.delivery_edit.text().strip()
    profile = self.profile_edit.text().strip()

    if not delivery:
        QMessageBox.warning(self, tr("missing_input", lang), tr("delivery_required", lang))
        return
    if not profile:
        QMessageBox.warning(self, tr("missing_input", lang), tr("profile_required", lang))
        return
    if not os.path.isdir(delivery):
        QMessageBox.warning(
            self,
            tr("invalid_path", lang),
            tr("delivery_path_not_found", lang, path=delivery),
        )
        return
    if not os.path.isfile(profile):
        QMessageBox.warning(
            self,
            tr("invalid_file", lang),
            tr("profile_file_not_found", lang, path=profile),
        )
        return

    self._clear_console()
    _set_text_view(self.summary_view, tr("summary_running", lang))
    _set_text_view(self.issue_detail_view, tr("issue_detail_running", lang))
    _set_text_view(self.compare_view, tr("compare_running", lang))
    _set_text_view(self.report_preview_view, tr("report_preview_running", lang))
    self._populate_results_table(None)
    self._populate_line_coverage_table(None)
    self._populate_compare_options(None)
    self.output_tabs.setCurrentWidget(self.summary_view)
    self.run_btn.setEnabled(False)
    self.profile_btn.setEnabled(False)
    self.progress.show()
    self.statusbar.showMessage(tr("validating", lang))

    self.worker = ValidationWorker(
        delivery_path=delivery,
        profile_path=profile,
        linelist_path=self.linelist_edit.text().strip(),
        output_path=self.output_edit.text().strip(),
        variables=self._get_variables(),
        basic=self.basic_check.isChecked(),
        folder_filter=self.filter_edit.text().strip(),
        language=lang,
    )
    self.worker.log_signal.connect(self._append_console)
    self.worker.done_signal.connect(self._on_validation_done)
    self.worker.error_signal.connect(self._on_validation_error)
    self.worker.start()


def _patched_on_validation_done_v2(self, report):
    lang = _ui_lang(self)
    self.last_report = report
    self.progress.hide()
    self.run_btn.setEnabled(True)
    self.profile_btn.setEnabled(True)

    if not report:
        self.statusbar.showMessage(tr("validation_finished", lang))
        return

    insight = build_readiness_insight(report, lang)
    _set_text_view(self.summary_view, format_readiness_text(insight, lang))
    self._populate_results_table(report)
    self._populate_line_coverage_table(report)
    self._populate_compare_options(report)
    _set_text_view(self.report_preview_view, build_report_preview_text(report, lang))
    self.output_tabs.setCurrentWidget(self.summary_view)
    self.statusbar.showMessage(
        tr(
            "status_with_counts",
            lang,
            label=insight.readiness_label,
            failed=insight.failed_checks,
            warning=insight.warning_checks,
        )
    )


def _patched_on_validation_error_v2(self, msg):
    lang = _ui_lang(self)
    self.progress.hide()
    self.run_btn.setEnabled(True)
    self.profile_btn.setEnabled(True)
    self._append_console(f"\nERROR:\n{msg}", ERROR)
    _set_text_view(self.summary_view, tr("validation_failed_summary", lang))
    _set_text_view(self.issue_detail_view, tr("validation_failed_issue_detail", lang))
    _set_text_view(self.compare_view, tr("validation_failed_compare", lang))
    _set_text_view(self.report_preview_view, tr("validation_failed_report_preview", lang))
    self.statusbar.showMessage(tr("validation_error", lang))


def _patched_populate_results_table_v2(self, report):
    lang = _ui_lang(self)
    selected_row = self.results_table.currentRow()
    self.results_table.clearContents()
    self.results_table.setColumnCount(8)
    self._set_results_headers()
    self.current_issues = []
    if not report:
        self.results_table.setRowCount(1)
        placeholder = QTableWidgetItem(tr("no_results_yet", lang))
        placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEditable)
        self.results_table.setItem(0, 0, placeholder)
        self._update_issue_detail_view_from_selection()
        return

    issues = build_readiness_insight(report, lang).issues
    self.current_issues = issues
    self.results_table.setRowCount(max(1, len(issues)))
    if not issues:
        placeholder = QTableWidgetItem(tr("no_issues_found", lang))
        placeholder.setFlags(placeholder.flags() & ~Qt.ItemIsEditable)
        self.results_table.setItem(0, 0, placeholder)
        self._update_issue_detail_view_from_selection()
        return

    for row_index, issue in enumerate(issues):
        evidence_text = "\n".join(issue.details[:5]) if issue.details else ""
        if len(issue.details) > 5:
            evidence_text += f"\n... +{len(issue.details) - 5} more"

        items = [
            QTableWidgetItem(issue.scope),
            QTableWidgetItem(severity_text(issue.severity, lang)),
            QTableWidgetItem(status_text(issue.status.value, lang)),
            QTableWidgetItem(issue.check_label),
            QTableWidgetItem(issue.category),
            QTableWidgetItem(issue.message),
            QTableWidgetItem(issue.action_hint),
            QTableWidgetItem(evidence_text or tr("see_finding", lang)),
        ]
        items[1].setForeground(QColor(ERROR if issue.severity == "Blocker" else WARNING))
        items[2].setForeground(QColor(_status_colour(issue.status.value)))
        for column_index, item in enumerate(items):
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.results_table.setItem(row_index, column_index, item)

    target_row = 0 if selected_row < 0 else min(selected_row, len(issues) - 1)
    self.results_table.selectRow(target_row)
    self._update_issue_detail_view_from_selection()


def _patched_show_profile_v2(self):
    lang = _ui_lang(self)
    profile = self.profile_edit.text().strip()
    if not profile or not os.path.isfile(profile):
        QMessageBox.warning(self, tr("no_profile", lang), tr("select_valid_profile_first", lang))
        return

    try:
        import yaml

        from handover_check.config import load_and_merge_profile, resolve_variables

        merged = load_and_merge_profile(Path(profile))
        variables = resolve_variables(merged, self._get_variables())
        plan = build_profile_plan(
            merged,
            variables,
            basic=self.basic_check.isChecked(),
            folder_filter=self.filter_edit.text().strip() or None,
            linelist_override=self.linelist_edit.text().strip() or None,
            lang=lang,
        )
        self.current_profile_plan = plan

        _set_text_view(self.plan_view, format_profile_plan_text(plan, lang))
        self.output_tabs.setCurrentWidget(self.plan_view)
        self.statusbar.showMessage(tr("profile_loaded", lang))

        self._clear_console()
        self._append_console(tr("merged_profile_reference", lang), ACCENT)
        self._append_console("-" * 50, TEXT_SECONDARY)
        text = yaml.dump(
            merged,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
        self._append_console(text, TEXT_PRIMARY)

    except Exception as e:
        self._append_console(f"{tr('error_loading_profile', lang)}: {e}", ERROR)
        self.statusbar.showMessage(tr("profile_load_failed", lang))


ValidationWorker.__init__ = _localized_worker_init
ValidationWorker.run = _localized_worker_run
ValidationWorker._format_report = _localized_worker_format_report
MainWindow._build_menu = _patched_build_menu_v2
MainWindow._build_statusbar = _patched_build_statusbar_v2
MainWindow._browse_delivery = _patched_browse_delivery_v2
MainWindow._browse_profile = _patched_browse_profile_v2
MainWindow._browse_linelist = _patched_browse_linelist_v2
MainWindow._browse_output = _patched_browse_output_v2
MainWindow._show_about = _patched_show_about_v2
MainWindow._console_welcome = _patched_console_welcome_v2
MainWindow._add_var_row = _patched_add_var_row_v2
MainWindow._build_ui = _patched_build_ui_v2
MainWindow._set_results_headers = _set_results_headers_v2
MainWindow._refresh_views_for_language = _refresh_views_for_language_v2
MainWindow._apply_language = _apply_language_v2
MainWindow._on_language_changed = _on_language_changed_v2
MainWindow._populate_line_coverage_table = _populate_line_coverage_table_v2
MainWindow._populate_compare_options = _populate_compare_options_v2
MainWindow._refresh_compare_view = _refresh_compare_view_v2
MainWindow._update_issue_detail_view_from_selection = _update_issue_detail_view_from_selection_v2
MainWindow._run_validation = _patched_run_validation_v2
MainWindow._on_validation_done = _patched_on_validation_done_v2
MainWindow._on_validation_error = _patched_on_validation_error_v2
MainWindow._populate_results_table = _patched_populate_results_table_v2
MainWindow._show_profile = _patched_show_profile_v2


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    # High-DPI scaling
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Handover Package Validator")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(DARK_BG))
    palette.setColor(QPalette.WindowText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Base, QColor(DARK_SURFACE))
    palette.setColor(QPalette.AlternateBase, QColor(DARK_BG))
    palette.setColor(QPalette.ToolTipBase, QColor(DARK_SURFACE))
    palette.setColor(QPalette.ToolTipText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Text, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Button, QColor(DARK_SURFACE))
    palette.setColor(QPalette.ButtonText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.HighlightedText, QColor(DARK_BG))
    app.setPalette(palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
