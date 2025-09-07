"""
Модуль для загрузки переменных окружения из файла .env
"""

import os
from pathlib import Path

def load_env_file():
    """Загружает переменные окружения из файла .env"""
    env_file = Path('.env')
    
    if not env_file.exists():
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Пропускаем пустые строки и комментарии
                if not line or line.startswith('#'):
                    continue
                
                # Разделяем ключ и значение
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Убираем кавычки, если есть
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Устанавливаем переменную окружения, если она еще не установлена
                    if key not in os.environ:
                        os.environ[key] = value
        
        return True
        
    except Exception as e:
        print(f"Ошибка загрузки файла .env: {e}")
        return False

# Автоматически загружаем .env при импорте модуля
load_env_file()