# 🚀 Cloud To-Do List Application

## Обзор Проекта

Это простое, но полнофункциональное веб-приложение для управления списком задач (**To-Do List**), развернутое на платформе **Google Cloud**. Приложение позволяет пользователям создавать карточки задач, сохранять их в облачной базе данных и отмечать как выполненные с помощью бессерверной функции.

---

## ✨ Основные Функции

1.  **Создание Карточек:** Добавление новых задач с **Заголовком (Title)** и **Описанием (Description)**.
2.  **Валидация Формы:** Защита от создания пустых задач (поля должны быть заполнены).
3.  **Визуализация Статуса:** Каждая задача отображается с **чекбоксом**. При выполнении задачи её текст **зачеркивается**.
4.  **Облачное Хранение:** Все данные задач надежно хранятся в **Google Cloud Datastore**.

---

## 🏗️ Архитектура и Технологии

Проект использует гибридную архитектуру Google Cloud, сочетая традиционный веб-сервер с бессерверными вычислениями.

### 1. 🌐 Google App Engine (Standard Environment)

**Роль:** Основной веб-сервер и API для обработки пользовательского интерфейса и создания данных.

* **Технология:** **Python** (Flask)
* **Функционал:**
    * **Обработка GET /**: Рендеринг главной страницы (`index.html`) и отображение актуального списка задач, полученных из Datastore.
    * **Обработка POST /add**: Прием данных с формы, валидация полей `title` и `description`, и сохранение новой задачи в Datastore.
    * **Хостинг Фронтенда:** Обслуживание HTML/CSS/JavaScript.

### 2. ☁️ Google Cloud Functions

**Роль:** Бессерверная обработка API для специфических, атомарных операций, таких как обновление статуса задачи.

* **Технология:** **Python**
* **Функционал:**
    * **Обработка POST /updateTaskStatus**: Принимает JSON-запрос от фронтенда, содержащий `task_id` и новый статус `is_done` (True/False).
    * **Обновление Datastore:** Использует полученный ID для поиска и атомарного обновления поля `is_done` в Datastore, используя транзакцию.

### 3. 💾 Google Cloud Datastore

**Роль:** Постоянное, NoSQL-хранилище данных для всех карточек задач.

* **Структура данных (Сущность `Task`):**
    * `title` (string)
    * `description` (string)
    * `is_done` (boolean)
    * `created_at` (datetime)

### 4. ☁️ Google Cloud Endpoints

**Роль:** Возможность подключаться к серверу из внешних источников через Cloud Endpoint (с аутентификацией).

* **Технология:** **OpenAPI 2.0**
* **Функционал:**
    * **Обработка входящих запросов через Endpoint:** Установка правил OpenAPI для исходящих запросов
    * **Введение документации:** OpenAPI позволяет вести документацию для сайта. В данном сайте используется Swagger UI для введения документации

---

## 🧪 Тестирование и Обеспечение Качества (QA)

Для гарантии надежности, корректности и масштабируемости приложения применены строгие практики тестирования:

### 2. Нагрузочное Тестирование (Load Testing)

* Для оценки масштабируемости используется инструмент **Locust**.
* **Сценарий:** Имитируются тысячи одновременных пользователей, выполняющих **просмотр** и **создание** задач.
* **Анализ:** Отслеживаются **Requests per second (RPS)** и **среднее время ответа (Latency)** для оценки производительности GKE и Cloud Functions при пиковой нагрузке.
* Для запуска тестирования
```bash
python -m locust -f locustfile.py
```
---

## 🛠️ Установка и Развертывание

### Предварительные Требования

* Установленный Google Cloud SDK (`gcloud`).
* Проект Google Cloud с включенными API: **App Engine**, **Cloud Functions**, **Cloud Datastore**.
* Локальная установка Python (3.9+).

### Шаги

1.  **Клонирование Репозитория:**
    ```bash
    git clone [ссылка на ваш репозиторий] todo-cloud-app
    cd todo-cloud-app
    ```

2.  **Развертывание App Engine (Flask-приложение):**
    Убедитесь, что `main_appengine.py` и `app.yaml` находятся в корневой папке.
    ```bash
    pip install -r requirements.txt # Установите локально для проверки
    gcloud app deploy app.yaml
    ```
    *(Приложение будет доступно по адресу `https://[PROJECT_ID].appspot.com`)*

3.  **Развертывание Cloud Function:**
    Перейдите в директорию с кодом функции и разверните её.
    ```bash
    cd cloud-function-update-task/ 
    gcloud functions deploy updateTaskStatus \
      --runtime python311 \
      --trigger-http \
      --allow-unauthenticated \
      --source .
    ```

4.  **Обновление URL Функции:**
    **ВАЖНО:** Скопируйте реальный URL развернутой Cloud Function из консоли и вставьте его в файл `templates/index.html` в переменную `CLOUD_FUNCTION_URL`.

5. **Развертывание Cloud Endpoint:**
    Для развертывания Cloud Endpoint для начала необходимо настроить IAP. Для этого:
    
    * Перейдите во вкладку **Security -> Identity-Aware Proxy (IAP)**
    * Включите IAP для вашего проекта
    * Нажмите на троеточие справа от имени вашего проекта -> **Settings** (прокрутите если не видно)
    * Выберите **Custom OAuth** и в разделе **Custom client ID and secret** нажмите **Auto Genereate Credentials**. Сохраните

    После выполненных шагов:
    
    * Перейдите во вкладку **API & Services -> Credentials**.
    * Выберите **OAuth 2.0 Client ID** сгенерированный вами (IAP-App-Engine-app).
    * В раздел **Authorized JavaScript origins** добавьте URL адрес вашего проекта.

    Выдайте право на использование IAP вашему проекту (IAP-secured Web App user). Для этого:
    * Нажмите на ваш проект на главной странице (справа от Google Cloud)
    * Выберите иконку папки с шестеренкой (менеджер проектов)
    * Выберите **Show Info Panel** справа в верхнем углу
    * Выберите ваш проект
    * Нажмите **Add Principal** (укажите свою почту)
    * В **Select a role** найдите **IAP-serured Web App user**
    
    Далее необходимо перейти в папку вашего проекта и развернуть endpoint (перед этим замените URL в файле openapi-appengine.yaml):
    ```bash
    gcloud endpoints services deploy openapi-appengine.yaml
    ```
    Обновите ваш проект:
    ```bash
    gcloud app deploy
    ```

    Для того чтобы узнать Cloud Endpoint URL вы можете выполнить команду:
    ```bash
    gcloud endpoints services list
    ```

    * Данный Cloud Endpoint позволяет вам зайти на сайт с авторизованным токеном (Oauth 2.0 Client ID).
    * Теперь вы можете перейти во вкладку /docs вашего проекта через данный endpoint (https://[CLOUD_ENDPOINT_URL]/docs) для введения OpenAPI документации.
      
6. Для деплоя в Google Kubernetes Engine (GKE) замените PROJECT_ID на ваш собственный (выбранный регион для деплоя us-central1). GKE распознает в какой репозиторий деплоить код по тегам Docker:
   
   Для Windows:
   ```bash
   $Env:PROJECT_ID=[your_project_id]
   $Env:REGION=us-central1
   
   docker build --build-arg ADC=$Env:APPDATA/gcloud/application_default_credentials.json -t $Env:REGION-docker.pkg.dev/$Env:PROJECT_ID/gae-standard/flask-app .
   
   docker push $Env:REGION-docker.pkg.dev/$Env:PROJECT_ID/gae-standard/flask-app
   
   gcloud container clusters create-auto hello-cluster
   
   gcloud container clusters get-credentials hello-cluster --location=$Env:REGION
   
   kubectl create deployment flask-app --image=$Env:REGION-docker.pkg.dev/$Env:PROJECT_ID/gae-standard/flask-app
   
   kubectl expose deployment flask-app --name=flask-app-service --type=LoadBalancer --port 80 --target-port 8080
   ```

   Для MacOS:
   ```bash
   export PROJECT_ID=[your_project_id]
   export REGION=us-central1
   
   docker build --build-arg ADC=~/gcloud/application_default_credentials.json -t $REGION-docker.pkg.dev/$PROJECT_ID/gae-standard/flask-app .
   
   docker push $REGION-docker.pkg.dev/$PROJECT_ID/gae-standard/flask-app
   
   gcloud container clusters create-auto hello-cluster
   
   gcloud container clusters get-credentials hello-cluster --location=$REGION
   
   kubectl create deployment flask-app --image=$REGION-docker.pkg.dev/$PROJECT_ID/gae-standard/flask-app
   
   kubectl expose deployment flask-app --name=flask-app-service --type=LoadBalancer --port 80 --target-port 8080
   ```
   Для Linux замените аргумент первой команды (ADC) на $HOME/.config/gcloud/application_default_credentials.json.

   Для получения списка задеплоенных сервисов выполните:
   ```bash
   kubectl get service
   ```
   Данная команда покажет вами задеплоенный "flask-app-service". Перейдите по EXTERNAL_IP чтобы увидеть ваш сервис задеплоенный в интернет.
---

## 👨‍💻 Как Пользоваться

1.  Откройте приложение по адресу App Engine.
2.  Заполните поля "Заголовок Задачи" и "Описание Задачи".
3.  Нажмите **"Создать Задачу"**.
4.  Для отметки выполнения, кликните на чекбокс рядом с карточкой задачи. Это действие отправит запрос в Cloud Function.
