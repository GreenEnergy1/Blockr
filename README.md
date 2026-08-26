# Blockr

Blockr is a Windows desktop utility for managing a local website blocklist through the system `hosts` file. Blocked domains are redirected to `127.0.0.1` and tagged with the `#BLOCKR` marker so they can be listed or removed later.

## Features

- Add one or more domains using commas or new lines
- Remove the selected domain from the Blockr entries
- Restore the built-in default blocklist
- Refresh the list from the current `hosts` file
- Package as a windowed Windows executable with PyInstaller

## Requirements

- Windows
- Python 3.10 or newer
- PyQt6
- Administrator privileges

The application requests administrator privileges because it reads and updates:

```text
C:\Windows\System32\drivers\etc\hosts
```

## Run From Source

Create and activate a virtual environment, then install the dependency:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install PyQt6
```

Start the application:

```powershell
python blockr.py
```

Windows will display an elevation prompt when administrator access is needed.

## Build The Executable

Install PyInstaller if it is not already available:

```powershell
python -m pip install pyinstaller
```

Build using the included spec file:

```powershell
pyinstaller blockr.spec
```

The resulting executable is written to `dist\blockr.exe`.

## Usage

1. Enter a domain, or paste multiple domains separated by commas or new lines.
2. Select **Add Sites**.
3. Select a listed domain and choose **Remove Selected** to unblock it.
4. Choose **Restore Default Blocklist** to add the built-in defaults.
5. Choose **Refresh** to reload entries from the `hosts` file.

Input may include `http://`, `https://`, `www.`, or a path; these are removed during normalization.

## Notes

- Changes affect the whole computer and may require restarting a browser or flushing the DNS cache before they are visible.
- Only lines containing the `#BLOCKR` marker are managed by this application.
- Back up the `hosts` file before making changes if it contains important custom entries.
