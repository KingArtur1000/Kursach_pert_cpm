"""
Темы приложения: QSS для виджетов + палитры для matplotlib.
"""

# ================================================================ QSS

DARK_QSS = """
QWidget {
    background-color: #1e1e24;
    color: #e6e6e6;
    font-size: 10pt;
}
QMainWindow, QDialog { background-color: #181820; }

QMenuBar {
    background-color: #232330;
    border-bottom: 1px solid #333;
}
QMenuBar::item { background: transparent; padding: 4px 10px; }
QMenuBar::item:selected { background: #3a3a4a; }
QMenu { background-color: #232330; border: 1px solid #3a3a4a; }
QMenu::item { padding: 6px 24px 6px 12px; }
QMenu::item:selected { background: #4a4a5e; }

QToolBar {
    background-color: #232330;
    border-bottom: 1px solid #333;
    spacing: 4px;
    padding: 4px;
}
QToolButton {
    background: transparent;
    padding: 6px 10px;
    border-radius: 4px;
}
QToolButton:hover { background: #3a3a4a; }
QToolButton:pressed { background: #4a4a5e; }

QStatusBar {
    background-color: #232330;
    border-top: 1px solid #333;
    color: #b0b0b0;
}

QTableWidget {
    background-color: #202028;
    alternate-background-color: #26262f;
    gridline-color: #333;
    selection-background-color: #3b6ea5;
    selection-color: #ffffff;
}
QHeaderView::section {
    background-color: #2a2a36;
    color: #e6e6e6;
    padding: 6px;
    border: none;
    border-right: 1px solid #333;
    border-bottom: 1px solid #333;
}
QTableWidget QTableCornerButton::section { background: #2a2a36; }

QTabWidget::pane { border: 1px solid #333; background: #181820; }
QTabBar::tab {
    background: #232330;
    color: #b0b0b0;
    padding: 6px 14px;
    border: 1px solid #333;
    border-bottom: none;
}
QTabBar::tab:selected { background: #181820; color: #ffffff; }
QTabBar::tab:hover { background: #2a2a3a; }

QPushButton {
    background-color: #2f2f3d;
    border: 1px solid #444;
    padding: 6px 12px;
    border-radius: 4px;
}
QPushButton:hover { background-color: #3a3a4a; }
QPushButton:pressed { background-color: #4a4a5e; }

QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
    background-color: #2a2a36;
    border: 1px solid #444;
    padding: 4px 6px;
    border-radius: 4px;
    color: #e6e6e6;
}
QComboBox QAbstractItemView {
    background: #2a2a36;
    border: 1px solid #444;
    selection-background-color: #3b6ea5;
    color: #e6e6e6;
}
QComboBox::drop-down { border: none; width: 18px; }

QSplitter::handle { background: #333; }

QScrollBar:vertical { background: #202028; width: 10px; margin: 0; }
QScrollBar::handle:vertical {
    background: #444; border-radius: 5px; min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #555; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #202028; height: 10px; margin: 0; }
QScrollBar::handle:horizontal {
    background: #444; border-radius: 5px; min-width: 20px;
}
QScrollBar::handle:horizontal:hover { background: #555; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QLabel { background: transparent; }
"""


LIGHT_QSS = """
QWidget {
    background-color: #f5f6fa;
    color: #1a1a1a;
    font-size: 10pt;
}
QMainWindow, QDialog { background-color: #ffffff; }

QMenuBar {
    background-color: #e9ebf2;
    border-bottom: 1px solid #d0d3dc;
}
QMenuBar::item { background: transparent; padding: 4px 10px; }
QMenuBar::item:selected { background: #d6d9e3; }
QMenu {
    background-color: #ffffff;
    border: 1px solid #c0c3cc;
}
QMenu::item { padding: 6px 24px 6px 12px; color: #1a1a1a; }
QMenu::item:selected { background: #d6e4f5; color: #0b3a75; }
QMenu::separator { height: 1px; background: #d0d3dc; margin: 4px 8px; }

QToolBar {
    background-color: #e9ebf2;
    border-bottom: 1px solid #d0d3dc;
    spacing: 4px;
    padding: 4px;
}
QToolButton {
    background: transparent;
    padding: 6px 10px;
    border-radius: 4px;
    color: #1a1a1a;
}
QToolButton:hover { background: #d6d9e3; }
QToolButton:pressed { background: #c3c7d3; }

QStatusBar {
    background-color: #e9ebf2;
    border-top: 1px solid #d0d3dc;
    color: #333333;
}
QStatusBar::item { border: none; }

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f3f5fa;
    gridline-color: #d0d3dc;
    selection-background-color: #3b6ea5;
    selection-color: #ffffff;
    color: #1a1a1a;
}
QHeaderView::section {
    background-color: #e1e4ec;
    color: #1a1a1a;
    padding: 6px;
    border: none;
    border-right: 1px solid #d0d3dc;
    border-bottom: 1px solid #d0d3dc;
}
QTableWidget QTableCornerButton::section { background: #e1e4ec; }

QTabWidget::pane {
    border: 1px solid #d0d3dc;
    background: #ffffff;
}
QTabBar::tab {
    background: #e9ebf2;
    color: #555555;
    padding: 6px 14px;
    border: 1px solid #d0d3dc;
    border-bottom: none;
}
QTabBar::tab:selected {
    background: #ffffff;
    color: #0b3a75;
    border-bottom: 2px solid #3b6ea5;
}
QTabBar::tab:hover { background: #dde0e8; }

QPushButton {
    background-color: #ffffff;
    border: 1px solid #b8bcc8;
    padding: 6px 12px;
    border-radius: 4px;
    color: #1a1a1a;
}
QPushButton:hover { background-color: #eef1f7; }
QPushButton:pressed { background-color: #dfe3ec; }

QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
    background-color: #ffffff;
    border: 1px solid #b8bcc8;
    padding: 4px 6px;
    border-radius: 4px;
    color: #1a1a1a;
    selection-background-color: #3b6ea5;
    selection-color: #ffffff;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #b8bcc8;
    selection-background-color: #d6e4f5;
    selection-color: #0b3a75;
    color: #1a1a1a;
}
QComboBox::drop-down { border: none; width: 18px; }

QSplitter::handle { background: #d0d3dc; }

QScrollBar:vertical {
    background: #f0f2f7;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #c0c4cf;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #a8adba; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal {
    background: #f0f2f7;
    height: 10px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #c0c4cf;
    border-radius: 5px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover { background: #a8adba; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

QLabel { background: transparent; }
"""


# ================================================================ Палитры
# Используются в matplotlib для согласования графиков с темой.

PALETTES = {
    "dark": {
        "fig_bg": "#181820",
        "ax_bg": "#181820",
        "text": "#e6e6e6",
        "subtext": "#cccccc",
        "spine": "#444444",
        "grid": "#444444",
        "critical": "#ff6b6b",
        "normal": "#4dabf7",
        "reserve": "#666666",
        "reserve_edge": "#aaaaaa",
        "duration": "#4dff88",
        "legend_bg": "#232330",
        "legend_edge": "#444444",
        "node_critical": "#ff6b6b",
        "node_normal": "#4dabf7",
        "node_edge": "#ffffff",
        "edge_critical": "#ff3b3b",
        "edge_normal": "#888888",
    },
    "light": {
        "fig_bg": "#ffffff",
        "ax_bg": "#ffffff",
        "text": "#1a1a1a",
        "subtext": "#444444",
        "spine": "#bbbbbb",
        "grid": "#cccccc",
        "critical": "#e74c3c",
        "normal": "#3498db",
        "reserve": "#d0d3dc",
        "reserve_edge": "#888888",
        "duration": "#27ae60",
        "legend_bg": "#f7f8fb",
        "legend_edge": "#c0c4cf",
        "node_critical": "#e74c3c",
        "node_normal": "#3498db",
        "node_edge": "#ffffff",
        "edge_critical": "#c0392b",
        "edge_normal": "#666666",
    },
}


def apply_theme(app, theme: str):
    app.setStyleSheet(DARK_QSS if theme == "dark" else LIGHT_QSS)


def palette(theme: str) -> dict:
    return PALETTES.get(theme, PALETTES["dark"])