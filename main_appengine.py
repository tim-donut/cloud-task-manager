# main_appengine.py

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from google.cloud import datastore # Изменяем импорт
from datetime import datetime
from google.auth.exceptions import DefaultCredentialsError

app = Flask(__name__)
# В реальном приложении: app.secret_key должен быть секретным и храниться в Secret Manager
app.secret_key = 'super_secret_key_for_flash' 

# Инициализация клиента Firestore
# Автоматически использует учетные данные среды App Engine
try:
    client = datastore.Client()# Изменяем инициализацию
except DefaultCredentialsError:
    client = None # При локальных тестах клиент будет отключен
ENTITY_KIND = 'Task' # В Datastore сущности называются Kind (Тип)

# ------------------------------------
# 1. GET: Отображение списка задач
# ------------------------------------
@app.route('/', methods=['GET'])
def index():
    """Отображает главную страницу со списком задач."""
    try:
        query = client.query(kind=ENTITY_KIND)
        query.order = ['created_at'] # Сортировка
        
        # Загружаем сущности (Entities)
        tasks_entities = list(query.fetch())
        
        # Преобразуем сущности Datastore в удобный список словарей
        tasks = []
        for entity in tasks_entities:
            task = dict(entity) # Копируем поля
            task['id'] = entity.key.id # Получаем ID из ключа
            tasks.append(task)

    except Exception as e:
        flash(f"Ошибка загрузки задач: {e}", "error")
        tasks = []

    return render_template('index.html', tasks=tasks)

# ------------------------------------
# 2. POST: Создание новой задачи
# ------------------------------------
@app.route('/add', methods=['POST'])
def add_task():

    # Отправка на форму по правилам REST API должна быть в виде JSON файлов (которому данный сайт не следует).
    # Для введения документации OpenAPI необходимо добавить принятие JSON файлов.
    if request.is_json:
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
    else:
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
    
    # Проверка на пустое поле
    if not title or not description:
        message = "🚫 Ошибка: Оба поля (Заголовок и Текст) должны быть заполнены."
        if request.is_json:
            return {"error": message}, 400  
        flash(message, "error")
        return redirect(url_for('index'))
    
    new_task = None
    try:
        # Создаем новую сущность Datastore
        if client:
            key = client.key(ENTITY_KIND)
            new_task = datastore.Entity(key)
            new_task.update({
                'title': title,
                'description': description,
                'is_done': False,
                'created_at': datetime.utcnow()
            })
            client.put(new_task)
        else:
            new_task = {'title': title, 'description': description, 'is_done': False}
        flash(f"✅ Задача '{title}' успешно добавлена!", "success")
        
    except Exception as e:
        flash(f"❌ Критическая ошибка при сохранении задачи: {e}", "error")

    # Возврат ответа для OpenAPI в виде JSON файла.
    if request.is_json:
        created_task = dict(new_task) if new_task else {}
        created_task['id'] = getattr(getattr(new_task, 'key', None), 'id', None)
        return created_task, 201
    return redirect(url_for('index'))

@app.route('/docs')
def get_docs():
    """Отображает страницу документации."""
    return render_template('docs.html')

@app.route('/openapi-appengine.yaml')
def get_api_spec():
    """Возвращает OpenAPI спецификацию"""
    return send_from_directory('.', 'openapi-appengine.yaml')

if __name__ == '__main__':
    # Используется только для локального запуска
    app.run(debug=True, host='0.0.0.0', port=8080)