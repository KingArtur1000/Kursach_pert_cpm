from collections import defaultdict

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

import theme
from model import build_graph


CRITICAL_BG_DARK = QColor("#5a2a2a")
CRITICAL_BG_LIGHT = QColor("#fde2e2")


# =====================================================================
#  Таблица результатов
# =====================================================================

class ResultsTable(QWidget):
    COLUMNS = ["ID", "Название", "Длит.", "ES", "EF",
               "LS", "LF", "TF", "FF", "Крит."]

    def __init__(self):
        super().__init__()
        self.current_theme = "dark"
        self.result = None
        layout = QVBoxLayout(self)

        self.info = QLabel("")
        self.info.setTextFormat(Qt.RichText)
        self.info.setVisible(False)
        layout.addWidget(self.info)

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.set_theme("dark")

    def set_theme(self, name):
        self.current_theme = name
        if name == "dark":
            self.info.setStyleSheet(
                "background:#2a2a3a; padding:6px 10px; border-radius:4px;"
                "color:#e6e6e6;"
            )
        else:
            self.info.setStyleSheet(
                "background:#eef1f7; padding:6px 10px; border-radius:4px;"
                "color:#1a1a1a; border:1px solid #d0d3dc;"
            )
        if self.result is not None:
            self.update_results(self.result)

    def update_results(self, result):
        self.result = result
        bg = (CRITICAL_BG_DARK if self.current_theme == "dark"
              else CRITICAL_BG_LIGHT)
        fg = (QColor("#ffffff") if self.current_theme == "dark"
              else QColor("#7a1f1f"))

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
                    item.setBackground(bg)
                    item.setForeground(fg)
                self.table.setItem(row, c, item)

    def set_info(self, html: str):
        self.info.setText(html)
        self.info.setVisible(bool(html))

    def clear(self):
        self.result = None
        self.table.setRowCount(0)
        self.set_info("")


# =====================================================================
#  База для графиков
# =====================================================================

class _ThemedChart(QWidget):
    """Общая база для диаграммы Ганта и сетевого графика."""

    def __init__(self, figsize=(8, 5)):
        super().__init__()
        self.current_theme = "dark"
        self.pal = theme.palette("dark")
        self.fig = Figure(figsize=figsize)
        self.fig.set_layout_engine("none")
        self.canvas = FigureCanvasQTAgg(self.fig)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

    def set_theme(self, name):
        self.current_theme = name
        self.pal = theme.palette(name)

    def clear(self):
        self.fig.clear()
        self.canvas.draw()


# =====================================================================
#  Диаграмма Ганта
# =====================================================================

class GanttChart(_ThemedChart):

    def plot(self, result):
        pal = self.pal
        self.fig.clear()
        self.fig.set_layout_engine("none")
        self.fig.patch.set_facecolor(pal["fig_bg"])

        ax = self.fig.add_subplot(111)
        ax.set_facecolor(pal["ax_bg"])
        for spine in ax.spines.values():
            spine.set_color(pal["spine"])
        ax.tick_params(colors=pal["subtext"])
        ax.xaxis.label.set_color(pal["subtext"])

        tasks = sorted(result.tasks.values(), key=lambda r: (r.es, r.task_id))
        n = max(1, len(tasks))

        for i, r in enumerate(tasks):
            y = n - i - 1
            color = pal["critical"] if r.is_critical else pal["normal"]
            ax.barh(y, r.duration, left=r.es, height=0.55,
                    color=color, edgecolor=pal["node_edge"],
                    linewidth=0.6, zorder=3)
            if r.tf > 0:
                ax.barh(y, r.tf, left=r.ef, height=0.55,
                        color=pal["reserve"], edgecolor=pal["reserve_edge"],
                        linestyle="--", zorder=2, alpha=0.7)
            ax.text(-0.012, y, f"{r.task_id} — {r.name}",
                    transform=ax.get_yaxis_transform(),
                    va="center", ha="right", fontsize=9,
                    color=pal["text"], clip_on=False)

        ax.set_yticks([])
        ax.set_xlabel("Время (дни)", color=pal["subtext"], labelpad=6)
        ax.set_xlim(0, max(result.duration + 1.5, 5))
        # Запас сверху: бейдж «Длительность» висит в пустой полосе
        ax.set_ylim(-0.6, n + 0.9)
        ax.grid(axis="x", linestyle=":", alpha=0.35,
                color=pal["grid"], zorder=0)

        ax.axvline(result.duration, color=pal["duration"],
                   linestyle="--", linewidth=1.5, zorder=4)

        dur_text = (f"Длительность = {result.duration:.2f}"
                    .rstrip("0").rstrip("."))
        ax.text(0.015, 0.985, dur_text,
                transform=ax.transAxes,
                ha="left", va="top", fontsize=10,
                color=pal["duration"], zorder=6,
                bbox=dict(boxstyle="round,pad=0.35",
                          facecolor=pal["fig_bg"],
                          edgecolor=pal["duration"], linewidth=1.0,
                          alpha=0.95))

        ax.set_title("Диаграмма Ганта", color=pal["text"], pad=14)

        # ---- Легенда в координатах ФИГУРЫ, самый низ ----
        legend = [
            mpatches.Patch(color=pal["critical"], label="Критические работы"),
            mpatches.Patch(color=pal["normal"],   label="Работы с резервом"),
            mpatches.Patch(color=pal["reserve"],  label="Резерв времени"),
        ]
        leg = self.fig.legend(
            handles=legend,
            loc="lower left",
            bbox_to_anchor=(0.01, 0.015),
            ncol=3,
            frameon=True,
            facecolor=pal["legend_bg"],
            edgecolor=pal["legend_edge"],
            fontsize=9,
        )
        for text in leg.get_texts():
            text.set_color(pal["text"])

        self.fig.subplots_adjust(
            left=0.26, right=0.98, top=0.90, bottom=0.20,
        )
        self.canvas.draw()


# =====================================================================
#  Сетевой график
# =====================================================================

class NetworkChart(_ThemedChart):

    def plot(self, tasks, result):
        pal = self.pal
        self.fig.clear()
        self.fig.set_layout_engine("none")
        self.fig.patch.set_facecolor(pal["fig_bg"])

        ax = self.fig.add_subplot(111)
        ax.set_facecolor(pal["ax_bg"])

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

        node_colors = [pal["node_critical"] if n in critical
                       else pal["node_normal"] for n in G.nodes()]
        edge_colors, edge_widths = [], []
        for u, v in G.edges():
            if u in critical and v in critical:
                edge_colors.append(pal["edge_critical"])
                edge_widths.append(2.8)
            else:
                edge_colors.append(pal["edge_normal"])
                edge_widths.append(1.0)

        labels = {}
        for n in G.nodes():
            d = result.tasks[n].duration
            labels[n] = f"{n}\n({d:.2f}".rstrip("0").rstrip(".") + ")"

        nx.draw_networkx_nodes(
            G, pos, node_color=node_colors, node_size=1600, ax=ax,
            edgecolors=pal["node_edge"], linewidths=1.2,
        )
        nx.draw_networkx_edges(
            G, pos, edge_color=edge_colors, width=edge_widths,
            arrows=True, arrowsize=20, ax=ax,
            connectionstyle="arc3,rad=0.1",
        )
        nx.draw_networkx_labels(G, pos, labels, font_size=10, ax=ax,
                                font_color="white")

        ax.set_title("Сетевой график проекта",
                     color=pal["text"], pad=14)
        ax.axis("off")

        # ---- Легенда в координатах ФИГУРЫ, ПОД графом ----
        legend = [
            mpatches.Patch(color=pal["node_critical"],
                           label="Критическая работа"),
            mpatches.Patch(color=pal["node_normal"],
                           label="Работа с резервом"),
        ]
        leg = self.fig.legend(
            handles=legend,
            loc="lower center",
            bbox_to_anchor=(0.5, 0.02),
            ncol=2,
            frameon=True,
            facecolor=pal["legend_bg"],
            edgecolor=pal["legend_edge"],
            fontsize=10,
        )
        for text in leg.get_texts():
            text.set_color(pal["text"])

        self.fig.subplots_adjust(
            left=0.03, right=0.97, top=0.90, bottom=0.12,
        )
        self.canvas.draw()