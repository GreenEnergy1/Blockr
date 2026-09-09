"""
Blockr — a small Windows utility that blocks websites system-wide by
redirecting them to 127.0.0.1 in the hosts file.

Only lines tagged with MARKER are ever touched, so anything else already
in the hosts file is left alone.
"""

import os
import sys
import ctypes


# ---------------- ADMIN ELEVATION ----------------
# This has to happen before anything else — including the PyQt6 import —
# because we want to relaunch elevated and exit, not open a window first.

def is_admin() -> bool:
    """True if the current process already has administrator rights."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def relaunch_as_admin() -> None:
    """Re-launch this same process with a UAC elevation prompt."""
    params = " ".join(f'"{arg}"' for arg in sys.argv)
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )


if __name__ == "__main__" and not is_admin():
    relaunch_as_admin()
    sys.exit()


from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QListWidget,
    QLabel,
    QMessageBox,
    QFrame,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt


HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "127.0.0.1"
MARKER = "#BLOCKR"

# Seed list used by "Restore Default Blocklist". Deduplicated on load, so
# it's safe to add to this without worrying about repeats.
DEFAULT_BLOCKS = sorted(set([
    "pornhub.com", "xvideos.com", "xnxx.com", "redtube.com", "youporn.com",
    "brazzers.com", "spankbang.com", "txxx.com", "hclips.com", "beeg.com",
    "xhamster.com", "slutload.com", "porndig.com", "motherless.com",
    "sex.com", "faketaxi.com", "erome.com", "xkeezmovies.com", "nuvid.com",
    "yespornplease.com", "xtube.com", "3movs.com", "sextvx.com", "porn.com",
    "drtuber.com", "empflix.com", "hdzog.com", "keeplinks.org",
    "lubetube.com", "mylust.com", "shooshtime.com",
]))


def resource_path(filename: str) -> str:
    """Resolve a bundled resource whether running from source or as a
    PyInstaller-frozen exe."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


# ---------------- HOSTS FILE I/O ----------------

def clean_site(raw: str) -> str | None:
    """Normalize user input down to a bare domain, e.g.
    'https://www.Example.com/path' -> 'example.com'."""
    if not raw:
        return None

    site = raw.strip().lower()
    site = site.replace("https://", "").replace("http://", "")
    site = site.replace("www.", "")
    site = site.split("/")[0]

    return site or None


def get_blocked_sites() -> list[str]:
    """Return the sorted set of bare domains currently managed by Blockr."""
    sites = set()
    try:
        with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if MARKER not in line:
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    host = parts[1].removeprefix("www.")
                    sites.add(host)
    except FileNotFoundError:
        pass

    return sorted(sites)


def add_site(site: str, already_blocked: set[str]) -> bool:
    """Append hosts entries for a domain. Returns False if it's already
    blocked (so callers can report skipped domains) rather than writing a
    duplicate line."""
    site = clean_site(site)
    if not site or site in already_blocked:
        return False

    with open(HOSTS_PATH, "a", encoding="utf-8") as f:
        f.write(f"{REDIRECT_IP} {site} {MARKER}\n")
        f.write(f"{REDIRECT_IP} www.{site} {MARKER}\n")

    already_blocked.add(site)
    return True


def remove_site(site: str) -> None:
    """Remove every Blockr-tagged line for an exact domain (and its www.
    variant) — never a substring match, so 'sex.com' can't accidentally
    also remove 'unisex.com'."""
    site = site.strip().lower()
    targets = {site, f"www.{site}"}

    with open(HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    with open(HOSTS_PATH, "w", encoding="utf-8") as f:
        for line in lines:
            parts = line.split()
            is_match = (
                MARKER in line and len(parts) >= 2 and parts[1] in targets
            )
            if not is_match:
                f.write(line)


def batch_add(raw: str) -> tuple[int, int]:
    """Add every domain in a comma/newline separated blob.
    Returns (added_count, skipped_count)."""
    if not raw:
        return 0, 0

    already_blocked = set(get_blocked_sites())
    parts = raw.replace(",", "\n").split("\n")

    added = skipped = 0
    for part in parts:
        site = clean_site(part)
        if not site:
            continue
        if add_site(site, already_blocked):
            added += 1
        else:
            skipped += 1

    return added, skipped


# ---------------- STYLE ----------------
# Palette matches the app icon and landing page: near-black background,
# a single green accent, everything else quiet.

STYLESHEET = """
QWidget {
    background-color: #0a0d10;
    color: #e7ebee;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

QLabel#title {
    font-size: 19px;
    font-weight: 600;
}

QLabel#subtitle, QLabel#count {
    color: #7c8791;
    font-size: 12px;
}

QLineEdit {
    background-color: #11161b;
    border: 1px solid #232b32;
    border-radius: 8px;
    padding: 10px 12px;
    color: #e7ebee;
    selection-background-color: #22c55e;
}
QLineEdit:focus {
    border: 1px solid #22c55e;
}

QListWidget {
    background-color: #11161b;
    border: 1px solid #232b32;
    border-radius: 8px;
    padding: 4px;
    font-family: Consolas, "Courier New", monospace;
    outline: none;
}
QListWidget::item {
    padding: 7px 8px;
    border-radius: 5px;
    color: #c4cad2;
}
QListWidget::item:selected {
    background-color: #14361f;
    color: #e7ebee;
}
QListWidget::item:hover:!selected {
    background-color: #161d24;
}

QPushButton {
    border-radius: 8px;
    padding: 10px;
    font-weight: 600;
}

QPushButton#primary {
    background-color: #22c55e;
    color: #06210f;
    border: none;
}
QPushButton#primary:hover {
    background-color: #3ad571;
}
QPushButton#primary:pressed {
    background-color: #1aa34d;
}

QPushButton#secondary {
    background-color: transparent;
    color: #e7ebee;
    border: 1px solid #232b32;
}
QPushButton#secondary:hover {
    border: 1px solid #4f5860;
}

QPushButton#ghost {
    background-color: transparent;
    color: #7c8791;
    border: 1px solid #232b32;
    font-weight: 500;
}
QPushButton#ghost:hover {
    color: #e7ebee;
    border: 1px solid #4f5860;
}

QFrame#divider {
    background-color: #1a2027;
    max-height: 1px;
    min-height: 1px;
}
"""


# ---------------- UI ----------------
class Blockr(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Blockr")
        self.resize(460, 660)
        self.setMinimumSize(400, 540)
        self.setStyleSheet(STYLESHEET)

        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        # Header
        title = QLabel("Blockr")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        self.subtitle = QLabel("System Control Panel")
        self.subtitle.setObjectName("subtitle")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.subtitle)

        root.addSpacing(8)

        # Input row
        self.input = QLineEdit()
        self.input.setPlaceholderText("Paste sites (comma or new lines)")
        self.input.returnPressed.connect(self.add_sites)
        root.addWidget(self.input)

        add_btn = QPushButton("Add Sites")
        add_btn.setObjectName("primary")
        add_btn.clicked.connect(self.add_sites)
        root.addWidget(add_btn)

        divider = QFrame()
        divider.setObjectName("divider")
        root.addWidget(divider)

        # List
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.remove)
        root.addWidget(self.list_widget, stretch=1)

        self.count_label = QLabel()
        self.count_label.setObjectName("count")
        root.addWidget(self.count_label)

        # Actions
        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.setObjectName("secondary")
        remove_btn.clicked.connect(self.remove)
        actions_row.addWidget(remove_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("secondary")
        refresh_btn.clicked.connect(self.refresh)
        actions_row.addWidget(refresh_btn)

        root.addLayout(actions_row)

        seed_btn = QPushButton("Restore Default Blocklist")
        seed_btn.setObjectName("ghost")
        seed_btn.clicked.connect(self.seed_defaults)
        root.addWidget(seed_btn)

        self.refresh()

    # ---------------- HELPERS ----------------
    def _report_error(self, err: Exception) -> None:
        if isinstance(err, PermissionError):
            QMessageBox.critical(
                self,
                "Permission denied",
                "Blockr couldn't write to the hosts file.\n\n"
                "Make sure it's running as Administrator, then try again.",
            )
        else:
            QMessageBox.critical(self, "Something went wrong", str(err))

    def _set_status(self, text: str) -> None:
        self.subtitle.setText(text)

    # ---------------- ACTIONS ----------------
    def refresh(self) -> None:
        try:
            sites = get_blocked_sites()
        except Exception as err:
            self._report_error(err)
            return

        self.list_widget.clear()
        self.list_widget.addItems(sites)
        n = len(sites)
        self.count_label.setText(f"{n} domain{'s' if n != 1 else ''} blocked")

    def add_sites(self) -> None:
        raw = self.input.text()
        if not raw.strip():
            return

        try:
            added, skipped = batch_add(raw)
        except Exception as err:
            self._report_error(err)
            return

        self.input.clear()
        self.refresh()

        if added and skipped:
            self._set_status(f"Added {added} · {skipped} already blocked")
        elif added:
            self._set_status(f"Added {added} domain{'s' if added != 1 else ''}")
        else:
            self._set_status("Already on the blocklist")

    def remove(self) -> None:
        item = self.list_widget.currentItem()
        if not item:
            return

        site = item.text()
        try:
            remove_site(site)
        except Exception as err:
            self._report_error(err)
            return

        self.refresh()
        self._set_status(f"Removed {site}")

    def seed_defaults(self) -> None:
        reply = QMessageBox.question(
            self,
            "Restore default blocklist",
            f"Add {len(DEFAULT_BLOCKS)} default domains to your blocklist?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            already_blocked = set(get_blocked_sites())
            added = sum(
                1 for site in DEFAULT_BLOCKS if add_site(site, already_blocked)
            )
        except Exception as err:
            self._report_error(err)
            return

        self.refresh()
        self._set_status(f"Restored defaults — added {added}")


# ---------------- RUN ----------------
if __name__ == "__main__":
    if not is_admin():
        print("Run as Administrator")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = Blockr()
    window.show()
    sys.exit(app.exec())
