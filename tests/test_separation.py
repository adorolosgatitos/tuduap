"""Guarda arquitectónica: el dominio no puede depender de la interfaz.

Es la regla que sostiene AC-11. Si algún día todo_app/ importa streamlit, la
suite seguiría pasando los tests de comportamiento (que ya no correrían) y
nadie se enteraría hasta que la lógica dejara de ser testeable. Por eso el
chequeo es explícito y va sobre el AST, no sobre el texto: los docstrings
mencionan streamlit a propósito, y una búsqueda de substring daría un falso
positivo.
"""

import ast
from pathlib import Path

import pytest

import todo_app

DOMINIO = Path(todo_app.__path__[0])
INTERFAZ = "streamlit"


@pytest.fixture(scope="module")
def modulos():
    return sorted(DOMINIO.glob("*.py"))


def imports_de(modulo: Path) -> set[str]:
    arbol = ast.parse(modulo.read_text(), filename=str(modulo))
    nombres = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres.add(nodo.module)
    return nombres


def test_el_paquete_tiene_los_tres_modulos_esperados(modulos):
    assert {m.name for m in modulos} >= {"task.py", "logic.py", "store.py"}


@pytest.mark.parametrize("atributo", ["Task", "TaskFilter"])
def test_el_paquete_expone_el_modelo(atributo):
    assert hasattr(todo_app, atributo)


def test_ningun_modulo_del_dominio_importa_streamlit(modulos):
    culpables = {
        m.name: n for m in modulos for n in imports_de(m) if n.split(".")[0] == INTERFAZ
    }
    assert culpables == {}, (
        f"todo_app/ no puede depender de la interfaz, pero importa {culpables}. "
        "El store recibe el estado por parámetro justamente para que esto sea posible."
    )


def test_el_dominio_no_depende_de_nada_de_la_app_tampoco(modulos):
    """El otro lado del mismo problema: que la UI no se filtre adentro del
    dominio y termine importada desde abajo."""
    culpables = {m.name: n for m in modulos for n in imports_de(m) if n == "app"}
    assert culpables == {}, f"todo_app/ no debería importar app: {culpables}"
