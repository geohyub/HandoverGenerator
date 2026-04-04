from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget


class VariableRow(QWidget):
    removed = Signal(object)

    def __init__(self, key: str = "", value: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.key_edit = QLineEdit(key)
        self.key_edit.setFixedWidth(180)
        self.value_edit = QLineEdit(value)
        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(28, 28)
        self.remove_btn.clicked.connect(lambda: self.removed.emit(self))
        layout.addWidget(self.key_edit)
        layout.addWidget(QLabel("="))
        layout.addWidget(self.value_edit, 1)
        layout.addWidget(self.remove_btn)
