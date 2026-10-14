"""Adaptador entre las reglas y el estado de la sesión.

La app le pasa `st.session_state` y los tests le pasan un dict vacío. Por eso
este módulo no importa streamlit: recibe el estado por parámetro y no sabe de
dónde vino. Es lo que hace que la suite corra sin instalar ni levantar la app.

No hay persistencia. Lo que hay en el mapping vive mientras viva la sesión del
navegador, y eso es exactamente lo pedido.
"""

from collections.abc import MutableMapping, Sequence

from .logic import (
    InvalidTaskText,
    count_by_state,
    create_task,
    filter_tasks,
    remove_task,
    toggle,
)
from .task import Task, TaskFilter

STATE_KEY = "tuduap_tasks"


class TaskStore:
    def __init__(self, state: MutableMapping, *, key: str = STATE_KEY) -> None:
        self._state = state
        self._key = key

    def all(self) -> list[Task]:
        return list(self._state.get(self._key, []))

    def add(self, raw: str | None) -> Task:
        """Agrega una tarea pendiente. Propaga InvalidTaskText si el texto
        está vacío, para que la UI decida cómo avisarle."""
        task = create_task(raw)
        self._state[self._key] = self.all() + [task]
        return task

    def toggle(self, task_id: str) -> None:
        self._state[self._key] = toggle(self.all(), task_id)

    def remove(self, task_id: str) -> None:
        self._state[self._key] = remove_task(self.all(), task_id)

    def filtered(self, task_filter: TaskFilter) -> list[Task]:
        return filter_tasks(self.all(), task_filter)

    def counts(self) -> dict[TaskFilter, int]:
        return count_by_state(self.all())
