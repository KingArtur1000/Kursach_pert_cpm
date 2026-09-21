import math

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)

from model import Mode, optimize_crashing


class OptimizationPanel(QWidget):
    """Вкладка «Оптимизация время–стоимость»."""

    COLUMNS = ["Шаг", "Работа", "Сжатие (дн.)", "Стоимость"]

    def __init__(self):
        super().__init__()
        self._tasks = []
        self._mode = Mode.DETERMINISTIC
        self._current_duration = 0.0
        self._build_ui()

    def set_context(self, tasks, mode, current_duration):
        self._tasks = tasks
        self._mode = mode
        self._current_duration = current_duration
        self.target.setValue(max(1.0, round(current_duration - 1)))

    def _build_ui(self):
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("Текущая длительность:"))
        self.current_label = QLabel("—")
        top.addWidget(self.current_label)

        top.addSpacing(20)
        top.addWidget(QLabel("Целевая длительность:"))
        self.target = QDoubleSpinBox()
        self.target.setRange(0.1, 99999)
        self.target.setDecimals(1)
        self.target.setValue(10)
        top.addWidget(self.target)

        self.btn = QPushButton("  Оптимизировать")
        self.btn.clicked.connect(self._run)
        top.addWidget(self.btn)

        top.addStretch()
        layout.addLayout(top)

        self.summary = QLabel("")
        self.summary.setTextFormat(Qt.RichText)
        self.summary.setStyleSheet(
            "background:#2a2a3a; padding:8px 12px; border-radius:4px;"
        )
        layout.addWidget(self.summary)

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def attach_icon(self, ico):
        self.btn.setIcon(ico)

    def _run(self):
        if not self._tasks:
            QMessageBox.information(self, "Нет данных",
                                    "Сначала рассчитайте проект.")
            return

        target = self.target.value()
        try:
            crash = optimize_crashing(self._tasks, target, self._mode)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка оптимизации", str(e))
            return

        self.current_label.setText(f"{self._current_duration:.2f}"
                                   .rstrip("0").rstrip("."))

        # Агрегируем шаги по задачам
        agg = {}
        for s in crash.steps:
            if s.task_id not in agg:
                agg[s.task_id] = [0.0, 0.0]
            agg[s.task_id][0] += s.days
            agg[s.task_id][1] += s.cost

        self.table.setRowCount(0)
        for i, (tid, (days, cost)) in enumerate(agg.items(), start=1):
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(i)))
            self.table.setItem(r, 1, QTableWidgetItem(tid))
            self.table.setItem(r, 2, QTableWidgetItem(f"{days:g}"))
            self.table.setItem(r, 3, QTableWidgetItem(f"{cost:.2f}"))

        reachable = crash.final_duration <= target + 1e-6
        status = ("<span style='color:#4dff88'>цель достигнута</span>"
                  if reachable
                  else "<span style='color:#ff6b6b'>цель недостижима "
                       "(упёрлись в минимумы)</span>")

        self.summary.setText(
            f"<b>Итог оптимизации.</b> "
            f"Начальная длительность: {self._current_duration:.2f}".rstrip("0").rstrip(".") +
            f"  →  конечная: <b>{crash.final_duration:.2f}".rstrip("0").rstrip(".") +
            f"</b> дн.<br>"
            f"Суммарная стоимость ускорения: <b>{crash.total_cost:.2f}</b><br>"
            f"Статус: {status}"
        )