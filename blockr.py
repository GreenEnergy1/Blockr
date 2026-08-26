import os
import sys
import ctypes


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()
    
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QLineEdit, QListWidget, QLabel
)

from PyQt6.QtCore import Qt


HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "127.0.0.1"
MARKER = "#BLOCKR"


# ---------------- SEED BLOCKLIST ----------------
DEFAULT_BLOCKS = [
    "pornhub.com","xvideos.com", "xnxx.com", "redtube.com", "youporn.com", "brazzers.com", "spankbang.com", "txxx.com", "hclips.com", "beeg.com", "xhamster.com", "slutload.com", "porndig.com", "motherless.com", "sex.com", "faketaxi.com", "erome.com", "xkeezmovies.com", "nuvid.com", "yespornplease.com", "xtube.com", "3movs.com", "sextvx.com", "porn.com", "drtuber.com", "empflix.com", "hdzog.com", "keeplinks.org", "lubetube.com", "mylust.com", "shooshtime.com",
    "xvideos.com",
    "xnxx.com"
]


# ---------------- ADMIN ----------------
def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


# ---------------- READ ----------------
def get_blocked_sites():
    sites = set()

    try:
        with open(HOSTS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if MARKER in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        sites.add(parts[1])
    except Exception:
        pass

    return sorted(list(sites))


# ---------------- WRITE ----------------
def add_site(site):
    site = clean_site(site)
    if not site:
        return

    with open(HOSTS_PATH, "a", encoding="utf-8") as f:
        f.write(f"{REDIRECT_IP} {site} {MARKER}\n")
        f.write(f"{REDIRECT_IP} www.{site} {MARKER}\n")


def remove_site(site):
    site = site.strip().lower()

    try:
        with open(HOSTS_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

        with open(HOSTS_PATH, "w", encoding="utf-8") as f:
            for line in lines:
                if MARKER in line and site in line:
                    continue
                f.write(line)

    except Exception as e:
        print(e)


# ---------------- CLEANER ----------------
def clean_site(raw):
    if not raw:
        return None

    site = raw.strip().lower()

    # batch safety (just in case single call)
    site = site.replace("https://", "")
    site = site.replace("http://", "")
    site = site.replace("www.", "")

    if "/" in site:
        site = site.split("/")[0]

    return site


def batch_add(raw):
    if not raw:
        return

    # normalize batch input
    raw = raw.replace(",", "\n")
    parts = raw.split("\n")

    for p in parts:
        site = clean_site(p)
        if site:
            add_site(site)


# ---------------- UI ----------------
class Blockr(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Blockr")
        self.setFixedSize(440, 600)

        self.setStyleSheet("""
            QWidget {
                background-color: #0b0f14;
                color: #e5e7eb;
                font-family: Arial;
                font-size: 13px;
            }

            QPushButton {
                background-color: #22c55e;
                color: black;
                padding: 10px;
                border-radius: 10px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #16a34a;
            }

            QLineEdit {
                padding: 10px;
                border-radius: 10px;
                background-color: #121a24;
                color: white;
                border: 1px solid #1f2937;
            }

            QListWidget {
                background-color: #121a24;
                border-radius: 10px;
                padding: 5px;
            }
        """)

        layout = QVBoxLayout()

        # TITLE
        title = QLabel("Blockr")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # STATUS (simple but clean)
        self.status = QLabel("System Control Panel")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("opacity: 0.7;")
        layout.addWidget(self.status)

        # INPUT (batch enabled)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Paste sites (comma or new lines)")
        layout.addWidget(self.input)

        add_btn = QPushButton("Add Sites")
        add_btn.clicked.connect(self.add_sites)
        layout.addWidget(add_btn)

        # LIST
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove)
        layout.addWidget(remove_btn)

        seed_btn = QPushButton("Restore Default Blocklist")
        seed_btn.clicked.connect(self.seed_defaults)
        layout.addWidget(seed_btn)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(refresh_btn)

        self.setLayout(layout)

        self.refresh()

    # ---------------- CORE ----------------
    def refresh(self):
        self.list_widget.clear()
        for site in get_blocked_sites():
            self.list_widget.addItem(site)

    def add_sites(self):
        raw = self.input.text()
        batch_add(raw)
        self.input.clear()
        self.refresh()

    def remove(self):
        item = self.list_widget.currentItem()
        if item:
            remove_site(item.text())
            self.refresh()

    def seed_defaults(self):
        for site in DEFAULT_BLOCKS:
            add_site(site)
        self.refresh()


# ---------------- RUN ----------------
if __name__ == "__main__":
    if not is_admin():
        print("Run as Administrator")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = Blockr()
    window.show()
    sys.exit(app.exec())
