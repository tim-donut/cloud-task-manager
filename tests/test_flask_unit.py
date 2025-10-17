#test_flask_unit.py
import types
import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ---------------------------
# Мокаем пакеты google.*
# ---------------------------
mock_google = types.ModuleType("google")
mock_google.cloud = types.SimpleNamespace(datastore=types.SimpleNamespace(Client=lambda: None))
mock_google.auth = types.SimpleNamespace(exceptions=types.SimpleNamespace(DefaultCredentialsError=Exception))

# Регистрируем в sys.modules
sys.modules["google"] = mock_google
sys.modules["google.cloud"] = mock_google.cloud
sys.modules["google.cloud.datastore"] = mock_google.cloud.datastore
sys.modules["google.auth"] = mock_google.auth
sys.modules["google.auth.exceptions"] = mock_google.auth.exceptions


from main_appengine import app

# ---------------------------
# Настройка тестового клиента
# ---------------------------
@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

# ---------------------------
# Мокаем Datastore (успех)
# ---------------------------
def test_add_task_success(monkeypatch, client):
    # Простой мок для entity/put
    class MockKey:
        pass

    class MockEntity(dict):
        pass

    class MockDatastoreClient:
        def key(self, kind, id=None):
            # Возвращаем фиктивный ключ (в твоём коде key может строиться иначе)
            return MockKey()

        def put(self, entity):
            # Имитация сохранения — можно сохранить куда-то или просто пройти
            return None

    # Подмена реального клиента на мок в модуле main
    monkeypatch.setattr("main_appengine.client", MockDatastoreClient())

    # Формируем корректный запрос (подставь нужные поля для твоего add-эндпоинта)
    payload = {
        "title": "Unit test task",
        "description": "Testing add_task"
    }

    # Если твой маршрут — "/add", оставь как есть. Если "/add_task" — поменяй URL.
    response = client.post("/add", json=payload)

    # Проверки — подстрой под то, что возвращает твой роут
    assert response.status_code in (200, 201)
    # Если возвращается json с сообщением:
    try:
        data = response.get_json()
        assert data is not None
    except Exception:
        # Если возвращается строка — просто проверим тело
        assert b"task" in response.data.lower() or b"added" in response.data.lower()

# ---------------------------
# Мокаем Datastore (недостаточно полей)
# ---------------------------
def test_add_task_bad_request(client):
    # Отправляем неполный запрос — ожидаем 400/422
    payload = {"title": ""}  # нет description
    response = client.post("/add", json=payload)

    # Ожидаем, что сервер валидирует тело и возвращает ошибку
    assert response.status_code in (400, 422)
