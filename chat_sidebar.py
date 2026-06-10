"""
AI Chat Sidebar — Claude claude-sonnet-4-20250514  (Enterprise Edition)
Streaming responses, conversation history, context-aware about the dataset.
Emits word_count_changed(int) signal so the water meter can track usage.
"""

import json
import logging
import re
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QScrollArea, QFrame,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from ai_app.data_store import get_stats

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert AI infrastructure analyst embedded in the \
"AI Data Center Tracker" desktop application — a real-time tool for monitoring \
active, under-construction, and planned AI data centers across the USA.

You have deep expertise in:
• Hyperscale and AI-focused data centers (Microsoft, Google/DeepMind, Amazon/AWS, \
Meta, OpenAI/Stargate, xAI, CoreWeave, Oracle, Apple, Equinix, etc.)
• GPU compute infrastructure: H100/H200/B200 clusters, training vs inference workloads
• Power requirements, cooling technologies, PUE, water usage
• Site selection factors: power grid access, land cost, tax incentives, fibre routes
• Investment trends, REIT structures, colocation vs hyperscale models
• The AI compute arms race and its geopolitical/economic implications

The live dataset is injected into context below. When answering, cite specific \
facilities by name when relevant. Be analytical, precise, and data-driven. \
Keep responses concise but insight-rich. Use bullet points for comparisons."""


def _count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


class _StreamWorker(QThread):
    chunk   = pyqtSignal(str)
    done    = pyqtSignal()
    error   = pyqtSignal(str)

    def __init__(self, messages: list, parent=None):
        super().__init__(parent)
        self._messages = messages

    def run(self):
        try:
            import anthropic
            client = anthropic.Anthropic()
            stats  = get_stats()
            system = (
                SYSTEM_PROMPT
                + f"\n\nLive dataset summary: {json.dumps(stats, indent=2)}"
            )
            with client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system,
                messages=self._messages,
            ) as stream:
                for text in stream.text_stream:
                    self.chunk.emit(text)
            self.done.emit()
        except Exception as exc:
            log.exception("Streaming error")
            self.error.emit(f"⚠  {type(exc).__name__}: {exc}")


class _Bubble(QFrame):
    def __init__(self, text: str, role: str, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 7, 10, 7)
        lay.setSpacing(3)
        who = QLabel("You" if role == "user" else "Claude")
        who.setFont(QFont("Monospace", 8))
        who.setStyleSheet(
            "color:#64c8ff; font-weight:bold;" if role == "user"
            else "color:#a064ff; font-weight:bold;"
        )
        lay.addWidget(who)
        self.body = QLabel(text)
        self.body.setWordWrap(True)
        self.body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.body.setFont(QFont("Monospace", 9))
        self.body.setStyleSheet("color:#d0e8ff; line-height:1.5;")
        lay.addWidget(self.body)
        if role == "user":
            self.setStyleSheet(
                "QFrame{background:rgba(40,80,140,0.35);"
                "border:1px solid rgba(100,200,255,0.20);"
                "border-radius:8px; margin:2px 24px 2px 4px;}"
            )
        else:
            self.setStyleSheet(
                "QFrame{background:rgba(60,30,100,0.30);"
                "border:1px solid rgba(160,100,255,0.20);"
                "border-radius:8px; margin:2px 4px 2px 24px;}"
            )

    def set_text(self, text: str):
        self.body.setText(text)


class AIChatSidebar(QWidget):
    # Emitted with the NEW words added each chunk (delta, not total)
    words_generated = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        self._history: list = []
        self._worker        = None
        self._live_bubble   = None
        self._live_text     = ""
        self._prev_len      = 0   # char length before current stream chunk
        self._dot_timer     = QTimer(self)
        self._dot_count     = 0
        self._dot_timer.timeout.connect(self._animate_dots)
        self._build()

    def _build(self):
        self.setStyleSheet("background:rgba(8,12,22,0.98);")
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # header
        hdr = QFrame()
        hdr.setFixedHeight(50)
        hdr.setStyleSheet(
            "QFrame{background:rgba(10,14,26,0.95);"
            "border-bottom:1px solid rgba(160,100,255,0.30);}"
        )
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(12, 0, 12, 0)
        icon_lbl = QLabel("⬡")
        icon_lbl.setFont(QFont("Monospace", 18))
        icon_lbl.setStyleSheet("color:#a064ff;")
        hl.addWidget(icon_lbl)
        col = QVBoxLayout()
        col.setSpacing(0)
        t1 = QLabel("Claude AI Assistant")
        t1.setFont(QFont("Monospace", 11))
        t1.setStyleSheet("color:#e0d0ff; font-weight:bold;")
        t2 = QLabel("claude-sonnet-4-20250514")
        t2.setFont(QFont("Monospace", 8))
        t2.setStyleSheet("color:#503860;")
        col.addWidget(t1); col.addWidget(t2)
        hl.addLayout(col); hl.addStretch()
        self._status_dot = QLabel("●")
        self._status_dot.setFont(QFont("Monospace", 10))
        self._status_dot.setStyleSheet("color:#32ff96;")
        hl.addWidget(self._status_dot)
        root.addWidget(hdr)

        # quick prompts
        qf = QFrame()
        qf.setStyleSheet(
            "background:rgba(20,10,40,0.60);"
            "border-bottom:1px solid rgba(160,100,255,0.15);"
        )
        ql = QHBoxLayout(qf)
        ql.setContentsMargins(8, 5, 8, 5)
        ql.setSpacing(5)
        for label, prompt in [
            ("📊 Stats",  "Give me a statistical overview of all tracked data centers — total capacity, investment, and breakdown by status."),
            ("🔥 Mega",   "Which are the largest planned or under-construction AI data center projects in the USA right now?"),
            ("🗺 States", "Which US states have the most AI data center activity and why?"),
        ]:
            b = QPushButton(label)
            b.setFont(QFont("Monospace", 8))
            b.setStyleSheet(
                "QPushButton{background:rgba(160,100,255,0.10);"
                "border:1px solid rgba(160,100,255,0.25);"
                "border-radius:12px; color:#b080ff; padding:3px 9px;}"
                "QPushButton:hover{background:rgba(160,100,255,0.22);"
                "border-color:rgba(160,100,255,0.55);}"
            )
            b.clicked.connect(lambda _, p=prompt: self._send(p))
            ql.addWidget(b)
        root.addWidget(qf)

        # message scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet(
            "QScrollArea{background:transparent;border:none;}"
            "QScrollBar:vertical{background:rgba(20,30,50,0.50);width:5px;border-radius:3px;}"
            "QScrollBar::handle:vertical{background:rgba(100,200,255,0.30);border-radius:3px;}"
        )
        self._msg_widget = QWidget()
        self._msg_widget.setStyleSheet("background:transparent;")
        self._msg_layout = QVBoxLayout(self._msg_widget)
        self._msg_layout.setContentsMargins(8, 8, 8, 8)
        self._msg_layout.setSpacing(8)
        self._msg_layout.addStretch()
        self._scroll.setWidget(self._msg_widget)
        root.addWidget(self._scroll)

        # input area
        inf = QFrame()
        inf.setStyleSheet(
            "QFrame{background:rgba(10,14,26,0.95);"
            "border-top:1px solid rgba(160,100,255,0.20);}"
        )
        il = QVBoxLayout(inf)
        il.setContentsMargins(10, 8, 10, 10)
        il.setSpacing(6)
        self._input = QTextEdit()
        self._input.setPlaceholderText(
            "Ask about AI data centers, trends, operators…  (Enter to send)")
        self._input.setFixedHeight(68)
        self._input.setFont(QFont("Monospace", 9))
        self._input.setStyleSheet(
            "QTextEdit{background:rgba(20,30,60,0.60);"
            "border:1px solid rgba(100,200,255,0.20);"
            "border-radius:7px; color:#d0e8ff; padding:7px;}"
            "QTextEdit:focus{border-color:rgba(160,100,255,0.50);}"
        )
        self._input.installEventFilter(self)
        il.addWidget(self._input)
        br = QHBoxLayout()
        br.setSpacing(8)
        clr = QPushButton("Clear")
        clr.setFont(QFont("Monospace", 8))
        clr.setFixedHeight(28)
        clr.setStyleSheet(
            "QPushButton{background:rgba(60,20,20,0.50);"
            "border:1px solid rgba(255,80,80,0.20);"
            "border-radius:5px; color:#ff6060; padding:0 10px;}"
            "QPushButton:hover{background:rgba(80,20,20,0.70);}"
        )
        clr.clicked.connect(self._clear)
        self._send_btn = QPushButton("Send  ↵")
        self._send_btn.setFont(QFont("Monospace", 9))
        self._send_btn.setFixedHeight(28)
        self._send_btn.setStyleSheet(
            "QPushButton{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 rgba(100,50,200,0.80),stop:1 rgba(160,100,255,0.80));"
            "border:1px solid rgba(160,100,255,0.50);"
            "border-radius:5px; color:#fff; font-weight:bold; padding:0 14px;}"
            "QPushButton:hover{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 rgba(120,60,220,0.90),stop:1 rgba(180,120,255,0.90));}"
            "QPushButton:disabled{opacity:0.35;}"
        )
        self._send_btn.clicked.connect(self._on_send_click)
        br.addWidget(clr); br.addStretch(); br.addWidget(self._send_btn)
        il.addLayout(br)
        root.addWidget(inf)

        QTimer.singleShot(400, self._welcome)

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        if obj is self._input and event.type() == QEvent.Type.KeyPress:
            if (event.key() == Qt.Key.Key_Return
                    and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier)):
                self._on_send_click()
                return True
        return super().eventFilter(obj, event)

    def _welcome(self):
        s = get_stats()
        msg = (
            f"👋  Live dataset loaded: {s['total']} facilities across {s['states']} states.\n\n"
            f"• {s['active']} active  •  {s['construction']} under construction"
            f"  •  {s['planned']} planned/announced\n"
            f"• {s['total_mw']:,} MW total tracked capacity\n"
            f"• ${s['total_investment_bn']}B+ in tracked investments\n\n"
            "Ask me anything about the AI infrastructure buildout."
        )
        bubble = self._add_bubble(msg, "assistant")
        # count welcome words toward water meter
        self.words_generated.emit(_count_words(msg))

    def _on_send_click(self):
        text = self._input.toPlainText().strip()
        if text:
            self._send(text)
            self._input.clear()

    def _send(self, text: str):
        if self._worker and self._worker.isRunning():
            return
        self._add_bubble(text, "user")
        self._history.append({"role": "user", "content": text})
        self._live_text  = ""
        self._prev_len   = 0
        self._live_bubble = self._add_bubble("○  ○  ○", "assistant")
        self._dot_count  = 0
        self._dot_timer.start(420)
        self._send_btn.setEnabled(False)
        self._status_dot.setStyleSheet("color:#ffb400;")
        self._worker = _StreamWorker(list(self._history))
        self._worker.chunk.connect(self._on_chunk)
        self._worker.done.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _animate_dots(self):
        frames = ["⬤  ○  ○", "○  ⬤  ○", "○  ○  ⬤"]
        if self._live_bubble and not self._live_text:
            self._live_bubble.set_text(frames[self._dot_count % 3])
            self._dot_count += 1

    def _on_chunk(self, text: str):
        self._dot_timer.stop()
        old_word_count = _count_words(self._live_text)
        self._live_text += text
        new_word_count  = _count_words(self._live_text)
        delta = new_word_count - old_word_count
        if delta > 0:
            self.words_generated.emit(delta)
        if self._live_bubble:
            self._live_bubble.set_text(self._live_text)
        self._scroll_bottom()

    def _on_done(self):
        self._dot_timer.stop()
        self._send_btn.setEnabled(True)
        self._status_dot.setStyleSheet("color:#32ff96;")
        if self._live_text:
            self._history.append({"role": "assistant", "content": self._live_text})
        self._live_bubble = None
        self._live_text   = ""

    def _on_error(self, msg: str):
        self._dot_timer.stop()
        if self._live_bubble:
            self._live_bubble.set_text(msg)
        self._send_btn.setEnabled(True)
        self._status_dot.setStyleSheet("color:#ff4040;")
        log.error("Chat error: %s", msg)

    def _add_bubble(self, text: str, role: str) -> _Bubble:
        b = _Bubble(text, role)
        count = self._msg_layout.count()
        self._msg_layout.insertWidget(count - 1, b)
        QTimer.singleShot(40, self._scroll_bottom)
        return b

    def _scroll_bottom(self):
        self._scroll.verticalScrollBar().setValue(
            self._scroll.verticalScrollBar().maximum())

    def _clear(self):
        self._history.clear()
        while self._msg_layout.count() > 1:
            item = self._msg_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # signal reset to water meter
        self.words_generated.emit(-999999)   # sentinel → controller will reset
        QTimer.singleShot(200, self._welcome)
