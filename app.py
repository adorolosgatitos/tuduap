"""Interfaz de la app. Acá solo se dibuja y se escuchan eventos.

Ninguna regla vive en este archivo: agregar, validar, alternar, filtrar y contar
están en todo_app/, que se puede testear sin abrir Streamlit.
"""

import streamlit as st

from todo_app.logic import InvalidTaskText
from todo_app.store import TaskStore
from todo_app.task import Task, TaskFilter

st.set_page_config(page_title="🐾 Mis tareas", page_icon="🐱", layout="centered")

# El gato de cada tarea: triste mientras le falta, contento cuando está hecha.
CATO_PENDIENTE = "😿"
CATO_LISTO = "😺"

FILTER_LABELS = {
    TaskFilter.ALL: "🐾 Todas",
    TaskFilter.PENDING: "😿 Pendientes",
    TaskFilter.COMPLETED: "😺 Completadas",
}

EMPTY_STATES = {
    TaskFilter.ALL: "🐾 Todavía no hay tareas. ¡Escribe la primera arriba!",
    TaskFilter.PENDING: "🐱 Ninguna pendiente. Michi puede dormir tranquilo 😴",
    TaskFilter.COMPLETED: "😺 Todavía no completaste ninguna tarea.",
}


def fila_de(tarea: Task) -> str:
    """El gato y el texto de una tarea.

    El tachado va con el texto, no solo con el color del checkbox: el estado
    tiene que poder distinguirse sin depender del color.
    """
    gato = CATO_LISTO if tarea.done else CATO_PENDIENTE
    texto = f"~~{tarea.text}~~" if tarea.done else tarea.text
    return f"{gato} {texto}"


store = TaskStore(st.session_state)

st.title("🐱 Mis tareas")
st.caption("Se guardan solo en esta sesión. Cuando cierras, se van con el gato.")

# --- Agregar ---
# clear_on_submit limpia el campo al enviar. Lo único que el formulario rechaza
# es texto vacío o de puros espacios, así que limpiar nunca tira away algo que
# el usuario haya tipeado de verdad.
with st.form("agregar", clear_on_submit=True):
    texto = st.text_input(
        "Nueva tarea",
        placeholder="Comprar comida para Michi",
        label_visibility="collapsed",
    )
    enviado = st.form_submit_button("🐾 Agregar")

if enviado:
    try:
        store.add(texto)
    except InvalidTaskText:
        st.error("🐾 Una tarea necesita texto: no puede estar vacía ni ser solo espacios.")

# --- Filtrar ---
conteos = store.counts()
filtro = st.radio(
    "Filtrar tareas",
    list(FILTER_LABELS),
    format_func=lambda f: f"{FILTER_LABELS[f]}  ({conteos[f]})",
    horizontal=True,
    label_visibility="collapsed",
)

# --- Listar ---
visibles = store.filtered(filtro)

if not visibles:
    st.info(EMPTY_STATES[filtro])
else:
    for tarea in visibles:
        col_check, col_texto, col_borrar = st.columns([0.5, 5, 0.7])

        with col_check:
            marcada = st.checkbox(
                "Completada",
                value=tarea.done,
                key=f"done-{tarea.id}",
                label_visibility="collapsed",
            )
        with col_texto:
            st.markdown(fila_de(tarea))
        with col_borrar:
            quitar = st.button("🗑️", key=f"del-{tarea.id}", help="Quitar tarea")

        if marcada != tarea.done:
            store.toggle(tarea.id)
            st.rerun()
        if quitar:
            store.remove(tarea.id)
            st.rerun()
