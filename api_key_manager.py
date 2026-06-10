"""
API Key Manager — Groq API key, secure storage and first-launch dialog.
Storage priority: GROQ_API_KEY env var → encrypted file → prompt user
"""

import base64
import hashlib
import logging
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

log = logging.getLogger(__name__)

KEY_DIR  = Path.home() / ".local/share/ai-datacenter-tracker"
KEY_FILE = KEY_DIR / "groq_key.enc"


def _secret() -> bytes:
    mid = ""
    p = Path("/etc/machine-id")
    if p.exists():
        mid = p.read_text().strip()
    return hashlib.sha256((mid + "ai-datacenter-tracker-groq").encode()).digest()


def _encrypt(text: str) -> bytes:
    data = text.encode()
    s = _secret()
    return base64.b64encode(b"XOR:" + bytes(b ^ s[i % 32] for i, b in enumerate(data)))


def _decrypt(blob: bytes) -> str:
    try:
        raw = base64.b64decode(blob)
        if raw.startswith(b"XOR:"):
            s = _secret()
            data = raw[4:]
            return bytes(b ^ s[i % 32] for i, b in enumerate(data)).decode()
    except Exception:
        pass
    return ""


def load_api_key() -> str:
    env = os.environ.get("GROQ_API_KEY", "").strip()
    if env:
        return env
    if KEY_FILE.exists():
        k = _decrypt(KEY_FILE.read_bytes())
        if k:
            return k
    return ""


def save_api_key(key: str):
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_bytes(_encrypt(key))
    KEY_FILE.chmod(0o600)
    log.info("Groq API key saved to encrypted file")


def delete_api_key():
    if KEY_FILE.exists():
        KEY_FILE.unlink()
    log.info("Groq API key deleted")


def apply_to_env(key: str):
    os.environ["GROQ_API_KEY"] = key


class _ValidateWorker(QThread):
    result = pyqtSignal(bool, str)

    def __init__(self, key: str):
        super().__init__()
        self._key = key

    def run(self):
        try:
            from groq import Groq
            Groq(api_key=self._key).chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1,
            )
            self.result.emit(True, "Groq API key validated successfully.")
        except Exception as e:
            msg = str(e).lower()
            if "auth" in msg or "invalid" in msg or "401" in msg or "403" in msg:
                self.result.emit(False, "Invalid API key — authentication failed.")
            else:
                self.result.emit(True, f"Network check skipped ({type(e).__name__}) — key saved.")


class ApiKeyDialog(QDialog):
    def __init__(self, parent=None, invalid: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Groq API Key — AI Data Center Tracker")
        self.setModal(True)
        self.setFixedWidth(520)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setStyleSheet("""
            QDialog  { background: #080c16; }
            QLabel   { color: #c0d8f0; font-family: monospace; }
            QLineEdit {
                background: rgba(15,25,50,0.90);
                border: 1px solid rgba(100,200,255,0.30);
                border-radius: 6px; color: #90c8e8;
                font-family: monospace; font-size: 12px; padding: 8px 12px;
            }
            QLineEdit:focus { border-color: rgba(100,200,255,0.70); }
            QPushButton {
                background: rgba(20,40,80,0.70);
                border: 1px solid rgba(100,200,255,0.30);
                border-radius: 5px; color: #80c0e0;
                font-family: monospace; font-size: 11px; padding: 7px 18px;
            }
            QPushButton:hover   { background: rgba(30,60,110,0.90); }
            QPushButton:disabled { opacity: 0.35; }
        """)
        self._worker  = None
        self._api_key = ""
        self._build(invalid)

    def _build(self, invalid: bool):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(14)

        # Header
        hl = QHBoxLayout()
        ico = QLabel("⬡")
        ico.setFont(QFont("Monospace", 26))
        ico.setStyleSheet("color: #64c8ff;")
        hl.addWidget(ico)
        col = QVBoxLayout()
        col.setSpacing(2)
        col.addWidget(_lbl("AI Data Center Tracker", 13, "#ffffff", bold=True))
        col.addWidget(_lbl("Groq API Key Setup", 10, "#4a7090"))
        hl.addLayout(col)
        hl.addStretch()
        root.addLayout(hl)

        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("background: rgba(100,200,255,0.12);")
        root.addWidget(div)

        if invalid:
            root.addWidget(_lbl(
                "⚠  The saved key is invalid. Please enter a new one.", 10, "#ffb400"))
        else:
            root.addWidget(_lbl(
                "The AI assistant requires a Groq API key.\n"
                "It is 100% free — no credit card needed.\n"
                "Your key is stored encrypted on this machine only.",
                10, "#607888"))

        root.addWidget(_lbl("Groq API Key:", 10, "#64c8ff"))

        row = QHBoxLayout()
        self._inp = QLineEdit()
        self._inp.setPlaceholderText("gsk_…")
        self._inp.setEchoMode(QLineEdit.EchoMode.Password)
        self._inp.textChanged.connect(
            lambda t: self._save_btn.setEnabled(len(t.strip()) > 10))
        self._inp.returnPressed.connect(self._on_save)
        row.addWidget(self._inp)

        eye = QPushButton("👁")
        eye.setFixedWidth(36)
        eye.setCheckable(True)
        eye.toggled.connect(lambda on: self._inp.setEchoMode(
            QLineEdit.EchoMode.Normal if on else QLineEdit.EchoMode.Password))
        row.addWidget(eye)
        root.addLayout(row)

        root.addWidget(_lbl(
            "Free key: console.groq.com → API Keys → Create API Key", 9, "#304858"))

        self._status = QLabel("")
        self._status.setFont(QFont("Monospace", 10))
        self._status.setWordWrap(True)
        self._status.setMinimumHeight(18)
        root.addWidget(self._status)

        br = QHBoxLayout()
        br.setSpacing(10)

        skip = QPushButton("Skip — Map Only")
        skip.setStyleSheet(
            "QPushButton { background: rgba(40,20,20,0.50);"
            " border: 1px solid rgba(100,60,60,0.40); border-radius: 5px;"
            " color: #806060; font-family: monospace; font-size: 11px; padding: 7px 18px; }"
            "QPushButton:hover { color: #a07070; }"
        )
        skip.clicked.connect(self.reject)

        self._save_btn = QPushButton("Validate & Save  ✓")
        self._save_btn.setEnabled(False)
        self._save_btn.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            " stop:0 rgba(0,80,160,0.80), stop:1 rgba(0,140,200,0.80));"
            " border: 1px solid rgba(0,180,255,0.50); border-radius: 5px;"
            " color: #ffffff; font-family: monospace; font-size: 11px;"
            " font-weight: bold; padding: 7px 18px; }"
            "QPushButton:hover { background: rgba(0,120,200,0.90); }"
            "QPushButton:disabled { opacity: 0.30; }"
        )
        self._save_btn.clicked.connect(self._on_save)

        br.addWidget(skip)
        br.addStretch()
        br.addWidget(self._save_btn)
        root.addLayout(br)

    def _on_save(self):
        key = self._inp.text().strip()
        if not key:
            return
        self._save_btn.setEnabled(False)
        self._inp.setEnabled(False)
        self._status.setText("⏳  Validating with Groq…")
        self._status.setStyleSheet("color: #ffb400;")
        self._worker = _ValidateWorker(key)
        self._worker.result.connect(lambda ok, msg: self._validated(ok, msg, key))
        self._worker.start()

    def _validated(self, ok: bool, msg: str, key: str):
        self._save_btn.setEnabled(True)
        self._inp.setEnabled(True)
        if ok:
            save_api_key(key)
            apply_to_env(key)
            self._api_key = key
            self._status.setText(f"✓  {msg}")
            self._status.setStyleSheet("color: #32ff96;")
            QTimer.singleShot(800, self.accept)
        else:
            self._status.setText(f"✗  {msg}")
            self._status.setStyleSheet("color: #ff4040;")

    def get_key(self) -> str:
        return self._api_key


def _lbl(text: str, size: int = 10, color: str = "#c0d8f0", bold: bool = False) -> QLabel:
    l = QLabel(text)
    l.setFont(QFont("Monospace", size))
    l.setWordWrap(True)
    l.setStyleSheet(f"color: {color}; {'font-weight: bold;' if bold else ''}")
    return l


def ensure_api_key(parent=None) -> str:
    """Load stored key or show first-launch dialog. Returns key (may be empty if skipped)."""
    key = load_api_key()
    if key:
        apply_to_env(key)
        log.info("Groq API key loaded from storage")
        return key
    dlg = ApiKeyDialog(parent=parent, invalid=False)
    dlg.exec()
    return dlg.get_key()


def prompt_reauth(parent=None) -> str:
    """Delete stored key and re-prompt (called on auth failure or 🔑 button)."""
    delete_api_key()
    dlg = ApiKeyDialog(parent=parent, invalid=True)
    dlg.exec()
    return dlg.get_key()
