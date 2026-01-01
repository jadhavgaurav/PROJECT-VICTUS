"""
Configuration and utilities for tools
"""

import os
import platform
import httpx
from pathlib import Path
from typing import Dict

HOME_DIR = Path.home()

# Shared async HTTP client for all tools
async_client = httpx.AsyncClient(timeout=10.0)

def get_windows_special_folder(folder_name: str) -> Path:
    """
    Finds the correct path for special folders (like Desktop) from the Windows Registry.
    This correctly handles OneDrive-managed folders.
    """
    if platform.system() == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            )
            path, _ = winreg.QueryValueEx(key, folder_name)
            return Path(path)
        except Exception:
            # Fallback if registry key is not found
            return HOME_DIR / folder_name
    elif platform.system() == "Darwin":  # macOS
        # macOS special folders
        special_folders = {
            "Desktop": HOME_DIR / "Desktop",
            "Documents": HOME_DIR / "Documents",
            "Downloads": HOME_DIR / "Downloads",
            "Pictures": HOME_DIR / "Pictures",
            "Videos": HOME_DIR / "Movies",
            "Music": HOME_DIR / "Music",
        }
        return special_folders.get(folder_name, HOME_DIR / folder_name)
    
    else:  # Linux and others
        # Linux special folders (XDG standard)
        xdg_dirs = {
            "Desktop": os.environ.get("XDG_DESKTOP_DIR", str(HOME_DIR / "Desktop")),
            "Documents": os.environ.get("XDG_DOCUMENTS_DIR", str(HOME_DIR / "Documents")),
            "Downloads": os.environ.get("XDG_DOWNLOAD_DIR", str(HOME_DIR / "Downloads")),
            "Pictures": os.environ.get("XDG_PICTURES_DIR", str(HOME_DIR / "Pictures")),
            "Videos": os.environ.get("XDG_VIDEOS_DIR", str(HOME_DIR / "Videos")),
            "Music": os.environ.get("XDG_MUSIC_DIR", str(HOME_DIR / "Music")),
        }
        if folder_name in xdg_dirs:
            return Path(xdg_dirs[folder_name])
        return HOME_DIR / folder_name

# Path shortcuts for easy access
PATH_SHORTCUTS: Dict[str, Path] = {
    "desktop": get_windows_special_folder("Desktop"),
    "documents": get_windows_special_folder("Documents"),
    "downloads": get_windows_special_folder("Downloads"),
    "pictures": get_windows_special_folder("Pictures"),
    "videos": get_windows_special_folder("Videos"),
    "home": HOME_DIR,
}

def resolve_path(path_str: str) -> Path:
    """Resolves common shortcuts into full file paths."""
    path_str = path_str.lower().strip()
    return PATH_SHORTCUTS.get(path_str, Path(path_str).expanduser().resolve())

