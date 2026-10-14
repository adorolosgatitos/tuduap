"""El store contra un dict común.

El punto del store es justamente este: la app le pasa st.session_state y acá se
le pasa un dict. Si algún test necesitara streamlit, la separación que promete
el diseño estaría rota.
"""

import pytest

from todo_app.logic import InvalidTaskText
from todo_app.store import STATE_KEY, TaskStore
from todo_app.task import TaskFilter


@pytest.fixture
def state():
    """El equivalente de st.session_state en un test."""
    return {}


@pytest.fixture
def store(state):
    return TaskStore(state)


class TestEstadoInicial:
    def test_una_sesion_nueva_no_tiene_tareas(self, store):
        assert store.all() == []

    def test_agregar_a_un_mapping_vacio_no_lo_rompe(self, store, state):
        store.add("dormir")
        assert len(state[STATE_KEY]) == 1

    def test_no_se_toca_la_clave_del_estado_antes_de_agregar(self, store, state):
        store.all()
        assert state == {}, "consultar la lista no debería escribir nada"


class TestAgregar:
    def test_agregar_guarda_la_tarea(self, store):
        tarea = store.add("dormir")
        assert store.all() == [tarea]

    def test_las_tareas_se_guargan_en_orden(self, store):
        for texto in ("primera", "segunda", "tercera"):
            store.add(texto)
        assert [t.text for t in store.all()] == ["primera", "segunda", "tercera"]

    def test_agregar_recorta_el_texto(self, store):
        assert store.add("   hola   ").text == "hola"

    def test_agregar_texto_vacio_falla_y_no_ensucia_la_lista(self, store, state):
        with pytest.raises(InvalidTaskText):
            store.add("   ")
        assert store.all() == []
        assert STATE_KEY not in state, "un error no debería dejar basura en el estado"

    def test_los_ids_no_se_repiten(self, store):
        for _ in range(20):
            store.add("tarea")
        ids = [t.id for t in store.all()]
        assert len(ids) == len(set(ids))


class TestModificar:
    def test_alternar_desde_el_store_persiste(self, store):
        tarea = store.add("dormir")
        store.toggle(tarea.id)
        assert store.all()[0].done is True

    def test_alternar_desde_el_store_togglea_de_vuelta(self, store):
        tarea = store.add("dormir")
        store.toggle(tarea.id)
        store.toggle(tarea.id)
        assert store.all()[0].done is False

    def test_alternar_no_toca_las_demas(self, store):
        primera = store.add("a")
        store.add("b")
        store.toggle(primera.id)
        assert [t.done for t in store.all()] == [True, False]

    def test_eliminar_desde_el_store_persiste(self, store):
        primera = store.add("a")
        store.add("b")
        store.remove(primera.id)
        assert [t.text for t in store.all()] == ["b"]

    def test_alternar_una_tarea_ya_eliminada_no_reaparece(self, store):
        """El widget se dibujó con esa fila y el click llegó tarde: quitar tiene
        que ganarle al toggle, no devolver la tarea a la lista."""
        tarea = store.add("a")
        store.remove(tarea.id)
        store.toggle(tarea.id)
        assert store.all() == []

    def test_eliminar_un_id_desconocido_no_rompe_nada(self, store):
        store.add("a")
        store.remove("no-existe")
        assert len(store.all()) == 1


class TestFiltrarYContar:
    @pytest.fixture
    def con_estados(self, store):
        store.add("pendiente")
        hecha = store.add("hecha")
        store.toggle(hecha.id)
        return store

    def test_el_store_filtra_igual_que_la_logica(self, con_estados):
        assert len(con_estados.filtered(TaskFilter.ALL)) == 2
        assert len(con_estados.filtered(TaskFilter.PENDING)) == 1
        assert len(con_estados.filtered(TaskFilter.COMPLETED)) == 1

    def test_los_conteos_siguen_a_las_tareas(self, con_estados):
        conteos = con_estados.counts()
        assert conteos[TaskFilter.ALL] == 2
        assert conteos[TaskFilter.PENDING] == 1
        assert conteos[TaskFilter.COMPLETED] == 1


class TestPersistenciaDeSesion:
    def test_las_tareas_mueren_con_la_sesion(self, state):
        """Sin base de datos y sin archivos: un estado nuevo arranca vacío.
        Esto es la garantía de que nada se persiste."""
        TaskStore(state).add("dormir")
        assert TaskStore({}).all() == []

    def test_un_store_nuevo_sobre_el_mismo_estado_ve_las_tareas(self, store, state):
        store.add("dormir")
        assert TaskStore(state).all() == store.all()

    def test_cada_store_usa_su_propia_clave(self, state):
        otro = TaskStore(state, key="otras_tareas")
        otro.add("ajena")
        assert TaskStore(state).all() == []
        assert len(otro.all()) == 1
