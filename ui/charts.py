from collections import defaultdict

import networkx as nx
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
)

from model import build_graph


CRITICAL_BG = QColor("#ffe3e3")


class ResultsTable(QWidget):
    """Таблица с результатами расчёта CPM."""

    COLUMNS = ["ID", "Название", "Длит.", "ES", "EF",
               "LS", "LF", "TF", "FF", "Крит."]

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def update_results(self, result):
        self.table.setRowCount(0)
        for tid, r in sorted(result.tasks.items(), key=lambda x: x[1].es):
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = [r.task_id, r.name, f"{r.duration:g}",
                      f"{r.es:g}", f"{r.ef:g}", f"{r.ls:g}",
                      f"{r.lf:g}", f"{r.tf:g}", f"{r.ff:g}",
                      "★" if r.is_critical else ""]
            for c, v in enumerate(values):
                item = QTableWidgetItem(v)
                if r.is_critical:
                    item.setBackground(CRITICAL_BG)
                self.table.setItem(row, c, item)

    def clear(self):
        self.table.setRowCount(0)


class GanttChart(QWidget):
    """Диаграмма Ганта с выделением критических работ и резервов."""

    def __init__(self):
        super().__init__()
        self.fig = Figure(figsize=(8, 5), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.fig)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def plot(self, result):
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        tasks = sorted(result.tasks.values(), key=lambda r: (r.es, r.task_id))
        n = len(tasks)

        for i, r in enumerate(tasks):
            y = n - i - 1
            color = "#ff6b6b" if r.is_critical else "#4dabf7"
            ax.barh(y, r.duration, left=r.es, height=0.5,
                    color=color, edgecolor="black", zorder=3)
            if r.tf > 0:
                ax.barh(y, r.tf, left=r.ef, height=0.5,
                        color="#dddddd", edgecolor="gray",
                        linestyle="--", zorder=2)
            ax.text(r.es - 0.4, y, f"{r.task_id} — {r.name}",
                    va="center", ha="right", fontsize=9)

        ax.set_yticks([])
        ax.set_xlabel("Время (дни)")
        ax.set_xlim(-max(5, n), result.duration + 3)
        ax.set_ylim(-0.5, n - 0.5)
        ax.grid(axis="x", linestyle=":", alpha=0.5, zorder=0)

        ax.axvline(result.duration, color="green",
                   linestyle="--", linewidth=1.5)
        ax.text(result.duration + 0.2, n - 0.6,
                f"Длительность = {result.duration:g}",
                color="green", fontsize=10)

        legend = [
            mpatches.Patch(color="#ff6b6b", label="Критические работы"),
            mpatches.Patch(color="#4dabf7", label="Работы с резервом"),
            mpatches.Patch(color="#dddddd", label="Резерв времени"),
        ]
        ax.legend(handles=legend, loc="lower right")
        ax.set_title("Диаграмма Ганта")
        self.canvas.draw()

    def clear(self):
        self.fig.clear()
        self.canvas.draw()


class NetworkChart(QWidget):
    """Сетевой график проекта с выделением критического пути."""

    def __init__(self):
        super().__init__()
        self.fig = Figure(figsize=(8, 5), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.fig)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def plot(self, tasks, result):
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        G = build_graph(tasks)

        # Послойная укладка по уровням зависимостей
        levels = {}
        for t in nx.topological_sort(G):
            preds = list(G.predecessors(t))
            levels[t] = 0 if not preds else max(levels[p] for p in preds) + 1

        by_level = defaultdict(list)
        for t, lvl in levels.items():
            by_level[lvl].append(t)

        pos = {}
        for lvl, nodes in by_level.items():
            for i, node in enumerate(sorted(nodes)):
                pos[node] = (lvl, -i)

        critical = set(result.critical_path)

        node_colors = ["#ff6b6b" if n in critical else "#a0c4ff"
                       for n in G.nodes()]
        edge_colors, edge_widths = [], []
        for u, v in G.edges():
            if u in critical and v in critical:
                edge_colors.append("#d62728")
                edge_widths.append(2.5)
            else:
                edge_colors.append("#888888")
                edge_widths.append(1.0)

        labels = {n: f"{n}\n({G.nodes[n]['duration']:g})"
                  for n in G.nodes()}

        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                               node_size=1500, ax=ax,
                               edgecolors="black")
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors,
                               width=edge_widths, arrows=True,
                               arrowsize=20, ax=ax,
                               connectionstyle="arc3,rad=0.1")
        nx.draw_networkx_labels(G, pos, labels, font_size=10, ax=ax)

        legend = [
            mpatches.Patch(color="#ff6b6b", label="Критическая работа"),
            mpatches.Patch(color="#a0c4ff", label="Работа с резервом"),
        ]
        ax.legend(handles=legend, loc="upper right")
        ax.set_title("Сетевой график проекта")
        ax.axis("off")
        self.canvas.draw()

    def clear(self):
        self.fig.clear()
        self.canvas.draw()