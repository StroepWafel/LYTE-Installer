# -*- coding: utf-8 -*-
"""
Fetch LYTE release versions from GitHub API.
"""

import requests

RELEASES_URL = "https://api.github.com/repos/StroepWafel/LYTE/releases"
LYTE_EXE_ASSET = "LYTE.exe"


def fetch_releases() -> list[dict]:
    """
    Fetch ALL releases from GitHub API (paginated).
    Returns list of release dicts with tag_name, assets, etc.
    """
    all_releases: list[dict] = []
    page = 1
    per_page = 100
    while True:
        resp = requests.get(RELEASES_URL, params={"per_page": per_page, "page": page}, timeout=15)
        resp.raise_for_status()
        releases = resp.json()
        if not releases:
            break
        all_releases.extend(releases)
        if len(releases) < per_page:
            break
        page += 1
    return all_releases


def get_versions_with_lyte_exe() -> list[tuple[str, str]]:
    """
    Get list of (display_name, tag_or_latest) for releases that have LYTE.exe.
    First non-prerelease is marked as "latest (recommended)".
    Returns: [(display_name, tag), ...] e.g. [("latest (recommended)", "latest"), ("1.11.0-Release", "1.11.0-Release"), ...]
    """
    releases = fetch_releases()
    result: list[tuple[str, str]] = []
    latest_added = False

    for r in releases:
        tag = r.get("tag_name", "")
        prerelease = r.get("prerelease", False)
        assets = r.get("assets", [])

        has_lyte = any(a.get("name") == LYTE_EXE_ASSET for a in assets)
        if not has_lyte:
            continue

        if not latest_added and not prerelease:
            result.append(("latest (recommended)", "latest"))
            latest_added = True

        result.append((tag, tag))

    return result


def get_download_url(version: str) -> str:
    """
    Get download URL for LYTE.exe.
    version: "latest" or a tag like "1.11.0-Release"
    """
    if version == "latest":
        return "https://github.com/StroepWafel/LYTE/releases/latest/download/LYTE.exe"
    return f"https://github.com/StroepWafel/LYTE/releases/download/{version}/LYTE.exe"
