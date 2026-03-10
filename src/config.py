# -*- coding: utf-8 -*-
"""
Branding and configuration paths for LYTE Installer.
Replace files in branding/ to rebrand; no code changes needed.
"""

import os
import sys

# Base path: when running from PyInstaller, use _MEIPASS; otherwise project root
if getattr(sys, "frozen", False):
    _BASE = os.path.join(sys._MEIPASS, "branding")
else:
    _BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "branding")

# Icon paths (required for installer/uninstaller)
INSTALL_ICON = os.path.join(_BASE, "ico", "install.ico")
UNINSTALL_ICON = os.path.join(_BASE, "ico", "uninstall.ico")

# Optional wizard images (fallback to solid color if missing)
HEADER_IMAGE = os.path.join(_BASE, "headerimage.bmp")
HEADER_IMAGE_PNG = os.path.join(_BASE, "header.png")
WIZARD_IMAGE = os.path.join(_BASE, "wizard.bmp")
WIZARD_IMAGE_PNG = os.path.join(_BASE, "sidebar.png")


def get_header_path() -> str | None:
    """Return path to header image if it exists."""
    for p in (HEADER_IMAGE_PNG, HEADER_IMAGE):
        if os.path.isfile(p):
            return p
    return None


def get_wizard_path() -> str | None:
    """Return path to wizard/sidebar image if it exists."""
    for p in (WIZARD_IMAGE_PNG, WIZARD_IMAGE):
        if os.path.isfile(p):
            return p
    return None


def get_install_icon_path() -> str | None:
    """Return path to install icon if it exists."""
    return INSTALL_ICON if os.path.isfile(INSTALL_ICON) else None


def get_uninstall_icon_path() -> str | None:
    """Return path to uninstall icon if it exists."""
    return UNINSTALL_ICON if os.path.isfile(UNINSTALL_ICON) else None
