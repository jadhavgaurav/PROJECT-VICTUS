"""
Cross-platform system-level tools for file operations, app control, and automation
Supports: Windows, macOS, Linux, and mobile-friendly alternatives
"""

import os
import subprocess
import platform
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
import pyperclip  # type: ignore

# Refactor: Use SafeTool and local schemas
from .base import SafeTool, RiskLevel
from .schemas.system_schemas import (
    ListFilesSchema, OpenAppSchema, GetClipboardContentSchema,
    TakeScreenshotSchema, TypeTextSchema, GetActiveWindowTitleSchema,
    GetSystemInfoSchema
)
from .config import resolve_path, HOME_DIR

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"
IS_MOBILE = False  # Can be detected via user agent in API layer

# Conditional imports
if IS_WINDOWS:
    import winreg  # type: ignore

try:
    import pyautogui  # type: ignore
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

try:
    import pygetwindow as gw  # type: ignore
    HAS_PYGETWINDOW = True
except ImportError:
    HAS_PYGETWINDOW = False

# --- Core Function Implementations (No Decorators) ---

def _list_files(directory: str) -> str:
    path = resolve_path(directory)
    if not path.is_dir():
        return f"Error: Directory '{path}' not found. Please ensure the shortcut or path is correct."
    try:
        files = [f.name for f in path.iterdir()]
        return "\n".join(files) if files else "The directory is empty."
    except Exception as e:
        return f"Error listing files: {e}"

def _open_app(application_name: str) -> str:
    app_name_lower = application_name.lower().strip()
    
    # Cross-platform app aliases
    aliases = {
        # Code Editors
        "vs code": "code", "visual studio code": "code",
        "sublime": "subl", "sublime text": "subl",
        "atom": "atom",
        "vim": "vim", "vi": "vi",
        "nano": "nano",
        
        # Browsers
        "chrome": "google-chrome" if IS_LINUX else "Google Chrome" if IS_MACOS else "chrome.exe",
        "google chrome": "google-chrome" if IS_LINUX else "Google Chrome" if IS_MACOS else "chrome.exe",
        "firefox": "firefox",
        "safari": "Safari" if IS_MACOS else None,
        "edge": "microsoft-edge" if IS_LINUX else "Microsoft Edge" if IS_MACOS else "msedge.exe",
        "brave": "brave-browser" if IS_LINUX else "Brave Browser" if IS_MACOS else "brave.exe",
        
        # Office
        "word": "Microsoft Word" if IS_MACOS else "WINWORD.EXE" if IS_WINDOWS else None,
        "excel": "Microsoft Excel" if IS_MACOS else "EXCEL.EXE" if IS_WINDOWS else None,
        "powerpoint": "Microsoft PowerPoint" if IS_MACOS else "POWERPNT.EXE" if IS_WINDOWS else None,
        "pages": "Pages" if IS_MACOS else None,
        "numbers": "Numbers" if IS_MACOS else None,
        "keynote": "Keynote" if IS_MACOS else None,
        
        # System Apps
        "calculator": "Calculator" if IS_MACOS else "gnome-calculator" if IS_LINUX else "calc.exe",
        "notepad": "TextEdit" if IS_MACOS else "gedit" if IS_LINUX else "notepad.exe",
        "terminal": "Terminal" if IS_MACOS else "gnome-terminal" if IS_LINUX else "cmd.exe",
        "finder": "Finder" if IS_MACOS else None,
        "explorer": "Explorer.exe" if IS_WINDOWS else "nautilus" if IS_LINUX else "Finder" if IS_MACOS else None,
        
        # Media
        "spotify": "Spotify",
        "music": "Music" if IS_MACOS else "rhythmbox" if IS_LINUX else None,
        "photos": "Photos" if IS_MACOS else "shotwell" if IS_LINUX else None,
        "itunes": "Music" if IS_MACOS else None,
        
        # Communication
        "whatsapp": "WhatsApp",
        "messages": "Messages" if IS_MACOS else None,
        "slack": "Slack",
        "discord": "Discord",
        "teams": "Microsoft Teams",
        "zoom": "zoom.us" if IS_MACOS else "zoom",
        
        # Development
        "xcode": "Xcode" if IS_MACOS else None,
        "android studio": "studio" if IS_LINUX else "Android Studio" if IS_MACOS else "studio64.exe",
        "docker": "Docker",
    }
    
    executable_name = aliases.get(app_name_lower, application_name)
    
    if executable_name is None:
        return f"Application '{application_name}' is not available on {platform.system()}."
    
    # macOS: Use 'open' command
    if IS_MACOS:
        try:
            # Try with .app extension first
            app_paths = [
                f"/Applications/{executable_name}.app",
                f"/Applications/{executable_name}",
                f"{HOME_DIR}/Applications/{executable_name}.app",
            ]
            
            for app_path in app_paths:
                if os.path.exists(app_path):
                    subprocess.Popen(["open", app_path])
                    return f"Successfully opened {application_name}."
            
            # Try with 'open -a' command (works for installed apps)
            try:
                subprocess.Popen(["open", "-a", executable_name])
                return f"Successfully opened {application_name}."
            except:
                pass
            
            # Try mdfind (Spotlight search) for apps
            try:
                result = subprocess.run(
                    ["mdfind", f"kMDItemKind == 'Application' && kMDItemDisplayName == '{executable_name}'"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0 and result.stdout.strip():
                    app_path = result.stdout.strip().split('\n')[0]
                    subprocess.Popen(["open", app_path])
                    return f"Successfully opened {application_name}."
            except:
                pass
            
            # Fallback: try direct command
            subprocess.Popen(["open", "-a", executable_name])
            return f"Attempted to open {application_name}. If it didn't open, it may not be installed."
            
        except Exception as e:
            return f"Failed to open {application_name} on macOS: {e}"
    
    # Linux: Use desktop files and common commands
    elif IS_LINUX:
        try:
            # Try desktop file first
            desktop_paths = [
                f"{HOME_DIR}/.local/share/applications/{executable_name}.desktop",
                f"/usr/share/applications/{executable_name}.desktop",
            ]
            
            for desktop_path in desktop_paths:
                if os.path.exists(desktop_path):
                    subprocess.Popen(["gtk-launch", f"{executable_name}.desktop"])
                    return f"Successfully opened {executable_name}."
            
            # Try which command to find in PATH
            which_result = shutil.which(executable_name)
            if which_result:
                subprocess.Popen([which_result])
                return f"Successfully opened {application_name}."
            
            # Try xdg-open as fallback
            subprocess.Popen(["xdg-open", executable_name])
            return f"Attempted to open {application_name}. If it didn't open, it may not be installed."
            
        except Exception as e:
            return f"Failed to open {application_name} on Linux: {e}"
    
    # Windows: Original Windows logic
    elif IS_WINDOWS:
        # Microsoft Store App Launch
        store_apps = {
            "whatsapp": "5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
            "spotify": "SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify",
        }
        if app_name_lower in store_apps:
            try:
                command = f'explorer.exe shell:appsfolder\\{store_apps[app_name_lower]}'
                subprocess.Popen(command, shell=True)
                return f"Successfully launched the {application_name} app."
            except Exception as e:
                return f"Failed to launch the {application_name} app: {e}"

        # Traditional App Search (Registry, File System, PATH)
        executable_name = aliases.get(app_name_lower, f"{application_name}.exe")

        try:
            key_path = fr"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{executable_name}"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                executable_path, _ = winreg.QueryValue(key, None)
                subprocess.Popen(executable_path)
                return f"Successfully opened {application_name} via Registry."
        except FileNotFoundError:
            pass
        except Exception as e:
            return f"Found {application_name} in Registry but failed to open: {e}"
        
        search_paths = [
            Path(os.environ.get("ProgramFiles", "C:/Program Files")),
            Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")),
            HOME_DIR / "AppData" / "Local" / "Programs",
            HOME_DIR / "AppData" / "Local",
        ]
        for path in search_paths:
            if not path.exists():
                continue
            for root, _, files in os.walk(path):
                if executable_name.lower() in [f.lower() for f in files]:
                    try:
                        subprocess.Popen(str(Path(root) / executable_name))
                        return f"Successfully found and opened {application_name}."
                    except Exception as e:
                        return f"Found {application_name} but failed to launch: {e}"
        
        try:
            subprocess.Popen(executable_name, shell=True)
            return f"Successfully launched {application_name} from system PATH."
        except Exception:
            return f"Error: Could not find the application '{application_name}' after a thorough search."
    
    else:
        return f"Platform {platform.system()} is not supported for opening applications."

def _get_clipboard_content() -> str:
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Could not get clipboard content: {e}"

def _take_screenshot(path: str = "desktop") -> str:
    if not HAS_PYAUTOGUI:
        # Fallback to platform-specific commands
        if IS_MACOS:
            try:
                save_path = resolve_path(path)
                if save_path.is_dir():
                    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    save_file = save_path / filename
                else:
                    save_file = save_path
                
                subprocess.run(["screencapture", str(save_file)], check=True)
                return f"Screenshot saved successfully to {save_file}"
            except Exception as e:
                return f"Failed to take screenshot on macOS: {e}"
        elif IS_LINUX:
            try:
                save_path = resolve_path(path)
                if save_path.is_dir():
                    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    save_file = save_path / filename
                else:
                    save_file = save_path
                
                # Try different screenshot tools
                for cmd in ["gnome-screenshot", "scrot", "maim"]:
                    if shutil.which(cmd):
                        if cmd == "gnome-screenshot":
                            subprocess.run([cmd, "-f", str(save_file)], check=True)
                        elif cmd == "scrot":
                            subprocess.run([cmd, str(save_file)], check=True)
                        elif cmd == "maim":
                            subprocess.run([cmd, str(save_file)], check=True)
                        return f"Screenshot saved successfully to {save_file}"
                
                return "No screenshot tool found. Install gnome-screenshot, scrot, or maim."
            except Exception as e:
                return f"Failed to take screenshot on Linux: {e}"
        else:
            return "Screenshot functionality requires pyautogui or platform-specific tools."
    
    try:
        save_path = resolve_path(path)
        if save_path.is_dir():
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            save_file = save_path / filename
        else:
            save_file = save_path

        pyautogui.screenshot(str(save_file))
        return f"Screenshot saved successfully to {save_file}"
    except Exception as e:
        return f"Failed to take screenshot: {e}"

def _type_text(text: str) -> str:
    if not HAS_PYAUTOGUI:
        return "Text typing requires pyautogui library. Install it with: pip install pyautogui"
    
    try:
        pyautogui.write(text, interval=0.05)
        return "Text typed successfully."
    except Exception as e:
        return f"Failed to type text: {e}"

def _get_active_window_title() -> str:
    if IS_MACOS:
        try:
            # Use AppleScript on macOS
            script = 'tell application "System Events" to get name of first process whose frontmost is true'
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return f"The active window is: '{result.stdout.strip()}'"
            else:
                return "No active window found."
        except Exception as e:
            return f"Failed to get active window title on macOS: {e}"
    
    elif IS_LINUX:
        try:
            # Try xdotool first
            if shutil.which("xdotool"):
                result = subprocess.run(
                    ["xdotool", "getactivewindow", "getwindowname"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    return f"The active window is: '{result.stdout.strip()}'"
            
            # Fallback: try wmctrl
            if shutil.which("wmctrl"):
                result = subprocess.run(
                    ["wmctrl", "-a", ":ACTIVE:"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    return "Active window detected (title unavailable with wmctrl)."
            
            return "No window manager tool found. Install xdotool or wmctrl."
        except Exception as e:
            return f"Failed to get active window title on Linux: {e}"
    
    elif IS_WINDOWS and HAS_PYGETWINDOW:
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                return f"The active window is: '{active_window.title}'"
            else:
                return "No active window found."
        except Exception as e:
            return f"Failed to get active window title: {e}"

    else:
        return f"Active window detection not available on {platform.system()}."

def _get_system_info() -> str:
    info = {
        "Platform": platform.system(),
        "Platform Release": platform.release(),
        "Platform Version": platform.version(),
        "Architecture": platform.machine(),
        "Processor": platform.processor(),
        "Python Version": platform.python_version(),
    }
    
    return "\n".join([f"{k}: {v}" for k, v in info.items()])

# --- Tool Construction ---

list_files = SafeTool.from_func(
    func=_list_files,
    name="list_files",
    description="Lists files and directories in a specified location.",
    args_schema=ListFilesSchema,
    risk_level=RiskLevel.LOW
)

open_app = SafeTool.from_func(
    func=_open_app,
    name="open_app",
    description="Intelligently finds and opens an application.",
    args_schema=OpenAppSchema,
    risk_level=RiskLevel.MEDIUM
)

get_clipboard_content = SafeTool.from_func(
    func=_get_clipboard_content,
    name="get_clipboard_content",
    description="Reads and returns the current content of the system clipboard.",
    args_schema=GetClipboardContentSchema,
    risk_level=RiskLevel.LOW
)

take_screenshot = SafeTool.from_func(
    func=_take_screenshot,
    name="take_screenshot",
    description="Takes a screenshot of the entire screen.",
    args_schema=TakeScreenshotSchema,
    risk_level=RiskLevel.MEDIUM
)

type_text = SafeTool.from_func(
    func=_type_text,
    name="type_text",
    description="Types the given text using the keyboard.",
    args_schema=TypeTextSchema,
    risk_level=RiskLevel.MEDIUM
)

get_active_window_title = SafeTool.from_func(
    func=_get_active_window_title,
    name="get_active_window_title",
    description="Gets the title of the currently active window.",
    args_schema=GetActiveWindowTitleSchema,
    risk_level=RiskLevel.LOW
)

get_system_info = SafeTool.from_func(
    func=_get_system_info,
    name="get_system_info",
    description="Returns information about the current system.",
    args_schema=GetSystemInfoSchema,
    risk_level=RiskLevel.LOW
)
