"""Reglas de las tareas. Corren sin streamlit instalado, y por eso deben
seguir siendo funciones puras: si algo acá necesitara la sesión, la suite
estaría probando la app y no las reglas."""

import pytest

from todo_app.logic import (
    InvalidTaskText,
    clean_text,
    count_by_state,
    create_task,
    filter_tasks,
    is_valid,
    remove_task,
    toggle,
)
from todo_app.task import Task, TaskFilter


def tareas(*estados):
    """Atajo para armar una lista de tareas con id y estado conocidos."""
    return [
        Task(id=f"t{i}", text=texto, done=done)
        for i, (texto, done) in enumerate(estados)
    ]


class TestValidacion:
    @pytest.mark.parametrize(
        "crudo",
        ["", "   ", "\t", "\n", " \t\n ", None],
    )
    def test_texto_sin_contenido_se_rechaza(self, crudo):
        assert is_valid(crudo) is False
        with pytest.raises(InvalidTaskText):
            create_task(crudo)

    @pytest.mark.parametrize(
        "crudo,esperado",
        [("hola", "hola"), ("  hola  ", "hola"), ("\tmia\n", "mia"), ("a", "a")],
    )
    def test_texto_valido_sobrevive_limpio(self, crudo, esperado):
        assert is_valid(crudo) is True
        assert create_task(crudo).text == esperado

    def test_los_espacios_del_interior_no_se_toquen(self):
        """Recortar es limpiar bordes, no reescribir lo que el usuario escribió."""
        assert clean_text("poner  la  comida") == "poner  la  comida"

    def test_una_tarea_nace_pendiente(self):
        assert create_task("dormir").done is False

    def test_cada_tarea_nace_con_id_propio(self):
        ids = {create_task("a").id for _ in range(50)}
        assert len(ids) == 50

    def test_el_id_se_puede_inyectar_para_los_tests(self):
        assert create_task("a", task_id="fijo").id == "fijo"


class TestAlternar:
    def test_alternar_completa_una_tarea_pendiente(self):
        (tarea,) = tareas(("dormir", False))
        assert toggle([tarea], tarea.id)[0].done is True

    def test_alternar_deja_una_tarea_completada_pendiente(self):
        (tarea,) = tareas(("dormir", True))
        assert toggle([tarea], tarea.id)[0].done is False

    def test_alternar_dos_veces_vuelve_al_inicio(self):
        (tarea,) = tareas(("dormir", False))
        return_al_todo = toggle(toggle([tarea], tarea.id), tarea.id)
        assert return_al_todo[0] == tarea

    def test_alternar_solo_toca_la_tarea_apuntada(self):
        lista = tareas(("a", False), ("b", False))
        resultado = toggle(lista, "t0")
        assert [t.done for t in resultado] == [True, False]

    def test_un_id_desconocido_no_rompe_nada(self):
        lista = tareas(("a", False))
        assert toggle(lista, "no-existe") == lista

    def test_alternar_no_muta_la_lista_original(self):
        lista = tareas(("a", False))
        toggle(lista, "t0")
        assert lista[0].done is False, "la UI guarda esta lista en session_state"


class TestEliminar:
    def test_eliminar_saca_la_tarea_apuntada(self):
        lista = tareas(("a", False), ("b", False))
        assert [t.text for t in remove_task(lista, "t0")] == ["b"]

    def test_eliminar_conserva_el_orden_del_resto(self):
        lista = tareas(("a", False), ("b", False), ("c", False))
        assert [t.text for t in remove_task(lista, "t1")] == ["a", "c"]

    def test_un_id_desconocido_no_rompe_nada(self):
        """El usuario puede apretar dos veces rápido el mismo botón."""
        lista = tareas(("a", False))
        assert remove_task(lista, "no-existe") == lista

    def test_eliminar_no_muta_la_lista_original(self):
        lista = tareas(("a", False))
        remove_task(lista, "t0")
        assert len(lista) == 1

    def test_una_lista_sin_tareas_sigue_funcionando(self):
        assert remove_task([], "t0") == []


class TestFiltrar:
    @pytest.fixture
    def lista(self):
        return tareas(("pendiente1", False), ("hecha", True), ("pendiente2", False))

    def test_el_filtro_todas_muestra_todo(self, lista):
        assert len(filter_tasks(lista, TaskFilter.ALL)) == 3

    def test_el_filtro_pendientes_saca_las_hechas(self, lista):
        visibles = filter_tasks(lista, TaskFilter.PENDING)
        assert [t.text for t in visibles] == ["pendiente1", "pendiente2"]

    def test_el_filtro_completadas_saca_las_pendientes(self, lista):
        visibles = filter_tasks(lista, TaskFilter.COMPLETED)
        assert [t.text for t in visibles] == ["hecha"]

    def test_filtrar_preserva_el_orden_de_insercion(self, lista):
        assert [t.id for t in filter_tasks(lista, TaskFilter.ALL)] == ["t0", "t1", "t2"]

    def test_filtrar_una_lista_vacia_devuelve_vacio(self):
        for filtro in TaskFilter:
            assert filter_tasks([], filtro) == []

    def test_pendientes_y_completadas_no_se_pisen(self, lista):
        """Cada tarea está en un filtro o en el otro, nunca en los dos."""
        pendientes = {t.id for t in filter_tasks(lista, TaskFilter.PENDING)}
        completadas = {t.id for t in filter_tasks(lista, TaskFilter.COMPLETED)}
        assert not pendientes & completadas

    def test_los_dos_filtros_juntos_cubren_la_lista_entera(self, lista):
        pendientes = {t.id for t in filter_tasks(lista, TaskFilter.PENDING)}
        completadas = {t.id for t in filter_tasks(lista, TaskFilter.COMPLETED)}
        assert pendientes | completadas == {t.id for t in lista}

    def test_todas_no_deja_ninguna_tarea_afuera(self, lista):
        assert {t.id for t in filter_tasks(lista, TaskFilter.ALL)} == {t.id for t in lista}

    def test_filtrar_no_muta_la_lista_original(self, lista):
        filter_tasks(lista, TaskFilter.PENDING)
        assert len(lista) == 3


class TestContadores:
    def test_los_conteos_reflejan_el_estado_real(self):
        lista = tareas(("a", False), ("b", False), ("c", True))
        conteos = count_by_state(lista)
        assert conteos[TaskFilter.ALL] == 3
        assert conteos[TaskFilter.PENDING] == 2
        assert conteos[TaskFilter.COMPLETED] == 1

    def test_una_lista_vacia_cuenta_cero_en_todo(self):
        conteos = count_by_state([])
        assert set(conteos.values()) == {0}
