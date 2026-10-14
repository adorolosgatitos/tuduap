# 🐱 Tuduap — ToDo gatil

Una lista de tareas con estética gatil, hecha con Streamlit. Se agregan, se
completan, se borran y se filtran. **No guarda nada**: las tareas viven en
`st.session_state` y se van cuando cierras la sesión.

## Correrla

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Se abre en http://localhost:8501

## Tests

```bash
.venv/bin/python -m pytest
```

## Cómo está armado

```
app.py                 Interfaz Streamlit. Solo dibuja y escucha.
todo_app/
  task.py              Task (inmutable) y TaskFilter. Modelo.
  logic.py             Reglas puras: validar, crear, alternar, eliminar, filtrar, contar.
  store.py             TaskStore: guarda las tareas en el estado que le pases.
tests/
  test_logic.py        Las reglas.
  test_store.py        El store, contra un dict.
  test_separation.py   Guarda: el dominio no importa streamlit.
```

La separación entre `app.py` y `todo_app/` no es una convención: `TaskStore`
recibe el estado por parámetro. En la app es `TaskStore(st.session_state)` y en
los tests es `TaskStore({})`, así que la suite corre sin instalar ni levantar
Streamlit. `test_separation.py` lo verifica sobre el AST, no sobre el texto.
