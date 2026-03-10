# -*- coding: utf-8 -*-
"""
Standalone uninstaller for LYTE.
Reads install path from registry, removes files, shortcuts, registry keys.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import winreg

REG_UNINSTALL = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE"
REG_LYTE = r"Software\LYTE"


def get_install_dir() -> str | None:
    """Read install directory from registry."""
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            REG_UNINSTALL,
            0,
            winreg.KEY_READ,
        )
        path, _ = winreg.QueryValueEx(key, "InstallLocation")
        winreg.CloseKey(key)
        return path
    except OSError:
        pass
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            REG_LYTE,
            0,
            winreg.KEY_READ,
        )
        path, _ = winreg.QueryValueEx(key, "Install_Dir")
        winreg.CloseKey(key)
        return path
    except OSError:
        pass
    return None


def message_box(title: str, text: str, style: int = 0) -> int:
    """Show Windows MessageBox. Returns IDOK, IDCANCEL, IDYES, IDNO."""
    import ctypes
    from ctypes import wintypes
    return ctypes.windll.user32.MessageBoxW(
        None,
        text,
        title,
        style,
    )


def uninstall(install_dir: str, remove_config: bool) -> None:
    """Remove LYTE files, shortcuts, registry."""
    # Remove LYTE.exe
    lyte_exe = os.path.join(install_dir, "LYTE.exe")
    if os.path.isfile(lyte_exe):
        try:
            os.remove(lyte_exe)
        except OSError:
            pass

    # Remove config files if requested
    if remove_config:
        for name in ("banned_IDs.json", "banned_users.json", "config.json"):
            p = os.path.join(install_dir, name)
            if os.path.isfile(p):
                try:
                    os.remove(p)
                except OSError:
                    pass
        for f in os.listdir(install_dir):
            if f.endswith(".log"):
                try:
                    os.remove(os.path.join(install_dir, f))
                except OSError:
                    pass
        logs_dir = os.path.join(install_dir, "logs")
        if os.path.isdir(logs_dir):
            try:
                shutil.rmtree(logs_dir)
            except OSError:
                pass

    # Remove shortcuts
    start_menu = os.path.join(
        os.environ.get("ProgramData", "C:\\ProgramData"),
        "Microsoft", "Windows", "Start Menu", "Programs", "LYTE",
    )
    for name in ("LYTE.lnk", "Uninstall LYTE.lnk"):
        p = os.path.join(start_menu, name)
        if os.path.isfile(p):
            try:
                os.remove(p)
            except OSError:
                pass
    if os.path.isdir(start_menu) and not os.listdir(start_menu):
        try:
            os.rmdir(start_menu)
        except OSError:
            pass

    desktop = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
    desktop_lnk = os.path.join(desktop, "LYTE.lnk")
    if os.path.isfile(desktop_lnk):
        try:
            os.remove(desktop_lnk)
        except OSError:
            pass

    # Remove registry
    for key_path in (REG_UNINSTALL, REG_LYTE):
        try:
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        except OSError:
            pass

    # Remove uninstaller itself and folder via batch script (can't delete running exe)
    uninstaller_exe = sys.executable if getattr(sys, "frozen", False) else __file__
    if not os.path.isfile(uninstaller_exe):
        uninstaller_exe = os.path.join(install_dir, "Uninstall LYTE.exe")
    batch = f'''@echo off
ping -n 2 127.0.0.1 >nul
del /f /q "{uninstaller_exe}"
rmdir /s /q "{install_dir}" 2>nul
del /f /q "%~f0"
'''
    with tempfile.NamedTemporaryFile(suffix=".bat", delete=False) as f:
        f.write(batch.encode())
        batch_path = f.name
    subprocess.Popen(["cmd", "/c", batch_path], creationflags=subprocess.CREATE_NO_WINDOW)


def main():
    install_dir = get_install_dir()
    if not install_dir or not os.path.isdir(install_dir):
        message_box(
            "Uninstall LYTE",
            "LYTE installation not found. It may have already been uninstalled.",
            0x40,  # MB_ICONINFORMATION
        )
        return

    # MB_ICONQUESTION | MB_YESNO
    r = message_box(
        "Uninstall LYTE",
        "Are you sure you want to completely remove LYTE?",
        0x24,
    )
    if r != 6:  # IDYES
        return

    r = message_box(
        "Uninstall LYTE",
        "Do you also want to remove all settings and configuration files?\n(config.json, banned lists, logs)",
        0x24,
    )
    remove_config = r == 6  # IDYES

    uninstall(install_dir, remove_config)

    message_box(
        "Uninstall LYTE",
        "LYTE has been successfully uninstalled from your computer.",
        0x40,
    )


if __name__ == "__main__":
    main()
