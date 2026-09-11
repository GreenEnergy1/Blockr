# Blockr

Blockr is a cross-platform desktop utility for managing a local website blocklist through the system `hosts` file. Blocked domains are redirected to `127.0.0.1` and tagged with the `#BLOCKR` marker so they can be listed or removed later.

Works on **Windows, macOS, and Linux**.

## Features

- Add one or more domains using commas or new lines
- Remove the selected domain from the Blockr entries
- Restore the built-in default blocklist
- Refresh the list from the current `hosts` file
- Flushes the OS DNS cache after a change so it takes effect immediately
- Requests elevated privileges natively per OS (UAC on Windows, an admin-password dialog on macOS, a PolicyKit prompt on Linux)
- Packaged as `.exe` (Windows), `.dmg` (macOS), and `.deb`/`.rpm` (Linux) — see [PACKAGING.md](PACKAGING.md)

## Requirements

- Python 3.10 or newer
- PyQt6
- Administrator / root privileges (the app requests these itself on launch)

The application requests elevated privileges because it reads and updates the OS hosts file:

| OS      | Path                                      |
|---------|--------------------------------------------|
| Windows | `C:\Windows\System32\drivers\etc\hosts`    |
| macOS / Linux | `/etc/hosts`                        |

On Linux, the elevation prompt is handled by `pkexec` (PolicyKit), which ships with virtually every desktop distro already. On macOS it's a native AppleScript admin-password dialog — no separate install needed.

## Run From Source

**Windows**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install PyQt6
python blockr.py
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install PyQt6
python3 blockr.py
```

The app will prompt you for elevated privileges on launch, however your OS normally does that.

## Build The Installers

See [PACKAGING.md](PACKAGING.md) for full instructions on producing `blockr.exe`, `Blockr.dmg`, `blockr.deb`, and `blockr.rpm`. Quick version:

```bash
# Windows
pyinstaller packaging/windows/blockr-win.spec        # -> dist/blockr.exe

# macOS
pyinstaller packaging/mac/blockr-mac.spec             # -> dist/Blockr.app
./packaging/mac/build-dmg.sh 1.0.0                     # -> dist/Blockr-1.0.0.dmg

# Linux
pyinstaller packaging/linux/blockr-linux.spec          # -> dist/blockr
./packaging/linux/build-deb.sh 1.0.0                    # -> dist/blockr_1.0.0_amd64.deb
./packaging/linux/build-rpm.sh 1.0.0                    # -> dist/blockr-1.0.0-1.x86_64.rpm
```

Each of these has to be built on its own OS — PyInstaller doesn't cross-compile.

## Usage

1. Enter a domain, or paste multiple domains separated by commas or new lines.
2. Select **Add Sites**.
3. Select a listed domain and choose **Remove Selected** to unblock it.
4. Choose **Restore Default Blocklist** to add the built-in defaults.
5. Choose **Refresh** to reload entries from the `hosts` file.

Input may include `http://`, `https://`, `www.`, or a path; these are removed during normalization.

## Notes

- Changes affect the whole computer and may require restarting a browser before they're visible; Blockr flushes the OS DNS cache automatically after each change to minimize this.
- Only lines containing the `#BLOCKR` marker are managed by this application.
- Back up the `hosts` file before making changes if it contains important custom entries.
