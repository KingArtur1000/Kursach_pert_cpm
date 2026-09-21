"""Простые векторные иконки, рисуются в рантайме (без внешних файлов)."""

import math

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPen, QColor, QPainterPath


def _make_icon(draw_func, color: str = "#e0e0e0", size: int = 22) -> QIcon:
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    pen = QPen(QColor(color), 1.8, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    draw_func(p, size, color)
    p.end()
    return QIcon(pm)


# ---------------------------------------------------- Примитивы

def _play(p, m, color):
    path = QPainterPath()
    path.moveTo(m * 0.30, m * 0.20)
    path.lineTo(m * 0.30, m * 0.80)
    path.lineTo(m * 0.78, m * 0.50)
    path.closeSubpath()
    p.setBrush(QColor(color))
    p.drawPath(path)


def _plus(p, m, color):
    p.drawLine(QPointF(m * 0.5, m * 0.2), QPointF(m * 0.5, m * 0.8))
    p.drawLine(QPointF(m * 0.2, m * 0.5), QPointF(m * 0.8, m * 0.5))


def _minus(p, m, color):
    p.drawLine(QPointF(m * 0.2, m * 0.5), QPointF(m * 0.8, m * 0.5))


def _folder(p, m, color):
    path = QPainterPath()
    path.moveTo(m * 0.15, m * 0.30)
    path.lineTo(m * 0.42, m * 0.30)
    path.lineTo(m * 0.52, m * 0.42)
    path.lineTo(m * 0.85, m * 0.42)
    path.lineTo(m * 0.85, m * 0.78)
    path.lineTo(m * 0.15, m * 0.78)
    path.closeSubpath()
    p.drawPath(path)


def _save(p, m, color):
    p.drawRect(QRectF(m * 0.20, m * 0.20, m * 0.60, m * 0.60))
    p.drawRect(QRectF(m * 0.35, m * 0.20, m * 0.30, m * 0.22))
    p.drawRect(QRectF(m * 0.30, m * 0.55, m * 0.40, m * 0.25))


def _export(p, m, color):
    # стрелка вниз
    p.drawLine(QPointF(m * 0.5, m * 0.18), QPointF(m * 0.5, m * 0.65))
    path = QPainterPath()
    path.moveTo(m * 0.30, m * 0.48)
    path.lineTo(m * 0.50, m * 0.68)
    path.lineTo(m * 0.70, m * 0.48)
    p.drawPath(path)
    p.drawLine(QPointF(m * 0.20, m * 0.82), QPointF(m * 0.80, m * 0.82))


def _sun(p, m, color):
    p.drawEllipse(QPointF(m * 0.5, m * 0.5), m * 0.14, m * 0.14)
    for i in range(8):
        a = i * math.pi / 4
        x1 = m * 0.5 + math.cos(a) * m * 0.26
        y1 = m * 0.5 + math.sin(a) * m * 0.26
        x2 = m * 0.5 + math.cos(a) * m * 0.42
        y2 = m * 0.5 + math.sin(a) * m * 0.42
        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))


def _moon(p, m, color):
    outer = QPainterPath()
    outer.addEllipse(QRectF(m * 0.20, m * 0.20, m * 0.60, m * 0.60))
    inner = QPainterPath()
    inner.addEllipse(QRectF(m * 0.34, m * 0.14, m * 0.60, m * 0.60))
    p.setBrush(QColor(color))
    p.setPen(Qt.NoPen)
    p.drawPath(outer.subtracted(inner))


def _gear(p, m, color):
    # центральный круг
    p.drawEllipse(QPointF(m * 0.5, m * 0.5), m * 0.13, m * 0.13)
    # зубцы
    for i in range(8):
        a = i * math.pi / 4
        x1 = m * 0.5 + math.cos(a) * m * 0.28
        y1 = m * 0.5 + math.sin(a) * m * 0.28
        x2 = m * 0.5 + math.cos(a) * m * 0.42
        y2 = m * 0.5 + math.sin(a) * m * 0.42
        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))


# ---------------------------------------------------- Публичный API

_BUILDERS = {
    "play": _play,
    "plus": _plus,
    "minus": _minus,
    "folder": _folder,
    "save": _save,
    "export": _export,
    "sun": _sun,
    "moon": _moon,
    "gear": _gear,
}


def icon(name: str, color: str = "#e0e0e0") -> QIcon:
    return _make_icon(_BUILDERS[name], color=color)