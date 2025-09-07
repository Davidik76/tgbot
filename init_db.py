#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""

import asyncio
import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, str(Path(__file__).parent))

from database import Database
from config import DATABASE_PATH

async def init_database():
    """Инициализация базы данных"""
    try:
        print("🔧 Инициализация базы данных...")
        
        # Создаем экземпляр базы данных
        db = Database(DATABASE_PATH)
        
        # Инициализируем базу данных
        await db.init_db()
        
        print(f"✅ База данных успешно инициализирована: {DATABASE_PATH}")
        
        # Проверяем создание таблиц
        import aiosqlite
        async with aiosqlite.connect(DATABASE_PATH) as conn:
            cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = await cursor.fetchall()
            
            print(f"📋 Созданные таблицы: {[table[0] for table in tables]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации базы данных: {e}")
        return False

def main():
    """Основная функция"""
    try:
        success = asyncio.run(init_database())
        if success:
            print("\n🎉 Инициализация завершена успешно!")
            print("Теперь вы можете запустить бота командой: python run.py")
        else:
            print("\n💥 Инициализация завершилась с ошибкой!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Инициализация прервана пользователем")
    except Exception as e:
        print(f"\n💥 Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()