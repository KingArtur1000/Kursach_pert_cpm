"""Визуализация результатов CPM: сетевой график и диаграмма Ганта."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

from data import TASK_NAMES
from model import ProjectResult, build_graph


def draw_network(tasks: dict, result: ProjectResult, save_path: str | None = None):
    """Рисует сетевой график с выделением критического пути."""
    G = build_graph(tasks)

    # Послойная укладка: уровень = максимальный ES среди предшественников
    pos = {}
    levels = {}
    for t in nx.topological_sort(G):
        preds = list(G.predecessors(t))
        levels[t] = 0 if not preds else max(levels[p] for p in preds) + 1

    # Раскладываем вершины по уровням
    from collections import defaultdict
    by_level = defaultdict(list)
    for t, lvl in levels.items():
        by_level[lvl].append(t)

    for lvl, nodes in by_level.items():
        for i, node in enumerate(sorted(nodes)):
            pos[node] = (lvl, -i)

    critical = set(result.critical_path)

    # Цвета рёбер и вершин
    node_colors = ["#ff6b6b" if n in critical else "#a0c4ff" for n in G.nodes()]
    edge_colors = []
    edge_widths = []
    for u, v in G.edges():
        if u in critical and v in critical:
            edge_colors.append("#d62728")
            edge_widths.append(2.5)
        else:
            edge_colors.append("#888888")
            edge_widths.append(1.0)

    fig, ax = plt.subplots(figsize=(12, 7))

    # Подписи вершин: ID + (длительность)
    labels = {n: f"{n}\n({G.nodes[n]['duration']})" for n in G.nodes()}

    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                           node_size=1600, ax=ax, edgecolors="black")
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
    ax.set_title("Сетевой график проекта", fontsize=14)
    ax.axis("off")

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()


def draw_gantt(result: ProjectResult, save_path: str | None = None):
    """Строит диаграмму Ганта с резервами."""
    tasks = sorted(result.tasks.values(), key=lambda r: (r.es, r.task_id))
    n = len(tasks)

    fig, ax = plt.subplots(figsize=(12, max(4, n * 0.6)))

    for i, r in enumerate(tasks):
        y = n - i - 1
        color = "#ff6b6b" if r.is_critical else "#4dabf7"

        # Основная полоса — от ES до EF
        ax.barh(y, r.duration, left=r.es, height=0.5,
                color=color, edgecolor="black", zorder=3)

        # Полоса резерва — от EF до LF
        if r.tf > 0:
            ax.barh(y, r.tf, left=r.ef, height=0.5,
                    color="#dddddd", edgecolor="gray",
                    linestyle="--", zorder=2)

        # Подпись
        name = TASK_NAMES.get(r.task_id, r.task_id)
        ax.text(r.es - 0.3, y, f"{r.task_id} — {name}",
                va="center", ha="right", fontsize=9)

    # Сетка по времени
    ax.set_yticks([])
    ax.set_xlabel("Время (дни)", fontsize=11)
    ax.set_xlim(-5, result.duration + 3)
    ax.set_ylim(-0.5, n - 0.5)
    ax.grid(axis="x", linestyle=":", alpha=0.5, zorder=0)

    # Линия длительности проекта
    ax.axvline(result.duration, color="green", linestyle="--", linewidth=1.5)
    ax.text(result.duration + 0.2, n - 0.6,
            f"Длительность = {result.duration}",
            color="green", fontsize=10)

    legend = [
        mpatches.Patch(color="#ff6b6b", label="Критические работы"),
        mpatches.Patch(color="#4dabf7", label="Работы с резервом"),
        mpatches.Patch(color="#dddddd", label="Резерв времени"),
    ]
    ax.legend(handles=legend, loc="lower right")

    ax.set_title("Диаграмма Ганта", fontsize=14)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()