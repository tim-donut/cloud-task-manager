#test_integration.py
import unittest
import time
from google.cloud import datastore
import requests

class IntegrationTestCF(unittest.TestCase):
    """Интеграционный тест Cloud Function и Datastore"""

    def setUp(self):
        # -----------------------------
        # Настройки Cloud Function
        # -----------------------------
        self.cf_url = "https://YOUR_CLOUD_FUNCTION_URL"  # <- подставьте свой CF URL
        self.ds_client = datastore.Client()  # Клиент Datastore
        self.test_id = f"test_{int(time.time())}"  # Уникальный ID теста
        print(f"🚀 Начало интеграционного теста, test_id={self.test_id}")

    def tearDown(self):
        """Удаление тестовых задач из Datastore после каждого теста"""
        query = self.ds_client.query(kind="Task")  # <- можно поменять на свой kind
        tasks = list(query.fetch())
        for task in tasks:
            if self.test_id in str(task.get("description", "")):
                self.ds_client.delete(task.key)

    def create_task_in_datastore(self, desc):
        """Создаём задачу напрямую в Datastore"""
        key = self.ds_client.key("Task")  # <- замените на ваш kind, если нужно
        task = datastore.Entity(key=key)
        task.update({
            "description": desc,
            "is_done": False
        })
        self.ds_client.put(task)
        return task.id

    def test_update_task_status(self):
        """Создаём задачу в Datastore и обновляем через Cloud Function"""
        desc = f"Тестовая задача {self.test_id}"
        task_id = self.create_task_in_datastore(desc)
        print(f"✓ Задача создана в Datastore, id={task_id}")

        # Обновляем статус через CF
        payload = {"id": task_id, "is_done": True}  # <- можно менять поля payload
        response = requests.post(self.cf_url, json=payload, headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success", False))
        print("✓ Статус обновлен через Cloud Function")

        # Проверяем в Datastore
        key = self.ds_client.key("Task", task_id)
        task = self.ds_client.get(key)
        self.assertTrue(task["is_done"])
        print("✓ Статус успешно обновлен в Datastore")

    def test_multiple_tasks_flow(self):
        """Создаём несколько задач и обновляем одну через CF"""
        task_ids = []
        for i in range(3):
            desc = f"Задача {i+1} {self.test_id}"
            task_id = self.create_task_in_datastore(desc)
            task_ids.append(task_id)
        print("✓ Созданы 3 задачи в Datastore")

        # Обновляем вторую задачу
        payload = {"id": task_ids[1], "is_done": True}
        response = requests.post(self.cf_url, json=payload, headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success", False))
        print("✓ Статус второй задачи обновлен через CF")

        # Проверяем статусы всех задач
        for i, task_id in enumerate(task_ids):
            task = self.ds_client.get(self.ds_client.key("Task", task_id))
            if i == 1:
                self.assertTrue(task["is_done"])
            else:
                self.assertFalse(task["is_done"])
        print("✓ Проверка статусов всех задач пройдена")


if __name__ == "__main__":
    unittest.main(verbosity=2)
