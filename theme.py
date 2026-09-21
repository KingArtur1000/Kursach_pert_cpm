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
QMenuBar::item:selected { background: #3a3a4a; }
QMenu { background-color: #232330; border: 1px solid #3a3a4a; }
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

QTabWidget::pane {
    border: 1px solid #333;
    background: #181820;
}
QTabBar::tab {
    background: #232330;
    color: #b0b0b0;
    padding: 6px 14px;
    border: 1px solid #333;
    border-bottom: none;
}
QTabBar::tab:selected {
    background: #181820;
    color: #ffffff;
}
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
}
QComboBox::drop-down { border: none; }

QSplitter::handle { background: #333; }
QScrollBar:vertical {
    background: #202028;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #444;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #555; }
"""

LIGHT_QSS = ""



def apply_theme(app, theme: str):
    if theme == "dark":
        app.setStyleSheet(DARK_QSS)
    else:
        app.setStyleSheet(LIGHT_QSS)