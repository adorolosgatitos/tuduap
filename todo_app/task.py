"""Modelo de datos de una tarea.

Vive aparte de la lógica y de la UI para que ninguna de las dos dependa de la
otra. `Task` es inmutable: la lógica devuelve listas nuevas en vez de mutar, y
congelar el dataclass hace que un mutar accidental sea un error visible y no
un bug silencioso que aparece tres filtros más abajo.
"""

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Task:
    id: str
    text: str
    done: bool = False


class TaskFilter(Enum):
    """Las tres vistas de la lista. Los valores son datos; las etiquetas con
    emoji viven en la UI, que es donde el usuario las ve."""

    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"
