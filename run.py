#!/usr/bin/env python3
"""
Скрипт запуска Reward Bot
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, str(Path(__file__).parent))

from bot import main

def setup_logging():
    """Настройка логирования"""
    # Создаем директорию для логов, если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'bot.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Настраиваем логирование для aiogram
    logging.getLogger('aiogram').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)

def check_environment():
    """Проверка переменных окружения"""
    from config import BOT_TOKEN, ADMIN_ID
    
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не установлен!")
        print("Установите переменную окружения BOT_TOKEN или создайте файл .env")
        return False
    
    if not ADMIN_ID or ADMIN_ID == 0:
        print("⚠️  Предупреждение: ADMIN_ID не установлен!")
        print("Административные команды будут недоступны")
    
    return True

def main_wrapper():
    """Обертка для основной функции"""
    try:
        # Настройка логирования
        setup_logging()
        logger = logging.getLogger(__name__)
        
        logger.info("🚀 Запуск Reward Bot...")
        
        # Проверка переменных окружения
        if not check_environment():
            sys.exit(1)
        
        # Запуск бота
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("⏹️  Остановка бота по запросу пользователя")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main_wrapper()