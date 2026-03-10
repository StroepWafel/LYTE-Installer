# LYTE Installer

A Python-based installer for [LYTE](https://github.com/StroepWafel/LYTE) with a dark theme UI matching the main application.

### Proudly powered by [OSSIGN](https://ossign.org/)
[![OSSign Banner](https://github.com/OSSign/.github/raw/main/svg/badge-white-wide-links.svg)](https://github.com/OSSign/)

## Features

- **Auto-fetched versions** — Release list is fetched from GitHub; no manual updates needed
- **LYTE-matching dark UI** — PySide6 interface with the same colors and styling as LYTE
- **Standalone EXE** — Single `LYTE_Installer.exe`; no Python or other runtime required
- **Optional VLC** — Install VLC Media Player for playback support
- **Custom branding** — Swap images in `branding/` to rebrand

## Build

1. Install Python 3.11+ and dependencies:
   ```bash
   pip install -r requirements.txt pyinstaller
   ```

2. Build uninstaller, then installer:
   ```bash
   pyinstaller uninstaller.spec
   pyinstaller installer.spec
   ```

3. Output: `dist/LYTE_Installer.exe`

## Branding

Place your images in `branding/`:

| File | Purpose |
|------|---------|
| `branding/ico/install.ico` | Installer window/taskbar icon |
| `branding/ico/uninstall.ico` | Uninstaller window icon |
| `branding/headerimage.bmp` or `header.png` | Banner at top of wizard pages |
| `branding/wizard.bmp` or `sidebar.png` | Welcome/Finish sidebar (164×314 px) |

## Run from source

```bash
pip install -r requirements.txt
python -m src.main
```

**Note:** Running from source requires the uninstaller to be built first and placed at `dist/Uninstall LYTE.exe` for the install step to work.

## Where are the signed files published?

The signed files are published in the [Releases](https://github.com/StroepWafel/LYTE-Installer/releases) tab under the `latest` tag.

You can find the latest workflow runs in the [Actions tab](https://github.com/StroepWafel/LYTE-Installer/actions).
