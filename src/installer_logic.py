# -*- coding: utf-8 -*-
"""
Install logic: download LYTE.exe, optional VLC, create shortcuts, registry.
"""

import os
import shutil
import subprocess
import tempfile
import winreg
from typing import Callable

import requests

VLC_URL = "https://mirror.aarnet.edu.au/pub/videolan/vlc/3.0.21/win64/vlc-3.0.21-win64.exe"
REG_UNINSTALL = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\LYTE"
REG_LYTE = r"Software\LYTE"


def get_default_install_dir() -> str:
    """Default install directory: Program Files\\LYTE"""
    pf = os.environ.get("ProgramFiles", "C:\\Program Files")
    return os.path.join(pf, "LYTE")


def download_file(url: str, dest: str, progress_callback: Callable[[int, int], None] | None = None) -> None:
    """Download file with optional progress callback (current, total bytes)."""
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        written = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    written += len(chunk)
                    if progress_callback and total:
                        progress_callback(written, total)


def create_shortcut(target: str, shortcut_path: str, icon_path: str | None = None) -> None:
    """Create a Windows shortcut (.lnk) using PowerShell."""
    env = os.environ.copy()
    env["LYTE_TARGET"] = target
    env["LYTE_LNK"] = shortcut_path
    env["LYTE_ICON"] = icon_path or target
    ps = """
$t = $env:LYTE_TARGET
$p = $env:LYTE_LNK
$i = $env:LYTE_ICON
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($p)
$s.TargetPath = $t
$s.WorkingDirectory = (Split-Path $t -Parent)
$s.IconLocation = $i
$s.Save()
"""
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps],
        env=env,
        check=True,
        capture_output=True,
    )


def install(
    install_dir: str,
    lyte_url: str,
    install_vlc: bool,
    add_start_menu: bool,
    add_desktop: bool,
    uninstaller_path: str,
    install_icon_path: str | None,
    progress_callback: Callable[[str, int, int], None] | None = None,
    log_callback: Callable[[str], None] | None = None,
) -> None:
    """
    Perform full installation.
    progress_callback: (message, current_step, total_steps) for UI updates.
    log_callback: (log_line) for installation log feed.
    """
    def log(msg: str):
        if log_callback:
            log_callback(msg)

    def step(msg: str, cur: int, tot: int = 4):
        log(msg)
        if progress_callback:
            progress_callback(msg, cur, tot)

    log("Preparing installation...")
    os.makedirs(install_dir, exist_ok=True)
    log(f"Install directory: {install_dir}")

    # 1. Download LYTE.exe
    step("Downloading LYTE.exe from GitHub...", 1, 4)
    lyte_exe = os.path.join(install_dir, "LYTE.exe")

    last_log_pct = [0]  # Use list to allow mutation in closure

    def lyte_progress(w: int, t: int):
        if progress_callback and t:
            pct = int(100 * w / t)
            progress_callback(f"Downloading LYTE... {pct}%", 1, 4)
        if log_callback and t:
            pct = int(100 * w / t)
            for milestone in (25, 50, 75, 100):
                if pct >= milestone > last_log_pct[0]:
                    log_callback(f"  Download progress: {milestone}%")
                    last_log_pct[0] = milestone
                    break

    download_file(lyte_url, lyte_exe, lyte_progress)
    log("LYTE.exe download complete.")

    # 2. Optional VLC
    if install_vlc:
        step("Downloading VLC Media Player installer...", 2, 4)
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as tmp:
            vlc_tmp = tmp.name
        try:
            download_file(VLC_URL, vlc_tmp)
            log("VLC installer downloaded.")
            step("Installing VLC Media Player...", 2, 4)
            subprocess.run([vlc_tmp, "/S"], check=False, capture_output=True)
            log("VLC installation complete.")
        finally:
            if os.path.isfile(vlc_tmp):
                os.unlink(vlc_tmp)
    else:
        log("Skipping VLC (not selected).")

    # 3. Copy uninstaller
    step("Copying uninstaller...", 3, 4)
    uninstall_dest = os.path.join(install_dir, "Uninstall LYTE.exe")
    shutil.copy2(uninstaller_path, uninstall_dest)
    log("Uninstall LYTE.exe installed.")

    # 4. Shortcuts
    step("Creating shortcuts...", 4, 4)
    icon_arg = install_icon_path if install_icon_path else lyte_exe

    if add_start_menu:
        start_menu = os.path.join(
            os.environ.get("ProgramData", "C:\\ProgramData"),
            "Microsoft", "Windows", "Start Menu", "Programs", "LYTE"
        )
        os.makedirs(start_menu, exist_ok=True)
        log("Creating Start Menu shortcut...")
        create_shortcut(
            lyte_exe,
            os.path.join(start_menu, "LYTE.lnk"),
            icon_arg,
        )
        create_shortcut(
            uninstall_dest,
            os.path.join(start_menu, "Uninstall LYTE.lnk"),
            None,
        )
        log("Start Menu shortcuts created.")

    if add_desktop:
        desktop = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
        if os.path.isdir(desktop):
            log("Creating Desktop shortcut...")
            create_shortcut(
                lyte_exe,
                os.path.join(desktop, "LYTE.lnk"),
                icon_arg,
            )
            log("Desktop shortcut created.")

    # 5. Registry
    log("Writing registry entries...")
    try:
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, REG_UNINSTALL)
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "LYTE")
        winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstall_dest}"')
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0")
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "StroepWafel")
        winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)

        key2 = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, REG_LYTE)
        winreg.SetValueEx(key2, "Install_Dir", 0, winreg.REG_SZ, install_dir)
        winreg.CloseKey(key2)
        log("Registry entries created.")
    except OSError:
        log("Warning: Could not write registry (may need admin).")

    log("Installation complete.")
