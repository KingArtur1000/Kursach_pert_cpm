from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QLabel
)
from model import Task


class TaskEditor(QWidget):
    """
    Редактируемая таблица работ.

    Столбцы:
      0 ID | 1 Название | 2 Длительность |
      3 O | 4 M | 5 P | 6 Предшественники |
      7 Мин.длит. | 8 Цена/день
    """

    COLUMNS = [
        "ID", "Название", "Длит.",
        "O (опт.)", "M (реал.)", "P (песс.)",
        "Предшественники",
        "Мин.длит.", "Цена/день",
    ]

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        header = QLabel(
            "<b>Работы проекта</b> — "
            "<span style='color:#999'>столбцы O/M/P используются в PERT-режиме, "
            "Мин.длит./Цена — при оптимизации «время–стоимость»</span>"
        )
        header.setTextFormat(Qt.RichText)
        layout.addWidget(header)

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setAlternatingRowColors(True)
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        for c in (2, 3, 4, 5, 7, 8):
            hh.setSectionResizeMode(c, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(6, QHeaderView.Stretch)
        layout.addWidget(self.table)

        btns = QHBoxLayout()
        add = QPushButton("  Добавить работу")
        add.clicked.connect(self.add_row)
        rm = QPushButton("  Удалить выбранные")
        rm.clicked.connect(self.remove_selected)
        clear = QPushButton("  Очистить")
        clear.clicked.connect(lambda: self.set_tasks([]))

        btns.addWidget(add)
        btns.addWidget(rm)
        btns.addWidget(clear)
        btns.addStretch()
        layout.addLayout(btns)

        # даём главному окну возможность подцепить иконки
        self._buttons = {"add": add, "rm": rm, "clear": clear}

    def attach_icons(self, add_icon, rm_icon):
        self._buttons["add"].setIcon(add_icon)
        self._buttons["rm"].setIcon(rm_icon)

    # ---------------------------------------------------------- строки
    def add_row(self):
        r = self.table.rowCount()
        self.table.insertRow(r)

        used = {self.table.item(i, 0).text()
                for i in range(self.table.rowCount())
                if self.table.item(i, 0)}
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if letter not in used:
                tid = letter
                break
        else:
            tid = f"T{r + 1}"

        self._set(r, 0, tid)
        self._set(r, 1, f"Работа {tid}")
        self._set(r, 2, "1")
        self._set(r, 3, "")
        self._set(r, 4, "")
        self._set(r, 5, "")
        self._set(r, 6, "")
        self._set(r, 7, "")
        self._set(r, 8, "")

    def remove_selected(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()},
                      reverse=True)
        for r in rows:
            self.table.removeRow(r)

    def _set(self, r, c, val):
        self.table.setItem(r, c, QTableWidgetItem(str(val)))

    # ---------------------------------------------------------- данные
    def set_tasks(self, tasks):
        self.table.setRowCount(0)
        for t in tasks:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self._set(r, 0, t.task_id)
            self._set(r, 1, t.name)
            self._set(r, 2, f"{t.duration:g}")
            self._set(r, 3, "" if t.o is None else f"{t.o:g}")
            self._set(r, 4, "" if t.m is None else f"{t.m:g}")
            self._set(r, 5, "" if t.p is None else f"{t.p:g}")
            self._set(r, 6, ", ".join(t.predecessors))
            self._set(r, 7, "" if t.crash_duration is None
                      else f"{t.crash_duration:g}")
            self._set(r, 8, "" if t.cost_per_day is None
                      else f"{t.cost_per_day:g}")

    def _cell(self, r, c):
        it = self.table.item(r, c)
        return it.text().strip() if it else ""

    @staticmethod
    def _opt_float(s):
        s = s.replace(",", ".")
        if s == "":
            return None
        return float(s)

    def get_tasks(self):
        tasks = []
        ids = set()
        for r in range(self.table.rowCount()):
            tid = self._cell(r, 0)
            if not tid:
                continue
            if tid in ids:
                raise ValueError(f"Дублирующийся ID работы: {tid}")
            ids.add(tid)

            name = self._cell(r, 1) or tid

            try:
                duration = float(self._cell(r, 2).replace(",", ".") or "1")
                if duration <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError(f"Некорректная длительность для {tid}")

            try:
                o = self._opt_float(self._cell(r, 3))
                m = self._opt_float(self._cell(r, 4))
                p = self._opt_float(self._cell(r, 5))
            except ValueError:
                raise ValueError(f"Некорректные PERT-оценки для {tid}")

            preds = [x.strip() for x in self._cell(r, 6).split(",")
                     if x.strip()]

            try:
                crash_d = self._opt_float(self._cell(r, 7))
                cost = self._opt_float(self._cell(r, 8))
            except ValueError:
                raise ValueError(f"Некорректные crash-параметры для {tid}")

            tasks.append(Task(
                task_id=tid, name=name, duration=duration,
                predecessors=preds,
                o=o, m=m, p=p,
                crash_duration=crash_d, cost_per_day=cost,
            ))

        for t in tasks:
            for p in t.predecessors:
                if p not in ids:
                    raise ValueError(
                        f"Работа {t.task_id} ссылается на несуществующего "
                        f"предшественника «{p}»")
        return tasks