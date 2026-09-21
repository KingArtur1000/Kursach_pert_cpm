"""
Математическая модель сетевого планирования (CPM).

Обозначения:
    ES (Early Start)  — раннее начало работы
    EF (Early Finish) — раннее окончание работы
    LS (Late Start)   — позднее начало работы
    LF (Late Finish)  — позднее окончание работы
    TF (Total Float)  — полный резерв времени
    FF (Free Float)   — свободный резерв времени
"""

from dataclasses import dataclass, field
from typing import Dict, List
import networkx as nx


@dataclass
class TaskResult:
    """Результат расчёта по одной работе."""
    task_id: str
    duration: int
    predecessors: List[str] = field(default_factory=list)
    successors: List[str] = field(default_factory=list)
    es: int = 0
    ef: int = 0
    ls: int = 0
    lf: int = 0
    tf: int = 0   # полный резерв
    ff: int = 0   # свободный резерв

    @property
    def is_critical(self) -> bool:
        return self.tf == 0


@dataclass
class ProjectResult:
    """Результат расчёта всего проекта."""
    tasks: Dict[str, TaskResult]
    duration: int
    critical_path: List[str]


def build_graph(tasks: Dict[str, tuple]) -> nx.DiGraph:
    """Строит ориентированный граф зависимостей между работами."""
    G = nx.DiGraph()
    for task_id, (duration, preds) in tasks.items():
        G.add_node(task_id, duration=duration)
        for p in preds:
            G.add_edge(p, task_id)
    return G


def calculate(tasks: Dict[str, tuple]) -> ProjectResult:
    """Основной расчёт CPM."""
    G = build_graph(tasks)
    order = list(nx.topological_sort(G))

    results: Dict[str, TaskResult] = {}
    for t in order:
        duration, preds = tasks[t]
        results[t] = TaskResult(
            task_id=t,
            duration=duration,
            predecessors=list(G.predecessors(t)),
            successors=list(G.successors(t)),
        )

    # ---------- Прямой проход (forward pass) ----------
    for t in order:
        r = results[t]
        if r.predecessors:
            r.es = max(results[p].ef for p in r.predecessors)
        else:
            r.es = 0
        r.ef = r.es + r.duration

    project_duration = max(r.ef for r in results.values())

    # ---------- Обратный проход (backward pass) ----------
    for t in reversed(order):
        r = results[t]
        if r.successors:
            r.lf = min(results[s].ls for s in r.successors)
        else:
            r.lf = project_duration
        r.ls = r.lf - r.duration

    # ---------- Резервы ----------
    for t in order:
        r = results[t]
        r.tf = r.ls - r.es
        if r.successors:
            r.ff = min(results[s].es for s in r.successors) - r.ef
        else:
            r.ff = project_duration - r.ef

    # ---------- Критический путь ----------
    # Работы с нулевым полным резервом, упорядоченные по ES
    critical = sorted(
        [t for t, r in results.items() if r.is_critical],
        key=lambda t: results[t].es,
    )

    return ProjectResult(
        tasks=results,
        duration=project_duration,
        critical_path=critical,
    )


def to_table(result: ProjectResult, names: Dict[str, str] | None = None):
    """Превращает результат в таблицу (список словарей) для вывода/экспорта."""
    rows = []
    for t, r in sorted(result.tasks.items(), key=lambda x: x[1].es):
        rows.append({
            "ID": t,
            "Работа": names.get(t, t) if names else t,
            "Длит.": r.duration,
            "ES": r.es,
            "EF": r.ef,
            "LS": r.ls,
            "LF": r.lf,
            "TF": r.tf,
            "FF": r.ff,
            "Крит.": "★" if r.is_critical else "",
        })
    return rows