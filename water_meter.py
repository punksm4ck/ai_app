"""
AI Water Consumption Meter
--------------------------
Tracks estimated water usage of the current AI chat session.

Metric (from your Chrome extension):
  100 words generated  →  16 fl oz of water
  100 words generated  →  2 g CO2e

This widget counts words produced by Claude in the chat sidebar and converts
them to 16 oz water bottle equivalents, fl oz, CO2, and raw word count.

It lives in the main window as a dockable panel that can be toggled from the
toolbar, and also exposes a compact label-set for the status bar.
"""

import logging
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QWidget,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

log = logging.getLogger(__name__)

OZ_PER_100_WORDS   = 16.0          # fl oz of water per 100 AI-generated words
CO2_PER_100_WORDS  =  2.0          # grams CO2e per 100 AI-generated words
BOTTLE_FL_OZ       = 16.0          # standard 16 oz water bottle
POOL_FL_OZ         = 84_535_040.0  # Olympic pool in fl oz (kept for reference)


def _words_in(text: str) -> int:
    import re
    return len(re.findall(r"\b\w+\b", text))


class WaterStatusWidget(QWidget):
    """
    A slim inline widget for the status bar showing:
      💧 0 bottles   🌿 0.00g CO2   📝 0 words
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        hl = QHBoxLayout(self)
        hl.setContentsMargins(6, 0, 6, 0)
        hl.setSpacing(14)

        def _lbl(text, color):
            l = QLabel(text)
            l.setFont(QFont("Monospace", 10))
            l.setStyleSheet(f"color:{color};")
            return l

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background:rgba(100,200,255,0.12); margin:3px 0;")
        hl.addWidget(sep)

        self._bottle_lbl = _lbl("💧 0 bottles", "#00cfff")
        self._co2_lbl    = _lbl("🌿 0.00g CO₂", "#50e878")
        self._word_lbl   = _lbl("📝 0 words",   "#a0a0c0")

        for w in (self._bottle_lbl, self._co2_lbl, self._word_lbl):
            hl.addWidget(w)

    def update_stats(self, words: int, oz: float, co2: float, bottles: float):
        self._bottle_lbl.setText(f"💧 {bottles:,.2f} bottles")
        self._co2_lbl.setText(   f"🌿 {co2:,.2f}g CO₂")
        self._word_lbl.setText(  f"📝 {words:,} words")


class WaterMeterPanel(QFrame):
    """
    A compact floating-style panel that displays four metrics.
    Designed to sit above the status bar on the right side of the window.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setStyleSheet("""
            QFrame#waterPanel {
                background: rgba(0,10,20,0.94);
                border: 1px solid rgba(0,200,255,0.30);
                border-radius: 10px;
            }
        """)
        self.setObjectName("waterPanel")
        self._build()
        self._words = 0

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(10)

        # ── Header ────────────────────────────────────────────────────────
        hdr = QLabel("💧  AI SESSION WATER USAGE")
        hdr.setFont(QFont("Monospace", 9))
        hdr.setStyleSheet(
            "color:rgba(0,200,255,0.70); letter-spacing:1.5px;"
            " border-bottom:1px solid rgba(0,200,255,0.15);"
            " padding-bottom:6px;"
        )
        root.addWidget(hdr)

        # ── Big number: bottles ───────────────────────────────────────────
        bottle_row = QHBoxLayout()
        bottle_row.setSpacing(8)
        bottle_icon = QLabel("🍶")
        bottle_icon.setFont(QFont("Monospace", 22))
        bottle_row.addWidget(bottle_icon)

        bottle_col = QVBoxLayout()
        bottle_col.setSpacing(0)
        self._bottle_big = QLabel("0.0000000000")
        self._bottle_big.setFont(QFont("Monospace", 18))
        self._bottle_big.setStyleSheet("color:#00ffff; font-weight:bold;")
        self._bottle_unit = QLabel("16 oz bottles")
        self._bottle_unit.setFont(QFont("Monospace", 9))
        self._bottle_unit.setStyleSheet("color:rgba(0,200,255,0.45);")
        bottle_col.addWidget(self._bottle_big)
        bottle_col.addWidget(self._bottle_unit)
        bottle_row.addLayout(bottle_col)
        bottle_row.addStretch()
        root.addLayout(bottle_row)

        # ── Grid of sub-metrics ───────────────────────────────────────────
        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)

        def _metric(icon, label, color):
            ico  = QLabel(icon)
            ico.setFont(QFont("Monospace", 13))
            lbl  = QLabel(label)
            lbl.setFont(QFont("Monospace", 8))
            lbl.setStyleSheet("color:rgba(160,160,180,0.70);")
            val  = QLabel("—")
            val.setFont(QFont("Monospace", 12))
            val.setStyleSheet(f"color:{color}; font-weight:bold;")
            val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            return ico, lbl, val

        # row 0 — fl oz
        i0, l0, self._oz_val    = _metric("💧", "Fluid Ounces",  "#00cfff")
        # row 1 — CO2
        i1, l1, self._co2_val   = _metric("🌿", "CO₂ Estimate",  "#50e878")
        # row 2 — words
        i2, l2, self._word_val  = _metric("📝", "Session Words", "#a0a0c0")
        # row 3 — pool fraction
        i3, l3, self._pool_val  = _metric("🏊", "Olympic Pool ×", "#6080ff")

        for row, (ico, lbl, val) in enumerate(
            [(i0,l0,self._oz_val),(i1,l1,self._co2_val),
             (i2,l2,self._word_val),(i3,l3,self._pool_val)]
        ):
            grid.addWidget(ico, row, 0)
            grid.addWidget(lbl, row, 1)
            grid.addWidget(val, row, 2)

        root.addLayout(grid)

        # ── Footer note ───────────────────────────────────────────────────
        note = QLabel("16 oz / 100 words  ·  2g CO₂ / 100 words")
        note.setFont(QFont("Monospace", 7))
        note.setStyleSheet(
            "color:rgba(80,120,140,0.60);"
            " border-top:1px solid rgba(100,200,255,0.08);"
            " padding-top:6px;"
        )
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(note)

    def update_stats(self, words: int, oz: float, co2: float,
                     bottles: float, pool_frac: float):
        self._bottle_big.setText(f"{bottles:.10f}")
        self._oz_val.setText(   f"{oz:,.2f} oz")
        self._co2_val.setText(  f"{co2:,.2f} g")
        self._word_val.setText( f"{words:,}")
        self._pool_val.setText( f"{pool_frac:.10f}")
        self._words = words


class WaterMeterController:
    """
    Wires the chat sidebar word-count into both the panel and the status widget.
    Call  .add_words(n)  whenever new AI words are generated.
    Call  .reset()       to clear the session.
    """
    # multipliers (per single word)
    _OZ_PER_WORD   = OZ_PER_100_WORDS  / 100.0
    _CO2_PER_WORD  = CO2_PER_100_WORDS / 100.0
    _POOL_PER_WORD = OZ_PER_100_WORDS  / (100.0 * POOL_FL_OZ)
    _BTL_PER_WORD  = OZ_PER_100_WORDS  / (100.0 * BOTTLE_FL_OZ)

    def __init__(self, panel: WaterMeterPanel, status: WaterStatusWidget):
        self._panel  = panel
        self._status = status
        self._words  = 0

    def add_words(self, n: int):
        if n <= 0:
            return
        self._words += n
        self._refresh()

    def set_words(self, total: int):
        """Set absolute word count (useful when re-counting full history)."""
        if total < 0:
            return
        self._words = total
        self._refresh()

    def reset(self):
        self._words = 0
        self._refresh()

    def _refresh(self):
        w   = self._words
        oz  = w * self._OZ_PER_WORD
        co2 = w * self._CO2_PER_WORD
        btl = w * self._BTL_PER_WORD
        poo = w * self._POOL_PER_WORD
        self._panel.update_stats(w, oz, co2, btl, poo)
        self._status.update_stats(w, oz, co2, btl)
        log.debug("Water meter: %d words → %.2f oz / %.4f bottles", w, oz, btl)
