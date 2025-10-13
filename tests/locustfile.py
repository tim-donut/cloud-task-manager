# locustfile.py

from locust import HttpUser, task, between
import random

# !!! ВАЖНО: Замените на реальные URL вашего приложения и функции !!!
# URL App Engine, где размещен Flask
APP_ENGINE_HOST = "https://[YOUR_PROJECT_ID].appspot.com"
# URL Cloud Function (требуется ключ API, если Endpoints настроен)
CLOUD_FUNCTION_URL = "https://[REGION]-[PROJECT_ID].cloudfunctions.net/updateTaskStatus" 
# Ваш реальный ключ API (если Endpoints включен)
API_KEY = "YOUR_API_KEY_HERE" 


class TaskUser(HttpUser):
    # Пауза между запросами (от 1 до 5 секунд)
    wait_time = between(1, 5)
    host = APP_ENGINE_HOST 

    # 1. Задача: Просмотр списка (Самый частый запрос)
    @task(3) # Вероятность выполнения в 3 раза выше, чем у других
    def view_tasks(self):
        self.client.get("/", name="/ (View Tasks)")

    # 2. Задача: Создание новой задачи
    @task(1)
    def create_task(self):
        # Генерируем уникальные данные для каждой задачи
        unique_id = random.randint(1000, 9999)
        
        self.client.post("/add", data={
            "title": f"Test Task {unique_id}",
            "description": "Load test generated description."
        }, name="/add (Create Task)")

    # 3. Задача: Обновление статуса через Cloud Function (Дополнительно)
    # *Чтобы протестировать Cloud Function, Host должен быть изменен.*
    @task(0) # Установить 1 или более, чтобы включить
    def update_status_cf(self):
        # Имитируем обновление случайного, существующего ID (требует реальных данных)
        # Для простоты, мы просто сделаем POST-запрос с тестовыми данными.
        # В реальной жизни нужно получить ID задачи, прежде чем ее обновлять.
        headers = {'Content-Type': 'application/json'}
        
        # NOTE: Если используете Endpoints, ключ API должен быть вставлен в URL
        cf_url = f"{CLOUD_FUNCTION_URL}?key={API_KEY}"
        
        self.client.post(cf_url, 
                         json={"id": "999999", "is_done": random.choice([True, False])},
                         headers=headers,
                         name="/updateTaskStatus (Cloud Function)")