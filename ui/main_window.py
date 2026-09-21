import csv
import json
import math

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QTabWidget,
    QToolBar, QFileDialog, QMessageBox, QStatusBar, QComboBox, QLabel
)

from model import Task, Mode, calculate
from ui.task_editor import TaskEditor
from ui.charts import ResultsTable, GanttChart, NetworkChart
from ui.optimization import OptimizationPanel
import icons
import theme as theme_module


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PERT/CPM — Сетевое планирование проекта")
        self.resize(1360, 860)
        self.result = None
        self.current_theme = "dark"

        self._build_ui()
        self._build_menu()
        self._build_toolbar()
        self._apply_icons()
        self._load_sample()
        # Распространить стартовую тему на все графики
        for w in (self.results_table, self.gantt, self.network):
            w.set_theme(self.current_theme)

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        splitter = QSplitter(Qt.Vertical)

        self.editor = TaskEditor()
        splitter.addWidget(self.editor)

        self.tabs = QTabWidget()
        self.results_table = ResultsTable()
        self.gantt = GanttChart()
        self.network = NetworkChart()
        self.optimization = OptimizationPanel()

        self.tabs.addTab(self.results_table, "Результаты")
        self.tabs.addTab(self.gantt, "Диаграмма Ганта")
        self.tabs.addTab(self.network, "Сетевой график")
        self.tabs.addTab(self.optimization, "Оптимизация")
        splitter.addWidget(self.tabs)

        splitter.setSizes([320, 540])
        layout.addWidget(splitter)
        self.setCentralWidget(central)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Готово")

    def _build_menu(self):
        menu = self.menuBar()

        # ---- Файл ----
        file_menu = menu.addMenu("Файл")

        self.act_new = QAction("Новый проект", self)
        self.act_new.setShortcut(QKeySequence.New)
        self.act_new.triggered.connect(self._new_project)
        file_menu.addAction(self.act_new)

        self.act_open = QAction("Открыть...", self)
        self.act_open.setShortcut(QKeySequence.Open)
        self.act_open.triggered.connect(self._open_project)
        file_menu.addAction(self.act_open)

        self.act_save = QAction("Сохранить...", self)
        self.act_save.setShortcut(QKeySequence.Save)
        self.act_save.triggered.connect(self._save_project)
        file_menu.addAction(self.act_save)

        file_menu.addSeparator()

        self.act_export = QAction("Экспорт результатов в CSV...", self)
        self.act_export.triggered.connect(self._export_csv)
        file_menu.addAction(self.act_export)

        file_menu.addSeparator()

        self.act_quit = QAction("Выход", self)
        self.act_quit.setShortcut(QKeySequence.Quit)
        self.act_quit.triggered.connect(self.close)
        file_menu.addAction(self.act_quit)

        # ---- Расчёт ----
        calc_menu = menu.addMenu("Расчёт")

        self.act_calc = QAction("Выполнить расчёт", self)
        self.act_calc.setShortcut("F5")
        self.act_calc.triggered.connect(self._calculate)
        calc_menu.addAction(self.act_calc)

        # ---- Вид ----
        view_menu = menu.addMenu("Вид")

        self.act_theme = QAction("Переключить тему", self)
        self.act_theme.setShortcut("Ctrl+T")
        self.act_theme.triggered.connect(self._toggle_theme)
        view_menu.addAction(self.act_theme)

        # ---- Справка ----
        help_menu = menu.addMenu("Справка")

        self.act_about = QAction("О программе", self)
        self.act_about.triggered.connect(self._about)
        help_menu.addAction(self.act_about)

        # ---- Регистрируем все действия в окне,
        #      чтобы shortcuts работали при фокусе на любом виджете ----
        for act in (self.act_new, self.act_open, self.act_save,
                    self.act_export, self.act_quit, self.act_calc,
                    self.act_theme, self.act_about):
            act.setShortcutContext(Qt.WindowShortcut)
            self.addAction(act)

    def _build_toolbar(self):
        tb = QToolBar("Панель инструментов")
        tb.setMovable(False)
        tb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(tb)

        # Используем уже существующие QAction из меню — никаких дублей
        tb.addAction(self.act_calc)
        tb.addSeparator()

        self.act_add = QAction("Добавить", self)
        self.act_add.triggered.connect(self.editor.add_row)
        tb.addAction(self.act_add)

        self.act_rm = QAction("Удалить", self)
        self.act_rm.triggered.connect(self.editor.remove_selected)
        tb.addAction(self.act_rm)

        tb.addSeparator()
        tb.addAction(self.act_open)
        tb.addAction(self.act_save)
        tb.addAction(self.act_export)
        tb.addSeparator()

        tb.addWidget(QLabel("  Режим: "))
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Детерминированный (CPM)",
                                Mode.DETERMINISTIC)
        self.mode_combo.addItem("Вероятностный (PERT)", Mode.PERT)
        self.mode_combo.currentIndexChanged.connect(self._calculate)
        tb.addWidget(self.mode_combo)

        tb.addSeparator()
        tb.addAction(self.act_theme)

    def _apply_icons(self):
        color = "#e6e6e6"
        self.act_calc.setIcon(icons.icon("play", color))
        self.act_add.setIcon(icons.icon("plus", color))
        self.act_rm.setIcon(icons.icon("minus", color))
        self.act_open.setIcon(icons.icon("folder", color))
        self.act_save.setIcon(icons.icon("save", color))
        self.act_export.setIcon(icons.icon("export", color))
        self.act_theme.setIcon(icons.icon("moon", color))

        self.editor.attach_icons(icons.icon("plus", color),
                                 icons.icon("minus", color))
        self.optimization.attach_icon(icons.icon("gear", color))

    # --------------------------------------------------------------- данные
    def _load_sample(self):
        sample = [
            Task("A", "Анализ требований", 3, [],
                 o=2, m=3, p=5, crash_duration=2, cost_per_day=100),
            Task("B", "Архитектура", 4, ["A"],
                 o=3, m=4, p=6, crash_duration=2, cost_per_day=200),
            Task("C", "Дизайн UI", 2, ["A"],
                 o=1, m=2, p=4, crash_duration=1, cost_per_day=150),
            Task("D", "Бэкенд", 5, ["B"],
                 o=4, m=5, p=7, crash_duration=3, cost_per_day=250),
            Task("E", "Фронтенд", 4, ["B", "C"],
                 o=3, m=4, p=6, crash_duration=2, cost_per_day=200),
            Task("F", "Интеграция API", 3, ["D"],
                 o=2, m=3, p=4, crash_duration=2, cost_per_day=150),
            Task("G", "Верстка", 2, ["E"],
                 o=1, m=2, p=3, crash_duration=1, cost_per_day=100),
            Task("H", "Тестирование", 3, ["F", "G"],
                 o=2, m=3, p=5, crash_duration=2, cost_per_day=180),
            Task("I", "Развертывание", 2, ["H"],
                 o=1, m=2, p=3, crash_duration=1, cost_per_day=100),
            Task("J", "Документация", 1, ["I"],
                 o=1, m=1, p=2, crash_duration=1, cost_per_day=50),
        ]
        self.editor.set_tasks(sample)
        self._calculate()

    # --------------------------------------------------------------- режим
    def _current_mode(self) -> Mode:
        return self.mode_combo.currentData()

    # ------------------------------------------------------------- расчёт
    def _calculate(self):
        try:
            tasks = self.editor.get_tasks()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e))
            return

        if not tasks:
            QMessageBox.warning(self, "Ошибка", "Список работ пуст.")
            return

        mode = self._current_mode()
        try:
            self.result = calculate(tasks, mode)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка расчёта", str(e))
            return

        # Обновить представления
        self.results_table.update_results(self.result)
        self.gantt.plot(self.result)
        self.network.plot(tasks, self.result)
        self.optimization.set_context(tasks, mode, self.result.duration)

        # PERT-инфо
        if mode == Mode.PERT:
            dur = self.result.duration
            sd = self.result.stdev
            prob95 = self._norm_cdf((dur + 1.645 * sd - dur) / sd) if sd > 0 else 1.0
            self.results_table.set_info(
                f"<b>PERT-режим.</b> Ожидаемая длительность: "
                f"<b>{dur:.2f}</b> дн., σ = <b>{sd:.2f}</b>. "
                f"С вероятностью 95% проект завершится не позже "
                f"<b>{dur + 1.645 * sd:.2f}</b> дн. "
                f"(<i>среднеквадратичное отклонение учитывает "
                f"неопределённость оценок O/M/P</i>)"
            )
        else:
            self.results_table.set_info("")

        self.status.showMessage(
            f"Длительность проекта: {self.result.duration:.2f}".rstrip("0").rstrip(".") +
            f" дн.   |   Критический путь: {' → '.join(self.result.critical_path)}"
        )

    @staticmethod
    def _norm_cdf(x):
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    # ------------------------------------------------------------- действия
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

        data = []
        for t in tasks:
            data.append({
                "id": t.task_id, "name": t.name, "duration": t.duration,
                "preds": t.predecessors,
                "o": t.o, "m": t.m, "p": t.p,
                "crash_duration": t.crash_duration,
                "cost_per_day": t.cost_per_day,
            })
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

        tasks = [Task(
            task_id=d["id"], name=d["name"],
            duration=float(d["duration"]),
            predecessors=list(d.get("preds", [])),
            o=d.get("o"), m=d.get("m"), p=d.get("p"),
            crash_duration=d.get("crash_duration"),
            cost_per_day=d.get("cost_per_day"),
        ) for d in data]
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

    # ------------------------------------------------------------- тема
    def _toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        theme_module.apply_theme(QApplication.instance(), self.current_theme)

        # Иконка в тулбаре: в тёмной теме — солнце (включить светлую),
        # в светлой — луна.
        color = "#1a1a1a" if self.current_theme == "light" else "#e6e6e6"
        self.act_theme.setIcon(icons.icon(
            "sun" if self.current_theme == "dark" else "moon", color))

        # Иконки кнопок редактора и оптимизации
        self.editor.attach_icons(icons.icon("plus", color),
                                 icons.icon("minus", color))
        self.optimization.attach_icon(icons.icon("gear", color))

        for act, name in (
                (self.act_calc, "play"),
                (self.act_add, "plus"),
                (self.act_rm, "minus"),
                (self.act_open, "folder"),
                (self.act_save, "save"),
                (self.act_export, "export"),
        ):
            act.setIcon(icons.icon(name, color))

        # Обновляем только цвета — без пересчёта
        for w in (self.results_table, self.gantt, self.network):
            w.set_theme(self.current_theme)

        # Перерисовываем графики на уже готовом self.result
        if self.result is not None:
            try:
                self.gantt.plot(self.result)
                self.network.plot(self.editor.get_tasks(), self.result)
            except Exception:
                pass
        # Таблица результатов перекрасится сама:
        # ResultsTable.set_theme уже вызывает update_results(self.result)

    def _about(self):
        QMessageBox.about(
            self, "О программе",
            "<h3>PERT/CPM — Сетевое планирование</h3>"
            "<p>Программная реализация математических моделей "
            "сетевого планирования:</p>"
            "<ul>"
            "<li>метод критического пути (CPM);</li>"
            "<li>вероятностная модель PERT (оценки O, M, P);</li>"
            "<li>оптимизация «время — стоимость» (crashing).</li>"
            "</ul>"
            "<p><b>Стек:</b> Python, PySide6, NetworkX, Matplotlib.</p>"
            "<p>Курсовая работа по системному анализу.</p>"
        )