"""
Математические модели сетевого планирования.

Реализовано:
  - CPM  — метод критического пути (детерминированные длительности);
  - PERT — вероятностные оценки (O, M, P), ожидаемая длительность и дисперсия;
  - Crashing — оптимизация «время — стоимость» (сжатие критических работ).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import networkx as nx


EPS = 1e-9


class Mode(str, Enum):
    DETERMINISTIC = "det"
    PERT = "pert"


@dataclass
class Task:
    task_id: str
    name: str
    duration: float = 1.0
    predecessors: List[str] = field(default_factory=list)

    # PERT-оценки
    o: Optional[float] = None
    m: Optional[float] = None
    p: Optional[float] = None

    # Crashing
    crash_duration: Optional[float] = None   # минимальная длительность
    cost_per_day: Optional[float] = None     # цена ускорения на 1 день


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
    variance: float = 0

    @property
    def is_critical(self) -> bool:
        return abs(self.tf) < EPS


@dataclass
class ProjectResult:
    tasks: Dict[str, TaskResult]
    duration: float
    critical_path: List[str]
    variance: float = 0.0

    @property
    def stdev(self) -> float:
        return self.variance ** 0.5


# ----------------------------------------------------------------- утилиты

def expected_duration(t: Task, mode: Mode) -> float:
    """Ожидаемая длительность с учётом режима."""
    if mode == Mode.PERT and None not in (t.o, t.m, t.p):
        return (t.o + 4 * t.m + t.p) / 6.0
    return t.duration


def task_variance(t: Task, mode: Mode) -> float:
    if mode == Mode.PERT and None not in (t.o, t.p):
        return ((t.p - t.o) / 6.0) ** 2
    return 0.0


def build_graph(tasks: List[Task]) -> nx.DiGraph:
    G = nx.DiGraph()
    for t in tasks:
        G.add_node(t.task_id)
    for t in tasks:
        for p in t.predecessors:
            if p in G:
                G.add_edge(p, t.task_id)
    return G


# ------------------------------------------------------------------- CPM

def calculate(tasks: List[Task],
              mode: Mode = Mode.DETERMINISTIC,
              durations_override: Optional[Dict[str, float]] = None
              ) -> ProjectResult:
    """Прямой/обратный проход + критические работы + резервы."""
    if not tasks:
        return ProjectResult(tasks={}, duration=0, critical_path=[])

    G = build_graph(tasks)
    order = list(nx.topological_sort(G))
    task_map = {t.task_id: t for t in tasks}

    # Длительности
    durations: Dict[str, float] = {}
    variances: Dict[str, float] = {}
    for t in tasks:
        if durations_override and t.task_id in durations_override:
            durations[t.task_id] = durations_override[t.task_id]
            variances[t.task_id] = 0.0
        else:
            durations[t.task_id] = expected_duration(t, mode)
            variances[t.task_id] = task_variance(t, mode)

    results: Dict[str, TaskResult] = {}
    for t in tasks:
        results[t.task_id] = TaskResult(
            task_id=t.task_id,
            name=t.name,
            duration=durations[t.task_id],
            predecessors=list(G.predecessors(t.task_id)),
            successors=list(G.successors(t.task_id)),
            variance=variances[t.task_id],
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

    # Дисперсия проекта = сумма дисперсий критических работ
    project_variance = sum(results[t].variance for t in critical)

    return ProjectResult(
        tasks=results,
        duration=project_duration,
        critical_path=critical,
        variance=project_variance,
    )


# ---------------------------------------------------------- Crashing

@dataclass
class CrashStep:
    task_id: str
    days: float
    cost: float


@dataclass
class CrashResult:
    steps: List[CrashStep]
    final_duration: float
    total_cost: float
    schedule: Dict[str, float]              # итоговые длительности
    result: ProjectResult                   # финальный расчёт


def optimize_crashing(tasks: List[Task],
                      target: float,
                      mode: Mode = Mode.DETERMINISTIC,
                      max_iter: int = 2000) -> CrashResult:
    """
    Жадный алгоритм сжатия критического пути.

    На каждой итерации:
      1. Считаем CPM с текущими длительностями.
      2. Если длительность проекта ≤ target — стоп.
      3. Иначе ищем критическую работу с минимальной ценой ускорения,
         которую ещё можно сжать.
      4. Уменьшаем её длительность на 1 день (или на остаток до минимума).
    """
    if not tasks:
        return CrashResult([], 0, 0, {}, calculate([], mode))

    task_map = {t.task_id: t for t in tasks}
    durations = {t.task_id: expected_duration(t, mode) for t in tasks}
    steps: List[CrashStep] = []
    total_cost = 0.0

    for _ in range(max_iter):
        result = calculate(tasks, mode, durations_override=durations)
        if result.duration <= target + EPS:
            return CrashResult(steps, result.duration, total_cost,
                               dict(durations), result)

        # Найти кандидатов на сжатие
        candidates = []
        for tid in result.critical_path:
            t = task_map[tid]
            if t.crash_duration is None or t.cost_per_day is None:
                continue
            room = durations[tid] - t.crash_duration
            if room <= EPS:
                continue
            candidates.append((t.cost_per_day, tid, room))

        if not candidates:
            # Дальше сжимать нечего
            break

        # Самый дешёвый критический шаг
        candidates.sort()
        cost, tid, room = candidates[0]
        step = min(1.0, room)
        durations[tid] -= step
        total_cost += cost * step
        steps.append(CrashStep(tid, step, cost * step))

    final = calculate(tasks, mode, durations_override=durations)
    return CrashResult(steps, final.duration, total_cost,
                       dict(durations), final)