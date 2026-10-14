"""Reglas de las tareas. Funciones puras: sin streamlit, sin estado global.

Cada función recibe lo que necesita y devuelve una lista nueva. La lista que
entra nunca se toca, así que la UI puede guardarla en session_state sin miedo a
que una operación la corrompa y los filtros muestren cosas raras.
"""

from collections.abc import Sequence
from dataclasses import replace
from uuid import uuid4

from .task import Task, TaskFilter


class InvalidTaskText(ValueError):
    """El texto está vacío o compuesto solo por espacios."""


def clean_text(raw: str | None) -> str:
    """Recorta los espacios de los extremos. El interior se respeta.

    Solo lo de los bordes: "poner  la  comida" sigue siendo una tarea con doble
    espacio adentro, y recortarla sería inventarse algo que el usuario no pidió.
    """
    return (raw or "").strip()


def is_valid(raw: str | None) -> bool:
    """True si queda texto después de limpiar."""
    return bool(clean_text(raw))


def create_task(raw: str | None, *, task_id: str | None = None) -> Task:
    """Arma una tarea pendiente.

    Lanza InvalidTaskText si no queda nada: una tarea sin texto no es una tarea,
    es un error de tipeo, y aceptarla deja basura en la lista.
    """
    text = clean_text(raw)
    if not text:
        raise InvalidTaskText("una tarea necesita texto")
    return Task(id=task_id or uuid4().hex, text=text, done=False)


def toggle(tasks: Sequence[Task], task_id: str) -> list[Task]:
    """Invierte el estado de una tarea. Un id desconocido no cambia nada."""
    return [
        task if task.id != task_id else replace(task, done=not task.done)
        for task in tasks
    ]


def remove_task(tasks: Sequence[Task], task_id: str) -> list[Task]:
    """Saca una tarea. Un id desconocido no cambia nada.

    Silencioso a propósito: la UI llama a esto desde un botón y un id que ya no
    está solo significa que el usuario apretó dos veces rápido.
    """
    return [task for task in tasks if task.id != task_id]


def filter_tasks(tasks: Sequence[Task], task_filter: TaskFilter) -> list[Task]:
    """Vista de la lista según el filtro. El orden de siempre se preserva."""
    if task_filter is TaskFilter.PENDING:
        return [task for task in tasks if not task.done]
    if task_filter is TaskFilter.COMPLETED:
        return [task for task in tasks if task.done]
    return list(tasks)


def count_by_state(tasks: Sequence[Task]) -> dict[TaskFilter, int]:
    """Cuántas hay de cada tipo, para los contadores de los filtros."""
    pending = sum(1 for task in tasks if not task.done)
    completed = sum(1 for task in tasks if task.done)
    return {
        TaskFilter.ALL: len(tasks),
        TaskFilter.PENDING: pending,
        TaskFilter.COMPLETED: completed,
    }
