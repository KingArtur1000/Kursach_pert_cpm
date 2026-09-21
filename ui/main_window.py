import csv
import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter, QTabWidget,
    QToolBar, QFileDialog, QMessageBox, QStatusBar
)

from model import Task, calculate
from ui.task_editor import TaskEditor
from ui.charts import ResultsTable, GanttChart, NetworkChart


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PERT/CPM — Сетевое планирование проекта")
        self.resize(1280, 820)
        self.result = None

        self._build_ui()
        self._build_menu()
        self._build_toolbar()
        self._load_sample()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(6, 6, 6, 6)

        splitter = QSplitter(Qt.Vertical)

        self.editor = TaskEditor()
        splitter.addWidget(self.editor)

        self.tabs = QTabWidget()
        self.results_table = ResultsTable()
        self.gantt = GanttChart()
        self.network = NetworkChart()
        self.tabs.addTab(self.results_table, "Результаты")
        self.tabs.addTab(self.gantt, "Диаграмма Ганта")
        self.tabs.addTab(self.network, "Сетевой график")
        splitter.addWidget(self.tabs)

        splitter.setSizes([320, 500])
        layout.addWidget(splitter)
        self.setCentralWidget(central)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Готово")

    def _build_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("Файл")

        new_action = QAction("Новый проект", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self._new_project)
        file_menu.addAction(new_action)

        open_action = QAction("Открыть...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self._open_project)
        file_menu.addAction(open_action)

        save_action = QAction("Сохранить...", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save_project)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        export_action = QAction("Экспорт результатов в CSV...", self)
        export_action.triggered.connect(self._export_csv)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("Выход", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Меню «Расчёт»
        calc_menu = menu.addMenu("Расчёт")
        calc_action = QAction("Выполнить расчёт", self)
        calc_action.setShortcut("F5")
        calc_action.triggered.connect(self._calculate)
        calc_menu.addAction(calc_action)

        # Меню «Справка»
        help_menu = menu.addMenu("Справка")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self._about)
        help_menu.addAction(about_action)

    def _build_toolbar(self):
        tb = QToolBar("Панель инструментов")
        tb.setMovable(False)
        tb.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.addToolBar(tb)

        def add(text, slot, shortcut=None):
            act = QAction(text, self)
            if shortcut:
                act.setShortcut(shortcut)
            act.triggered.connect(slot)
            tb.addAction(act)
            return act

        add("▶  Рассчитать", self._calculate, "F5")
        tb.addSeparator()
        add("➕  Добавить работу", self.editor.add_row)
        add("➖  Удалить выбранные", self.editor.remove_selected)
        tb.addSeparator()
        add("📂  Открыть", self._open_project)
        add("💾  Сохранить", self._save_project)
        add("📤  Экспорт CSV", self._export_csv)

    # --------------------------------------------------------------- Данные
    def _load_sample(self):
        sample = [
            Task("A", "Анализ требований", 3, []),
            Task("B", "Архитектура", 4, ["A"]),
            Task("C", "Дизайн UI", 2, ["A"]),
            Task("D", "Бэкенд", 5, ["B"]),
            Task("E", "Фронтенд", 4, ["B", "C"]),
            Task("F", "Интеграция API", 3, ["D"]),
            Task("G", "Верстка", 2, ["E"]),
            Task("H", "Тестирование", 3, ["F", "G"]),
            Task("I", "Развертывание", 2, ["H"]),
            Task("J", "Документация", 1, ["I"]),
        ]
        self.editor.set_tasks(sample)
        self._calculate()

    # ------------------------------------------------------------- Действия
    def _calculate(self):
        try:
            tasks = self.editor.get_tasks()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
            return

        if not tasks:
            QMessageBox.warning(self, "Ошибка", "Список работ пуст.")
            return

        try:
            self.result = calculate(tasks)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка расчёта", str(e))
            return

        self.results_table.update_results(self.result)
        self.gantt.plot(self.result)
        self.network.plot(tasks, self.result)

        self.status.showMessage(
            f"Длительность проекта: {self.result.duration:g} дн.   |   "
            f"Критический путь: {' → '.join(self.result.critical_path)}"
        )

    def _new_project(self):
        self.editor.set_tasks([])
        self.results_table.clear()
        self.gantt.clear()
        self.network.clear()
        self.result = None
        self.status.showMessage("Новый проект")

    def _save_project(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить проект", "", "JSON (*.json)")
        if not path:
            return
        try:
            tasks = self.editor.get_tasks()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
            return

        data = [{"id": t.task_id, "name": t.name,
                 "duration": t.duration, "preds": t.predecessors}
                for t in tasks]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.status.showMessage(f"Сохранено: {path}")

    def _open_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть проект", "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка чтения", str(e))
            return

        tasks = [Task(d["id"], d["name"], float(d["duration"]),
                      list(d.get("preds", []))) for d in data]
        self.editor.set_tasks(tasks)
        self._calculate()
        self.status.showMessage(f"Загружено: {path}")

    def _export_csv(self):
        if self.result is None:
            QMessageBox.information(self, "Нет данных",
                                    "Сначала выполните расчёт (F5).")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт результатов", "", "CSV (*.csv)")
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["ID", "Название", "Длительность",
                        "ES", "EF", "LS", "LF", "TF", "FF", "Крит."])
            for tid, r in sorted(self.result.tasks.items(),
                                 key=lambda x: x[1].es):
                w.writerow([r.task_id, r.name, r.duration,
                            r.es, r.ef, r.ls, r.lf, r.tf, r.ff,
                            "★" if r.is_critical else ""])
        self.status.showMessage(f"Экспортировано: {path}")

    def _about(self):
        QMessageBox.about(
            self, "О программе",
            "<h3>PERT/CPM — Сетевое планирование</h3>"
            "<p>Программная реализация математической модели "
            "сетевого планирования и анализа критического пути.</p>"
            "<p><b>Стек:</b> Python, PySide6, NetworkX, Matplotlib.</p>"
            "<p>Курсовая работа по системному анализу.</p>"
        )