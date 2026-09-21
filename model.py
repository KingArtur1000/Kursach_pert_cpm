"""
Математическая модель сетевого планирования (CPM).

Обозначения:
    ES / EF — раннее начало / окончание
    LS / LF — позднее начало / окончание
    TF      — полный резерв времени
    FF      — свободный резерв времени
"""

from dataclasses import dataclass, field
from typing import List, Dict
import networkx as nx


EPS = 1e-9


@dataclass
class Task:
    task_id: str
    name: str
    duration: float
    predecessors: List[str] = field(default_factory=list)


@dataclass
class TaskResult:
    task_id: str
    name: str
    duration: float
    predecessors: List[str]
    successors: List[str]
    es: float = 0
    ef: float = 0
    ls: float = 0
    lf: float = 0
    tf: float = 0
    ff: float = 0

    @property
    def is_critical(self) -> bool:
        return abs(self.tf) < EPS


@dataclass
class ProjectResult:
    tasks: Dict[str, TaskResult]
    duration: float
    critical_path: List[str]


def build_graph(tasks: List[Task]) -> nx.DiGraph:
    G = nx.DiGraph()
    for t in tasks:
        G.add_node(t.task_id, duration=t.duration, name=t.name)
    for t in tasks:
        for p in t.predecessors:
            if p in G:
                G.add_edge(p, t.task_id)
    return G


def calculate(tasks: List[Task]) -> ProjectResult:
    """Прямой и обратный проход + расчёт резервов."""
    G = build_graph(tasks)
    order = list(nx.topological_sort(G))

    results: Dict[str, TaskResult] = {}
    for t in tasks:
        results[t.task_id] = TaskResult(
            task_id=t.task_id,
            name=t.name,
            duration=t.duration,
            predecessors=list(G.predecessors(t.task_id)),
            successors=list(G.successors(t.task_id)),
        )

    # Прямой проход
    for tid in order:
        r = results[tid]
        r.es = max((results[p].ef for p in r.predecessors), default=0.0)
        r.ef = r.es + r.duration

    project_duration = max((r.ef for r in results.values()), default=0.0)

    # Обратный проход
    for tid in reversed(order):
        r = results[tid]
        r.lf = min((results[s].ls for s in r.successors),
                   default=project_duration)
        r.ls = r.lf - r.duration

    # Резервы
    for tid in order:
        r = results[tid]
        r.tf = r.ls - r.es
        if r.successors:
            r.ff = min(results[s].es for s in r.successors) - r.ef
        else:
            r.ff = project_duration - r.ef

    # Критический путь
    critical = sorted(
        [tid for tid, r in results.items() if r.is_critical],
        key=lambda t: results[t].es,
    )

    return ProjectResult(tasks=results,
                         duration=project_duration,
                         critical_path=critical)