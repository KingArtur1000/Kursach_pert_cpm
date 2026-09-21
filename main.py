"""Точка входа: расчёт CPM и вывод результатов."""

import pandas as pd

from data import TASKS, TASK_NAMES, PROJECT_NAME
from model import calculate, to_table
from visualize import draw_network, draw_gantt


def print_report(result):
    """Печатает текстовый отчёт по проекту."""
    print("=" * 70)
    print(f"Проект: {PROJECT_NAME}")
    print("=" * 70)

    rows = to_table(result, TASK_NAMES)
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))

    print()
    print(f"Длительность проекта: {result.duration} дн.")
    print(f"Критический путь: {' → '.join(result.critical_path)}")

    total_tf = sum(r.tf for r in result.tasks.values())
    print(f"Суммарный резерв всех работ: {total_tf} дн.")
    print(f"Критических работ: {len(result.critical_path)} "
          f"из {len(result.tasks)}")

    print()
    print("Резервы по работам (TF — полный, FF — свободный):")
    for t, r in sorted(result.tasks.items(), key=lambda x: x[1].es):
        name = TASK_NAMES.get(t, t)
        mark = " ★" if r.is_critical else ""
        print(f"  {t:>2} | {name:<20} | TF={r.tf:>2}  FF={r.ff:>2}{mark}")


def main():
    result = calculate(TASKS)

    print_report(result)

    # Визуализация
    draw_network(TASKS, result, save_path="network.png")
    draw_gantt(result, save_path="gantt.png")


if __name__ == "__main__":
    main()