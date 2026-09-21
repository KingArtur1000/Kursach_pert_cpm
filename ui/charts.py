from collections import defaultdict
import math

import networkx as nx
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel
)

from model import build_graph


CRITICAL_BG = QColor("#5a2a2a")


class ResultsTable(QWidget):
    """Таблица результатов CPM + строка PERT-информации."""

    COLUMNS = ["ID", "Название", "Длит.", "ES", "EF",
               "LS", "LF", "TF", "FF", "Крит."]

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.info = QLabel("")
        self.info.setTextFormat(Qt.RichText)
        self.info.setStyleSheet(
            "background:#2a2a3a; padding:6px 10px; border-radius:4px;"
        )
        self.info.setVisible(False)
        layout.addWidget(self.info)

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
            values = [
                r.task_id, r.name, f"{r.duration:.2f}".rstrip("0").rstrip("."),
                f"{r.es:g}", f"{r.ef:g}", f"{r.ls:g}",
                f"{r.lf:g}", f"{r.tf:g}", f"{r.ff:g}",
                "★" if r.is_critical else "",
            ]
            for c, v in enumerate(values):
                item = QTableWidgetItem(v)
                if r.is_critical:
                    item.setBackground(CRITICAL_BG)
                self.table.setItem(row, c, item)

    def set_info(self, html: str):
        self.info.setText(html)
        self.info.setVisible(bool(html))

    def clear(self):
        self.table.setRowCount(0)
        self.set_info("")


class GanttChart(QWidget):
    def __init__(self):
        super().__init__()
        self.fig = Figure(figsize=(8, 5), tight_layout=True)
        self.fig.patch.set_facecolor("#181820")
        self.canvas = FigureCanvasQTAgg(self.fig)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def plot(self, result):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#181820")
        for spine in ax.spines.values():
            spine.set_color("#444")
        ax.tick_params(colors="#cccccc")
        ax.xaxis.label.set_color("#cccccc")
        ax.title.set_color("#ffffff")

        tasks = sorted(result.tasks.values(), key=lambda r: (r.es, r.task_id))
        n = len(tasks)

        for i, r in enumerate(tasks):
            y = n - i - 1
            color = "#ff6b6b" if r.is_critical else "#4dabf7"
            ax.barh(y, r.duration, left=r.es, height=0.55,
                    color=color, edgecolor="white", linewidth=0.6, zorder=3)
            if r.tf > 0:
                ax.barh(y, r.tf, left=r.ef, height=0.55,
                        color="#666666", edgecolor="#aaaaaa",
                        linestyle="--", zorder=2, alpha=0.6)
            ax.text(r.es - 0.4, y, f"{r.task_id} — {r.name}",
                    va="center", ha="right", fontsize=9, color="#dddddd")

        ax.set_yticks([])
        ax.set_xlabel("Время (дни)")
        ax.set_xlim(-max(5, n), result.duration + 3)
        ax.set_ylim(-0.5, n - 0.5)
        ax.grid(axis="x", linestyle=":", alpha=0.35, zorder=0)

        ax.axvline(result.duration, color="#4dff88",
                   linestyle="--", linewidth=1.5)
        ax.text(result.duration + 0.2, n - 0.6,
                f"Длительность = {result.duration:.2f}".rstrip("0").rstrip("."),
                color="#4dff88", fontsize=10)

        legend = [
            mpatches.Patch(color="#ff6b6b", label="Критические работы"),
            mpatches.Patch(color="#4dabf7", label="Работы с резервом"),
            mpatches.Patch(color="#666666", label="Резерв времени"),
        ]
        leg = ax.legend(handles=legend, loc="lower right",
                        facecolor="#232330", edgecolor="#444")
        for text in leg.get_texts():
            text.set_color("#dddddd")
        ax.set_title("Диаграмма Ганта")
        self.canvas.draw()

    def clear(self):
        self.fig.clear()
        self.canvas.draw()


class NetworkChart(QWidget):
    def __init__(self):
        super().__init__()
        self.fig = Figure(figsize=(8, 5), tight_layout=True)
        self.fig.patch.set_facecolor("#181820")
        self.canvas = FigureCanvasQTAgg(self.fig)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def plot(self, tasks, result):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#181820")

        G = build_graph(tasks)

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

        node_colors = ["#ff6b6b" if n in critical else "#4dabf7"
                       for n in G.nodes()]
        edge_colors, edge_widths = [], []
        for u, v in G.edges():
            if u in critical and v in critical:
                edge_colors.append("#ff3b3b")
                edge_widths.append(2.8)
            else:
                edge_colors.append("#888888")
                edge_widths.append(1.0)

        labels = {n: f"{n}\n({result.tasks[n].duration:.2f}".rstrip("0")
                       .rstrip(".") + ")"
                  for n in G.nodes()}

        nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                               node_size=1600, ax=ax,
                               edgecolors="white", linewidths=1.2)
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors,
                               width=edge_widths, arrows=True,
                               arrowsize=20, ax=ax,
                               connectionstyle="arc3,rad=0.1")
        nx.draw_networkx_labels(G, pos, labels, font_size=10, ax=ax,
                                font_color="white")

        legend = [
            mpatches.Patch(color="#ff6b6b", label="Критическая работа"),
            mpatches.Patch(color="#4dabf7", label="Работа с резервом"),
        ]
        leg = ax.legend(handles=legend, loc="upper right",
                        facecolor="#232330", edgecolor="#444")
        for text in leg.get_texts():
            text.set_color("#dddddd")
        ax.set_title("Сетевой график проекта", color="white")
        ax.axis("off")
        self.canvas.draw()

    def clear(self):
        self.fig.clear()
        self.canvas.draw()