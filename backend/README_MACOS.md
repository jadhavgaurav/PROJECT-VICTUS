# Project VICTUS - MacOS Setup Guide

This guide covers specific configuration and troubleshooting steps for running Project VICTUS on macOS.

## Prerequisites

- **Python 3.11+**: Ensure you have Python 3.11 installed. We recommend using `conda` or `brew`.
- **Node.js**: Required for the frontend.
- **Poetry**: For backend dependency management.

## Installation

1.  **Backend Setup**:

    ```bash
    cd backend
    # Install dependencies (Windows-specific packages have been removed)
    poetry install
    ```

2.  **Frontend Setup**:
    ```bash
    cd frontend
    npm install
    ```

## System Permissions

Project VICTUS uses `pyautogui` for some automation tasks (like typing) and system commands for screenshots. macOS requires explicit permissions for these actions.

### Granting Accessibility Access

1.  Open **System Settings** > **Privacy & Security** > **Accessibility**.
2.  Click the `+` button.
3.  Add your **Terminal** application (e.g., Terminal, iTerm2) or your **IDE** (e.g., VS Code) if you are running the app from there.
4.  Toggle the switch to **ON**.

### Granting Screen Recording Access

1.  Open **System Settings** > **Privacy & Security** > **Screen Recording**.
2.  Add your Terminal or IDE.
3.  This is required for the `take_screenshot` tool to work.

## Troubleshooting

### "Example error: OMP: Error #15: Initializing libiomp5.dylib, but found libomp.dylib already initialized."

This is a common issue on macOS with PyTorch packages.
We have automatically handled this in `src/main.py` by setting:

```python
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
```

If you still see this error, ensure you are running the application through `src/main.py`.

### "ModuleNotFoundError: No module named 'pygetwindow'"

This module is Windows-specific and should not be used on macOS. It has been removed from `pyproject.toml`. If you see this error, ensure you have updated your dependencies:

```bash
poetry install --sync
```

### "xcrun: error: invalid active developer path"

If you see this error when installing dependencies, you may need to update Xcode command line tools:

```bash
xcode-select --install
```
