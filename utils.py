"""
Утилиты для работы с ботом
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import aiosqlite

from database import Database
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class BotUtils:
    """Класс с утилитами для работы с ботом"""
    
    def __init__(self, db: Database = None):
        self.db = db or Database(DATABASE_PATH)
    
    async def cleanup_old_activity(self, days: int = 7):
        """Очистка старых записей активности"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            async with aiosqlite.connect(DATABASE_PATH) as conn:
                # Удаляем старые записи активности
                cursor = await conn.execute(
                    "DELETE FROM chat_activity WHERE last_message_date < ?",
                    (cutoff_date,)
                )
                deleted_count = cursor.rowcount
                await conn.commit()
                
                logger.info(f"Удалено {deleted_count} старых записей активности")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Ошибка очистки старых записей: {e}")
            return 0
    
    async def backup_database(self, backup_path: str = None):
        """Создание резервной копии базы данных"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backup_{timestamp}.db"
            
            # Копируем файл базы данных
            import shutil
            shutil.copy2(DATABASE_PATH, backup_path)
            
            logger.info(f"Резервная копия создана: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
            return None
    
    async def get_database_stats(self) -> Dict:
        """Получение статистики базы данных"""
        try:
            async with aiosqlite.connect(DATABASE_PATH) as conn:
                stats = {}
                
                # Размер базы данных
                import os
                stats['file_size'] = os.path.getsize(DATABASE_PATH)
                
                # Количество записей в каждой таблице
                tables = ['users', 'chats', 'rewards', 'chat_activity']
                for table in tables:
                    cursor = await conn.execute(f"SELECT COUNT(*) FROM {table}")
                    count = (await cursor.fetchone())[0]
                    stats[f'{table}_count'] = count
                
                # Статистика по датам
                cursor = await conn.execute(
                    "SELECT MIN(registration_date), MAX(registration_date) FROM users"
                )
                user_dates = await cursor.fetchone()
                stats['first_user_date'] = user_dates[0]
                stats['last_user_date'] = user_dates[1]
                
                cursor = await conn.execute(
                    "SELECT MIN(added_date), MAX(added_date) FROM chats"
                )
                chat_dates = await cursor.fetchone()
                stats['first_chat_date'] = chat_dates[0]
                stats['last_chat_date'] = chat_dates[1]
                
                return stats
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики БД: {e}")
            return {}
    
    async def optimize_database(self):
        """Оптимизация базы данных"""
        try:
            async with aiosqlite.connect(DATABASE_PATH) as conn:
                # Анализируем базу данных
                await conn.execute("ANALYZE")
                
                # Очищаем свободное место
                await conn.execute("VACUUM")
                
                await conn.commit()
                logger.info("База данных оптимизирована")
                return True
                
        except Exception as e:
            logger.error(f"Ошибка оптимизации БД: {e}")
            return False
    
    async def export_data_to_csv(self, output_dir: str = "exports"):
        """Экспорт данных в CSV файлы"""
        try:
            import csv
            import os
            from pathlib import Path
            
            # Создаем директорию для экспорта
            Path(output_dir).mkdir(exist_ok=True)
            
            async with aiosqlite.connect(DATABASE_PATH) as conn:
                tables = ['users', 'chats', 'rewards', 'chat_activity']
                
                for table in tables:
                    # Получаем данные из таблицы
                    cursor = await conn.execute(f"SELECT * FROM {table}")
                    rows = await cursor.fetchall()
                    
                    if rows:
                        # Получаем названия колонок
                        cursor = await conn.execute(f"PRAGMA table_info({table})")
                        columns = [column[1] for column in await cursor.fetchall()]
                        
                        # Записываем в CSV
                        csv_path = os.path.join(output_dir, f"{table}.csv")
                        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                            writer = csv.writer(csvfile)
                            writer.writerow(columns)
                            writer.writerows(rows)
                        
                        logger.info(f"Экспортировано {len(rows)} записей в {csv_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка экспорта данных: {e}")
            return False
    
    async def health_check(self) -> Dict:
        """Проверка здоровья системы"""
        try:
            health = {
                'database_accessible': False,
                'tables_exist': False,
                'recent_activity': False,
                'errors': []
            }
            
            # Проверяем доступность базы данных
            try:
                async with aiosqlite.connect(DATABASE_PATH) as conn:
                    health['database_accessible'] = True
                    
                    # Проверяем существование таблиц
                    cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [row[0] for row in await cursor.fetchall()]
                    expected_tables = ['users', 'chats', 'rewards', 'chat_activity']
                    
                    if all(table in tables for table in expected_tables):
                        health['tables_exist'] = True
                    else:
                        health['errors'].append("Не все таблицы существуют")
                    
                    # Проверяем недавнюю активность
                    cursor = await conn.execute(
                        "SELECT COUNT(*) FROM chat_activity WHERE last_message_date >= datetime('now', '-1 day')"
                    )
                    recent_count = (await cursor.fetchone())[0]
                    health['recent_activity'] = recent_count > 0
                    
            except Exception as e:
                health['errors'].append(f"Ошибка доступа к БД: {e}")
            
            # Общая оценка здоровья
            health['overall_health'] = all([
                health['database_accessible'],
                health['tables_exist'],
                health['recent_activity']
            ])
            
            return health
            
        except Exception as e:
            logger.error(f"Ошибка проверки здоровья: {e}")
            return {'overall_health': False, 'errors': [str(e)]}

# Функции для работы с файлами конфигурации
def validate_config() -> List[str]:
    """Проверка конфигурации"""
    errors = []
    
    try:
        from config import BOT_TOKEN, ADMIN_ID
        
        if not BOT_TOKEN:
            errors.append("BOT_TOKEN не установлен")
        elif len(BOT_TOKEN) < 10:
            errors.append("BOT_TOKEN слишком короткий")
        
        if not ADMIN_ID:
            errors.append("ADMIN_ID не установлен")
        elif ADMIN_ID <= 0:
            errors.append("ADMIN_ID должен быть положительным числом")
            
    except ImportError as e:
        errors.append(f"Ошибка импорта конфигурации: {e}")
    
    return errors

def format_file_size(size_bytes: int) -> str:
    """Форматирование размера файла"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"