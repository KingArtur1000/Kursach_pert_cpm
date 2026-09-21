from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QLabel
)
from model import Task


class TaskEditor(QWidget):
    """Редактируемая таблица работ проекта."""

    COLUMNS = ["ID", "Название", "Длительность (дн.)", "Предшественники"]

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        header = QLabel(
            "<b>Работы проекта</b><br>"
            "<span style='color:#666'>Отредактируйте таблицу и нажмите "
            "«▶ Рассчитать» на панели инструментов (или F5)</span>"
        )
        header.setTextFormat(Qt.RichText)
        layout.addWidget(header)

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setAlternatingRowColors(True)
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.table)

        btns = QHBoxLayout()
        add = QPushButton("Добавить работу")
        add.clicked.connect(self.add_row)
        rm = QPushButton("Удалить выбранные")
        rm.clicked.connect(self.remove_selected)
        clear = QPushButton("Очистить")
        clear.clicked.connect(lambda: self.set_tasks([]))

        btns.addWidget(add)
        btns.addWidget(rm)
        btns.addWidget(clear)
        btns.addStretch()
        layout.addLayout(btns)

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

        self.table.setItem(r, 0, QTableWidgetItem(tid))
        self.table.setItem(r, 1, QTableWidgetItem(f"Работа {tid}"))
        self.table.setItem(r, 2, QTableWidgetItem("1"))
        self.table.setItem(r, 3, QTableWidgetItem(""))

    def remove_selected(self):
        rows = sorted({i.row() for i in self.table.selectedIndexes()},
                      reverse=True)
        for r in rows:
            self.table.removeRow(r)

    def set_tasks(self, tasks):
        self.table.setRowCount(0)
        for t in tasks:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(t.task_id))
            self.table.setItem(r, 1, QTableWidgetItem(t.name))
            self.table.setItem(r, 2, QTableWidgetItem(f"{t.duration:g}"))
            self.table.setItem(r, 3,
                               QTableWidgetItem(", ".join(t.predecessors)))

    def get_tasks(self):
        tasks = []
        ids = set()
        for r in range(self.table.rowCount()):
            def cell(c):
                it = self.table.item(r, c)
                return it.text().strip() if it else ""

            tid = cell(0)
            if not tid:
                continue
            if tid in ids:
                raise ValueError(f"Дублирующийся ID работы: {tid}")
            ids.add(tid)

            name = cell(1) or tid
            try:
                duration = float(cell(2).replace(",", "."))
                if duration <= 0:
                    raise ValueError
            except ValueError:
                raise ValueError(f"Некорректная длительность для {tid}")

            preds = [p.strip() for p in cell(3).split(",") if p.strip()]
            tasks.append(Task(tid, name, duration, preds))

        for t in tasks:
            for p in t.predecessors:
                if p not in ids:
                    raise ValueError(
                        f"Работа {t.task_id} ссылается на несуществующего "
                        f"предшественника «{p}»")
        return tasks