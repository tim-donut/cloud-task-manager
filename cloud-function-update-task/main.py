from google.cloud import datastore
import functions_framework
import json

client = datastore.Client() 
ENTITY_KIND = 'Task' 

@functions_framework.http
def updateTaskStatus(request):
    headers = {
        'Access-Control-Allow-Origin': '*', 
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600'
    }

    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    if request.method != 'POST':
        return (json.dumps({'error': 'Метод не разрешен'}), 405, headers)
    
    try:
        request_json = request.get_json(silent=True)
        
        # --- КРИТИЧЕСКИЙ МОМЕНТ: Преобразование ID в целое число (int) ---
        task_id = int(request_json['id']) # ID Datastore должен быть числом
        is_done = bool(request_json['is_done'])
        
        # Получаем ключ и сущность
        key = client.key(ENTITY_KIND, task_id)
        
        with client.transaction():
            task_entity = client.get(key)
            
            if not task_entity:
                return (json.dumps({'error': f'Задача с ID {task_id} не найдена'}), 404, headers)
                
            task_entity['is_done'] = is_done
            client.put(task_entity)
        
        response_data = {'success': True}
        return (json.dumps(response_data), 200, headers)
        
    except Exception as e:
        # Если здесь ошибка, это приведет к 500, и JS покажет ваше сообщение
        error_message = f'Ошибка обработки в функции: {e}'
        return (json.dumps({'error': error_message}), 500, headers)