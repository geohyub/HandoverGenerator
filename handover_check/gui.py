"""Handover Package Validator — Professional GUI (PyQt5)."""

import os
import sys
import threading
import traceback
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QIcon, QTextCharFormat, QPalette, QPixmap
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
    QFrame,
    QScrollArea,
    QToolButton,
    QSizePolicy,
    QMessageBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAction,
    QMenuBar,
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
