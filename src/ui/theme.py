# -*- coding: utf-8 -*-
"""
LYTE dark theme QSS for installer UI.
Matches LYTE dark_theme.json colors.
"""

import os
import sys

def _get_checkmark_path() -> str:
    """Resolve path to checkmark.svg (works when frozen or from source)."""
    if getattr(sys, "frozen", False):
        path = os.path.join(sys._MEIPASS, "src", "ui", "checkmark.svg")
    else:
        path = os.path.join(os.path.dirname(__file__), "checkmark.svg")
    return path if os.path.isfile(path) else ""

_CHECKBOX_CHECKED_IMAGE = ""
_path = _get_checkmark_path()
if _path:
    _CHECKBOX_CHECKED_IMAGE = f"image: url({_path.replace(chr(92), '/')});"


def get_stylesheet() -> str:
    """Return the stylesheet with resolved paths."""
    return LYTE_DARK_QSS.replace("{checkmark_style}", _CHECKBOX_CHECKED_IMAGE)


LYTE_DARK_QSS = """
QMainWindow, QWidget {
    background-color: #191919;
    color: #dcdcdc;
}

QFrame#card {
    background-color: #232323;
    border: 1px solid #465a46;
    border-radius: 8px;
    padding: 12px;
}

QLabel {
    color: #dcdcdc;
}

QLabel[class="secondary"] {
    color: #666666;
}

QLabel[class="title"] {
    font-size: 12pt;
    font-weight: bold;
}

QPushButton {
    background-color: #3c463c;
    color: #dcdcdc;
    border: 1px solid #465a46;
    border-radius: 8px;
    padding: 8px 16px;
    font-family: "Segoe UI", sans-serif;
}

QPushButton:hover {
    background-color: #507850;
}

QPushButton:pressed {
    background-color: #649664;
}

QPushButton:disabled {
    background-color: #2d2d2d;
    color: #666666;
}

QComboBox {
    background-color: #232323;
    color: #dcdcdc;
    border: 1px solid #465a46;
    border-radius: 8px;
    padding: 6px 12px;
    min-height: 24px;
}

QComboBox:hover {
    border-color: #507850;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #232323;
    color: #dcdcdc;
}

QLineEdit {
    background-color: #232323;
    color: #dcdcdc;
    border: 1px solid #465a46;
    border-radius: 8px;
    padding: 6px 12px;
}

QLineEdit:focus {
    border-color: #507850;
}

QCheckBox {
    color: #dcdcdc;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #465a46;
    background-color: #232323;
}

QCheckBox::indicator:checked {
    background-color: #649664;
    border-color: #85b585;
    {checkmark_style}
}

QProgressBar {
    background-color: #232323;
    border: 1px solid #465a46;
    border-radius: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #649664;
    border-radius: 7px;
}

QScrollArea {
    border: none;
    background: transparent;
}
"""
