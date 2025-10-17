#test_cloud_function.py
import sys
import os
import types
import json
import pytest

# -----------------------------
# Добавляем путь к модулю
# -----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cloud_function_update_task')))

# -----------------------------
# Мокаем google.cloud.datastore
# -----------------------------
class MockEntity(dict):
    pass

class MockKey:
    def __init__(self, kind, id):
        self.kind = kind
        self.id = id

class MockDatastoreClient:
    def __init__(self):
        self.storage = {}

    def key(self, kind, id):
        return MockKey(kind, id)

    def get(self, key):
        return self.storage.get(key.id)

    def put(self, entity):
        if hasattr(entity, 'key'):
            self.storage[entity.key.id] = entity
        else:
            self.storage[entity['id']] = entity

    def transaction(self):
        class DummyTransaction:
            def __enter__(self_): return self_
            def __exit__(self_, exc_type, exc_val, exc_tb): return False
        return DummyTransaction()

# -----------------------------
# Мокаем google.cloud.functions и functions_framework
# -----------------------------
mock_gcf = types.ModuleType("google.cloud.functions")
mock_gcf.Context = type("Context", (), {})
sys.modules["google.cloud.functions"] = mock_gcf

mock_ff = types.ModuleType("functions_framework")
sys.modules["functions_framework"] = mock_ff

sys.modules["google.cloud.datastore"] = types.SimpleNamespace(Client=lambda: MockDatastoreClient())

# -----------------------------
# Импортируем тестируемую функцию
# -----------------------------
from main import updateTaskStatus

# -----------------------------
# Фикстура для мок-запросов
# -----------------------------
class MockRequest:
    def __init__(self, method, json_data=None):
        self.method = method
        self._json = json_data

    def get_json(self, silent=True):
        return self._json

@pytest.fixture
def datastore_client():
    return MockDatastoreClient()

# -----------------------------
# Тесты
# -----------------------------
def test_update_task_status_done(datastore_client, monkeypatch):
    task_id = 1
    datastore_client.storage[task_id] = {'id': task_id, 'title': 'Task', 'description': 'Test', 'is_done': False}
    
    # Подменяем клиента на мок
    monkeypatch.setattr("main.client", datastore_client)

    request = MockRequest('POST', json_data={'id': task_id, 'is_done': True})
    response_body, status_code, headers = updateTaskStatus(request)
    data = json.loads(response_body)

    assert status_code == 200
    assert data['success'] is True
    assert datastore_client.storage[task_id]['is_done'] is True

def test_update_task_status_not_done(datastore_client, monkeypatch):
    task_id = 2
    datastore_client.storage[task_id] = {'id': task_id, 'title': 'Task2', 'description': 'Test2', 'is_done': True}

    monkeypatch.setattr("main.client", datastore_client)

    request = MockRequest('POST', json_data={'id': task_id, 'is_done': False})
    response_body, status_code, headers = updateTaskStatus(request)
    data = json.loads(response_body)

    assert status_code == 200
    assert data['success'] is True
    assert datastore_client.storage[task_id]['is_done'] is False

def test_cors_preflight():
    request = MockRequest('OPTIONS')
    response_body, status_code, headers = updateTaskStatus(request)

    assert status_code == 204
    assert headers['Access-Control-Allow-Origin'] == '*'
    assert 'OPTIONS' in headers['Access-Control-Allow-Methods']

def test_update_different_tasks(datastore_client, monkeypatch):
    datastore_client.storage[10] = {'id': 10, 'title': 'Task10', 'description': 'T10', 'is_done': False}
    datastore_client.storage[20] = {'id': 20, 'title': 'Task20', 'description': 'T20', 'is_done': False}

    monkeypatch.setattr("main.client", datastore_client)

    # Обновляем первую
    req1 = MockRequest('POST', {'id': 10, 'is_done': True})
    response_body, status_code, _ = updateTaskStatus(req1)
    data = json.loads(response_body)
    assert status_code == 200
    assert data['success'] is True
    assert datastore_client.storage[10]['is_done'] is True

    # Обновляем вторую
    req2 = MockRequest('POST', {'id': 20, 'is_done': True})
    response_body, status_code, _ = updateTaskStatus(req2)
    data = json.loads(response_body)
    assert status_code == 200
    assert data['success'] is True
    assert datastore_client.storage[20]['is_done'] is True
