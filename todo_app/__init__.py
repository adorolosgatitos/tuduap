"""Dominio de tareas: modelo, lógica y estado.

Ninguna módulo de este paquete importa streamlit. Esa restricción no es
estética: es lo que permite testear la app sin levantarla.
"""

from .task import Task, TaskFilter

__all__ = ["Task", "TaskFilter"]
