# -*- coding: utf-8 -*-
"""
LYTE Installer entry point.
"""

import sys
import os

# Ensure project root is on path when running from source
if not getattr(sys, "frozen", False):
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _root not in sys.path:
        sys.path.insert(0, _root)

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LYTE Installer")
    app.setOrganizationName("StroepWafel")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
