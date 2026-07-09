import pytest
from fastapi.testclient import TestClient
from main import app
import os
import sqlite3

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    """Limpia la BD antes de cada test para empezar siempre vacío"""
    if os.path.exists("tareas.db"):
        os.remove("tareas.db")
    from main import init_db
    init_db()
    yield


@pytest.fixture
def created_task_id():
    """Crea una tarea y devuelve su ID"""
    response = client.post("/items", json={
        "title": "Tarea de prueba",
        "priority": "high"
    })
    return response.json()["id"]


class TestRoot:
    def test_root_returns_ok(self):
        r = client.get("/")
        assert r.status_code == 200
        assert r.json() == {"message": "API funcionando"}


class TestListItems:
    def test_list_empty(self):
        r = client.get("/items")
        assert r.status_code == 200
        data = r.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["limit"] == 10

    def test_list_with_items(self, created_task_id):
        r = client.get("/items")
        assert r.status_code == 200
        data = r.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1

    def test_pagination(self):
        for i in range(15):
            client.post("/items", json={"title": f"Tarea {i}", "priority": "low"})

        r1 = client.get("/items?page=1&limit=10")
        assert r1.status_code == 200
        assert len(r1.json()["items"]) == 10
        assert r1.json()["total"] == 15

        r2 = client.get("/items?page=2&limit=10")
        assert r2.status_code == 200
        assert len(r2.json()["items"]) == 5
        assert r2.json()["total"] == 15

    def test_pagination_defaults(self):
        r = client.get("/items")
        assert r.json()["page"] == 1
        assert r.json()["limit"] == 10


class TestCreateItem:
    def test_create_valid(self):
        r = client.post("/items", json={
            "title": "Mi tarea",
            "priority": "medium"
        })
        assert r.status_code == 201
        data = r.json()
        assert data["title"] == "Mi tarea"
        assert data["priority"] == "medium"
        assert data["status"] == "pending"
        assert data["description"] == ""
        assert "id" in data
        assert "createdAt" in data

    def test_create_with_description(self):
        r = client.post("/items", json={
            "title": "Con desc",
            "priority": "low",
            "description": "Detalle importante"
        })
        assert r.status_code == 201
        assert r.json()["description"] == "Detalle importante"

    def test_create_missing_title(self):
        r = client.post("/items", json={"priority": "high"})
        assert r.status_code == 400

    def test_create_missing_priority(self):
        r = client.post("/items", json={"title": "Solo título"})
        assert r.status_code == 400

    def test_create_invalid_priority(self):
        r = client.post("/items", json={
            "title": "Test",
            "priority": "urgent"
        })
        assert r.status_code == 400


class TestGetItem:
    def test_get_existing(self, created_task_id):
        r = client.get(f"/items/{created_task_id}")
        assert r.status_code == 200
        assert r.json()["id"] == created_task_id

    def test_get_not_found(self):
        r = client.get("/items/id-inexistente")
        assert r.status_code == 404
        assert r.json()["detail"] == "Tarea no encontrada"


class TestUpdateItem:
    def test_update_status(self, created_task_id):
        r = client.patch(f"/items/{created_task_id}", json={"status": "done"})
        assert r.status_code == 200
        assert r.json()["status"] == "done"

    def test_update_not_found(self):
        r = client.patch("/items/id-inexistente", json={"status": "done"})
        assert r.status_code == 404

    def test_update_invalid_status(self, created_task_id):
        r = client.patch(f"/items/{created_task_id}", json={"status": "cancelado"})
        assert r.status_code == 400
