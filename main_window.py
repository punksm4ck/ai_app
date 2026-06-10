"""
Main Window — AI Data Center Tracker  (Enterprise Edition)
"""

import json
import logging
import os
import stat
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QToolBar, QLabel, QPushButton,
    QComboBox, QCheckBox, QFrame, QLineEdit,
    QSizePolicy, QMessageBox,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import Qt, QUrl, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QCloseEvent

from ai_app.data_store import get_datacenters_as_json, get_stats, DATACENTERS
from ai_app.chat_sidebar import AIChatSidebar
from ai_app.water_meter import WaterMeterPanel, WaterStatusWidget, WaterMeterController

log = logging.getLogger(__name__)

ICON_PATH    = str(Path.home() / "Pictures/Icons/AIDataCenterTracker.png")
DESKTOP_FILE = Path.home() / ".local/share/applications/ai-datacenter-tracker.desktop"

STYLE = """
QMainWindow                { background: #080c16; }
QSplitter::handle          { background: rgba(100,200,255,0.12); width: 3px; }
QSplitter::handle:hover    { background: rgba(100,200,255,0.30); }
QToolBar {
    background: rgba(10,14,28,0.98);
    border-bottom: 1px solid rgba(100,200,255,0.20);
    spacing: 6px; padding: 3px 8px;
}
QStatusBar {
    background: rgba(8,12,20,0.98);
    border-top: 1px solid rgba(100,200,255,0.12);
    color: #4a7090; font-family: monospace; font-size: 11px;
}
QLabel       { color: #c0d8f0; font-family: monospace; }
QPushButton  {
    background: rgba(20,40,80,0.60);
    border: 1px solid rgba(100,200,255,0.25);
    border-radius: 5px; color: #80c0e0;
    font-family: monospace; font-size: 11px; padding: 5px 14px;
}
QPushButton:hover   { background: rgba(30,60,110,0.80); border-color: rgba(100,200,255,0.50); }
QPushButton:pressed { background: rgba(50,100,160,0.80); }
QComboBox {
    background: rgba(15,25,50,0.70);
    border: 1px solid rgba(100,200,255,0.20);
    border-radius: 5px; color: #90c8e8;
    font-family: monospace; font-size: 11px;
    padding: 4px 10px; min-width: 140px;
}
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background: #0a1428;
    border: 1px solid rgba(100,200,255,0.30);
    color: #90c8e8;
    selection-background-color: rgba(50,100,180,0.60);
}
QLineEdit {
    background: rgba(15,25,50,0.70);
    border: 1px solid rgba(100,200,255,0.20);
    border-radius: 5px; color: #90c8e8;
    font-family: monospace; font-size: 11px; padding: 4px 10px;
}
QLineEdit:focus { border-color: rgba(100,200,255,0.50); }
QCheckBox { color: #80c0e0; font-family: monospace; font-size: 10px; spacing: 6px; }
QCheckBox::indicator {
    width: 14px; height: 14px;
    border: 1px solid rgba(100,200,255,0.30);
    border-radius: 3px; background: rgba(20,40,80,0.50);
}
QCheckBox::indicator:checked { background: rgba(100,200,255,0.60); border-color: #64c8ff; }
QScrollArea  { background: transparent; border: none; }
QScrollBar:vertical { background: rgba(10,20,40,0.40); width: 6px; border-radius: 3px; }
QScrollBar::handle:vertical { background: rgba(100,200,255,0.25); border-radius: 3px; }
QToolTip {
    background: #0a1428; color: #90c8e8;
    border: 1px solid rgba(100,200,255,0.30);
    font-family: monospace; font-size: 10px; padding: 4px 8px;
}
"""

BTN_GREEN = """QPushButton{background:rgba(20,70,30,0.55);border:1px solid rgba(50,200,80,0.35);border-radius:5px;color:#50e878;font-family:monospace;font-size:11px;padding:5px 14px;}QPushButton:hover{background:rgba(30,100,40,0.80);border-color:rgba(80,220,100,0.60);}"""
BTN_RED   = """QPushButton{background:rgba(80,20,20,0.55);border:1px solid rgba(255,80,80,0.35);border-radius:5px;color:#ff7070;font-family:monospace;font-size:11px;padding:5px 14px;}QPushButton:hover{background:rgba(110,30,30,0.80);border-color:rgba(255,100,100,0.60);}"""
BTN_CHAT_ON  = """QPushButton{background:rgba(100,50,200,0.50);border:1px solid rgba(160,100,255,0.50);border-radius:5px;color:#c090ff;font-family:monospace;font-size:11px;padding:5px 14px;}QPushButton:hover{background:rgba(120,60,220,0.70);}"""
BTN_CHAT_OFF = """QPushButton{background:rgba(20,40,80,0.60);border:1px solid rgba(100,200,255,0.25);border-radius:5px;color:#80c0e0;font-family:monospace;font-size:11px;padding:5px 14px;}QPushButton:hover{background:rgba(30,60,110,0.80);border-color:rgba(100,200,255,0.50);}"""
BTN_WATER_ON  = """QPushButton{background:rgba(0,80,120,0.55);border:1px solid rgba(0,200,255,0.50);border-radius:5px;color:#00e0ff;font-family:monospace;font-size:11px;padding:5px 14px;}QPushButton:hover{background:rgba(0,100,140,0.70);}"""
BTN_WATER_OFF = """QPushButton{background:rgba(20,40,80,0.60);border:1px solid rgba(100,200,255,0.25);border-radius:5px;color:#80c0e0;font-family:monospace;font-size:11px;padding:5px 14px;}QPushButton:hover{background:rgba(30,60,110,0.80);}"""


def _desktop_exists() -> bool:
    return DESKTOP_FILE.exists()

def _create_desktop_launcher():
    main_py = Path(__file__).resolve().parent.parent / "main.py"
    import sys as _sys
    DESKTOP_FILE.parent.mkdir(parents=True, exist_ok=True)
    DESKTOP_FILE.write_text(
        f'[Desktop Entry]\nVersion=1.0\nType=Application\n'
        f'Name=AI Data Center Tracker\nGenericName=AI Infrastructure Map\n'
        f'Comment=Real-time USA AI Data Center tracker with Claude AI assistant\n'
        f'Exec=bash -c "cd {main_py.parent} && {_sys.executable} {main_py} 2>/dev/null"\n'
        f'Icon={ICON_PATH}\nTerminal=false\n'
        f'Categories=Science;Network;Education;\n'
        f'Keywords=AI;DataCenter;Infrastructure;Claude;Map;\n'
        f'StartupNotify=true\nStartupWMClass=AI Data Center Tracker\n'
    )
    DESKTOP_FILE.chmod(DESKTOP_FILE.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)
    os.system("update-desktop-database ~/.local/share/applications/ 2>/dev/null &")

def _remove_desktop_launcher():
    if DESKTOP_FILE.exists():
        DESKTOP_FILE.unlink()
    os.system("update-desktop-database ~/.local/share/applications/ 2>/dev/null &")


class FilterPanel(QFrame):
    filter_changed = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(224)
        self.setStyleSheet(
            "QFrame{background:rgba(8,12,22,0.98);"
            "border-right:1px solid rgba(100,200,255,0.12);}"
        )
        self._build()

    def _section(self, heading):
        outer = QFrame()
        outer.setStyleSheet(
            "QFrame{background:rgba(20,30,60,0.40);"
            "border:1px solid rgba(100,200,255,0.10); border-radius:6px;}"
        )
        vbox = QVBoxLayout(outer)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        hdr = QLabel(heading)
        hdr.setFont(QFont("Monospace", 8))
        hdr.setStyleSheet(
            "color:#3a6080;background:rgba(30,60,100,0.30);"
            "padding:4px 8px;letter-spacing:2px;border-radius:5px 5px 0 0;"
        )
        vbox.addWidget(hdr)
        return outer

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(14)

        ttl = QLabel("⬡  FILTERS")
        ttl.setFont(QFont("Monospace", 10))
        ttl.setStyleSheet("color:#64c8ff;letter-spacing:3px;font-weight:bold;")
        root.addWidget(ttl)

        # status
        g = self._section("STATUS")
        gl = QVBoxLayout(g); gl.setContentsMargins(6,8,6,8); gl.setSpacing(6)
        self.status_checks = {}
        for key, color, label in [
            ("active","#32ff96","Active"),
            ("construction","#ffb400","Under Construction"),
            ("planned","#64b4ff","Planned"),
            ("announced","#c864ff","Announced"),
        ]:
            cb = QCheckBox(label); cb.setChecked(True)
            cb.setStyleSheet(
                f"QCheckBox{{color:{color};}}"
                f"QCheckBox::indicator:checked{{background:{color};border-color:{color};}}"
            )
            cb.stateChanged.connect(self._emit_status)
            gl.addWidget(cb); self.status_checks[key] = cb
        root.addWidget(g)

        # operator
        g2 = self._section("OPERATOR")
        gl2 = QVBoxLayout(g2); gl2.setContentsMargins(6,8,6,8)
        self.operator_combo = QComboBox()
        self.operator_combo.addItem("All Operators")
        for op in sorted(set(dc.operator for dc in DATACENTERS)):
            self.operator_combo.addItem(op)
        self.operator_combo.currentTextChanged.connect(
            lambda t: self.filter_changed and self.filter_changed(
                "operator", "" if t == "All Operators" else t))
        gl2.addWidget(self.operator_combo); root.addWidget(g2)

        # state
        g3 = self._section("STATE")
        gl3 = QVBoxLayout(g3); gl3.setContentsMargins(6,8,6,8)
        self.state_combo = QComboBox()
        self.state_combo.addItem("All States")
        for st in sorted(set(dc.state for dc in DATACENTERS)):
            self.state_combo.addItem(st)
        self.state_combo.currentTextChanged.connect(
            lambda t: self.filter_changed and self.filter_changed(
                "state", "" if t == "All States" else t))
        gl3.addWidget(self.state_combo); root.addWidget(g3)

        # stats
        g4 = self._section("LIVE STATS")
        gl4 = QVBoxLayout(g4); gl4.setContentsMargins(8,8,8,8); gl4.setSpacing(7)
        s = get_stats()
        for lbl_t, val_t in [
            ("Total Facilities",   str(s["total"])),
            ("Active",             str(s["active"])),
            ("Construction",       str(s["construction"])),
            ("Planned",            str(s["planned"])),
            ("Total Capacity",     f"{s['total_mw']:,} MW"),
            ("Tracked Investment", f"${s['total_investment_bn']}B+"),
            ("Operators",          str(s["operators"])),
            ("States",             str(s["states"])),
        ]:
            row = QHBoxLayout(); row.setSpacing(4)
            l = QLabel(lbl_t); l.setFont(QFont("Monospace",8)); l.setStyleSheet("color:#4a7090;")
            v = QLabel(val_t); v.setFont(QFont("Monospace",9))
            v.setStyleSheet("color:#64c8ff;font-weight:bold;")
            v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(l,1); row.addWidget(v,0); gl4.addLayout(row)
        root.addWidget(g4)

        root.addStretch()
        rst = QPushButton("↺  Reset Filters")
        rst.setToolTip("Clear all filters and show all facilities")
        rst.clicked.connect(self._reset)
        root.addWidget(rst)

    def _emit_status(self):
        if self.filter_changed:
            self.filter_changed("status",
                [k for k, cb in self.status_checks.items() if cb.isChecked()])

    def _reset(self):
        for cb in self.status_checks.values(): cb.setChecked(True)
        self.operator_combo.setCurrentIndex(0)
        self.state_combo.setCurrentIndex(0)


class MainWindow(QMainWindow):

    def __init__(self, app_icon: QIcon = None):
        super().__init__()
        self._app_icon  = app_icon or QIcon(ICON_PATH)
        self.tray_icon  = None
        self._map_ready = False

        self.setWindowTitle("⬡  AI Data Center Tracker — USA")
        self.setWindowIcon(self._app_icon)
        self.resize(1600, 900)
        self.setMinimumSize(1100, 650)
        self.setStyleSheet(STYLE)

        self._build_toolbar()
        self._build_central()
        self._build_statusbar()
        self._wire_water_meter()

    def closeEvent(self, event: QCloseEvent):
        if self.tray_icon and self.tray_icon.isSystemTrayAvailable():
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "AI Data Center Tracker",
                "Running in the system tray — double-click to restore.",
                self._app_icon, 2500,
            )
        else:
            event.accept()

    # ── Toolbar ───────────────────────────────────────────────────────────
    def _build_toolbar(self):
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        tb.setContextMenuPolicy(Qt.ContextMenuPolicy.PreventContextMenu)

        def _vsep():
            f = QFrame()
            f.setFrameShape(QFrame.Shape.VLine)
            f.setStyleSheet("background:rgba(100,200,255,0.15);margin:5px 2px;")
            tb.addWidget(f)

        def _btn(text, tip, slot, style=None):
            b = QPushButton(text); b.setToolTip(tip); b.clicked.connect(slot)
            if style: b.setStyleSheet(style)
            tb.addWidget(b); return b

        lbl = QLabel("  ⬡  AI DATA CENTER TRACKER — USA  ")
        lbl.setFont(QFont("Monospace", 11))
        lbl.setStyleSheet("color:#64c8ff;font-weight:bold;letter-spacing:2px;")
        tb.addWidget(lbl); _vsep()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍  Search facilities…")
        self.search_box.setFixedWidth(210)
        self.search_box.setToolTip("Search by name, operator, city, state or tag")
        self.search_box.textChanged.connect(self._on_search)
        tb.addWidget(self.search_box); _vsep()

        _btn("↻  Refresh Data", "Reload all markers from the dataset", self._reload_data)
        _btn("🗺  Reset View",   "Fly back to the full USA view",       self._reset_view)
        _vsep()

        # Desktop launcher
        self.launcher_btn = QPushButton()
        self.launcher_btn.setToolTip("Create or remove the KDE/GNOME app-menu launcher")
        self.launcher_btn.clicked.connect(self._toggle_launcher)
        tb.addWidget(self.launcher_btn)
        self._sync_launcher_btn()
        _vsep()

        # Expanding spacer
        sp = QWidget()
        sp.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        tb.addWidget(sp)

        # Timestamp
        self.ts_label = QLabel()
        self.ts_label.setFont(QFont("Monospace", 9))
        self.ts_label.setStyleSheet("color:#2a4060;")
        tb.addWidget(self.ts_label)
        self._tick_timestamp()
        _vsep()

        # Water meter toggle
        self.water_btn = QPushButton("💧  Water")
        self.water_btn.setCheckable(True)
        self.water_btn.setChecked(False)
        self.water_btn.setToolTip("Show/hide the AI session water consumption meter")
        self.water_btn.setStyleSheet(BTN_WATER_OFF)
        self.water_btn.toggled.connect(self._toggle_water)
        tb.addWidget(self.water_btn)

        # AI Chat toggle — OFF at startup
        self.chat_btn = QPushButton("◧  AI Chat")
        self.chat_btn.setCheckable(True)
        self.chat_btn.setChecked(False)
        self.chat_btn.setToolTip("Toggle the Claude AI assistant sidebar")
        self.chat_btn.setStyleSheet(BTN_CHAT_OFF)
        self.chat_btn.toggled.connect(self._toggle_chat)
        tb.addWidget(self.chat_btn)

    # ── Desktop launcher ──────────────────────────────────────────────────
    def _sync_launcher_btn(self):
        if _desktop_exists():
            self.launcher_btn.setText("🗑  Remove Desktop Launcher")
            self.launcher_btn.setStyleSheet(BTN_RED)
        else:
            self.launcher_btn.setText("🖥  Create Desktop Launcher")
            self.launcher_btn.setStyleSheet(BTN_GREEN)

    def _toggle_launcher(self):
        if _desktop_exists():
            _remove_desktop_launcher()
            self._status("Desktop launcher removed.")
        else:
            try:
                _create_desktop_launcher()
                self._status(f"Desktop launcher created → {DESKTOP_FILE}")
            except Exception as exc:
                log.exception("Failed to create desktop launcher")
                QMessageBox.critical(self, "Launcher Error", str(exc))
        self._sync_launcher_btn()

    # ── Central layout ────────────────────────────────────────────────────
    def _build_central(self):
        root = QWidget(); root.setStyleSheet("background:#080c16;")
        self.setCentralWidget(root)
        hl = QHBoxLayout(root)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(0)

        self.filter_panel = FilterPanel()
        self.filter_panel.filter_changed = self._on_filter
        hl.addWidget(self.filter_panel)

        # Vertical splitter: [map+chat] on top, water panel below
        self._v_splitter = QSplitter(Qt.Orientation.Vertical)
        self._v_splitter.setChildrenCollapsible(True)

        # Horizontal splitter: map | chat
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)

        self.webview = QWebEngineView()
        ws = self.webview.settings()
        ws.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        ws.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        ws.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        html_path = Path(__file__).resolve().parent / "map_widget.html"
        self.webview.loadFinished.connect(self._on_map_loaded)
        self.webview.setUrl(QUrl.fromLocalFile(str(html_path)))
        self.splitter.addWidget(self.webview)

        # AI Chat — HIDDEN at startup
        self.chat = AIChatSidebar()
        self.chat.setVisible(False)
        self.splitter.addWidget(self.chat)
        self.splitter.setSizes([1600, 0])

        self._v_splitter.addWidget(self.splitter)

        # Water meter panel — HIDDEN at startup
        self.water_panel = WaterMeterPanel()
        self.water_panel.setVisible(False)
        self._v_splitter.addWidget(self.water_panel)
        self._v_splitter.setSizes([900, 0])

        hl.addWidget(self._v_splitter)

    # ── Status bar ────────────────────────────────────────────────────────
    def _build_statusbar(self):
        sb = self.statusBar()
        s  = get_stats()
        for text, style in [
            (f"  {s['total']} facilities",            "color:#c0d8f0;"),
            (f"  ● {s['active']} active",             "color:#32ff96;"),
            (f"  ◐ {s['construction']} construction", "color:#ffb400;"),
            (f"  ○ {s['planned']} planned",           "color:#64b4ff;"),
            (f"  ⚡ {s['total_mw']:,} MW tracked",    "color:#4a7090;"),
        ]:
            lbl = QLabel(text); lbl.setStyleSheet(style)
            sb.addWidget(lbl)

        # Water status widget — always visible in status bar
        self.water_status = WaterStatusWidget()
        sb.addWidget(self.water_status)

        sb.addPermanentWidget(
            QLabel("  Data: curated public sources — updated continuously  "))

    # ── Wire water meter to chat word signal ──────────────────────────────
    def _wire_water_meter(self):
        self.water_ctrl = WaterMeterController(
            panel=self.water_panel,
            status=self.water_status,
        )
        def _on_words(delta: int):
            if delta == -999999:           # sentinel from Clear button
                self.water_ctrl.reset()
            else:
                self.water_ctrl.add_words(delta)
        self.chat.words_generated.connect(_on_words)

    # ── Map ───────────────────────────────────────────────────────────────
    def _on_map_loaded(self, ok: bool):
        if ok:
            self._map_ready = True
            self._push_markers()
            self._status("Map loaded — 60 facilities plotted.")

    def _push_markers(self):
        if not self._map_ready: return
        data = get_datacenters_as_json().replace("\\","\\\\").replace("`","\\`")
        self.webview.page().runJavaScript(f"loadDatacenters({data});")

    def _reload_data(self):
        self._push_markers(); self._tick_timestamp(); self._status("Dataset refreshed.")

    def _reset_view(self):
        self._js("map.flyTo([38.5,-96.0],4,{animate:true,duration:1.2});")

    def _js(self, code):
        if self._map_ready: self.webview.page().runJavaScript(code)

    # ── Search ────────────────────────────────────────────────────────────
    def _on_search(self, raw: str):
        text = raw.strip().lower()
        if not text:
            self._js("filterByOperator('');"); return
        matches = [
            dc for dc in DATACENTERS
            if text in dc.name.lower() or text in dc.operator.lower()
            or text in dc.city.lower() or text in dc.state.lower()
            or any(text in t for t in dc.tags)
        ]
        if len(matches) == 1:
            self._js(f"highlightMarker('{matches[0].id}');")
        elif matches:
            ids = json.dumps([m.id for m in matches])
            self._js(f"""allMarkers.forEach(function(m){{
                var ok={ids};var g=layerGroups[m.dc.status];
                if(ok.indexOf(m.dc.id)!==-1){{if(!g.hasLayer(m))g.addLayer(m);}}
                else g.removeLayer(m);}});""")
        self._status(f"Search '{raw.strip()}' → {len(matches)} result(s)")

    # ── Filters ───────────────────────────────────────────────────────────
    def _on_filter(self, kind, value):
        if kind == "status":
            self._js(f"filterByStatus({json.dumps(value)});")
        elif kind == "operator":
            self._js(f"filterByOperator('{value.replace(chr(39),chr(92)+chr(39))}');")
        elif kind == "state":
            if value: self._js(f"zoomToState('{value.replace(chr(39),chr(92)+chr(39))}');")
            else: self._reset_view()

    # ── Chat toggle ───────────────────────────────────────────────────────
    def _toggle_chat(self, on: bool):
        self.chat.setVisible(on)
        self.chat_btn.setStyleSheet(BTN_CHAT_ON if on else BTN_CHAT_OFF)
        self.splitter.setSizes([1200, 400] if on else [1600, 0])

    # ── Water meter toggle ────────────────────────────────────────────────
    def _toggle_water(self, on: bool):
        self.water_panel.setVisible(on)
        self.water_btn.setStyleSheet(BTN_WATER_ON if on else BTN_WATER_OFF)
        self._v_splitter.setSizes([700, 220] if on else [900, 0])

    # ── Helpers ───────────────────────────────────────────────────────────
    def _tick_timestamp(self):
        self.ts_label.setText(
            "  " + datetime.now().strftime("%Y-%m-%d  %H:%M:%S") + "  ")
        QTimer.singleShot(60_000, self._tick_timestamp)

    def _status(self, msg: str, ms: int = 5000):
        self.statusBar().showMessage(f"  {msg}", ms)
