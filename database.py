import aiosqlite
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
    
    async def init_db(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Таблица пользователей
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        registration_date TEXT NOT NULL,
                        total_rewards REAL DEFAULT 0.0
                    )
                ''')
                
                # Таблица чатов
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS chats (
                        chat_id INTEGER PRIMARY KEY,
                        title TEXT,
                        added_date TEXT NOT NULL,
                        value REAL DEFAULT 0.0,
                        member_count INTEGER DEFAULT 0,
                        last_activity_date TEXT
                    )
                ''')
                
                # Таблица вознаграждений
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS rewards (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        chat_id INTEGER NOT NULL,
                        reward_amount REAL NOT NULL,
                        reward_date TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (user_id),
                        FOREIGN KEY (chat_id) REFERENCES chats (chat_id)
                    )
                ''')
                
                # Таблица активности чатов (для анализа)
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS chat_activity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        message_count INTEGER DEFAULT 1,
                        last_message_date TEXT NOT NULL,
                        FOREIGN KEY (chat_id) REFERENCES chats (chat_id),
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                await db.commit()
                logger.info("База данных успешно инициализирована")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    async def add_user(self, user_id: int, username: str = None) -> bool:
        """Добавление пользователя в базу данных"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR IGNORE INTO users (user_id, username, registration_date)
                    VALUES (?, ?, ?)
                ''', (user_id, username, datetime.now().isoformat()))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя {user_id}: {e}")
            return False
    
    async def add_chat(self, chat_id: int, title: str, added_by_user_id: int) -> bool:
        """Добавление чата в базу данных"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Добавляем чат
                await db.execute('''
                    INSERT OR REPLACE INTO chats (chat_id, title, added_date, last_activity_date)
                    VALUES (?, ?, ?, ?)
                ''', (chat_id, title, datetime.now().isoformat(), datetime.now().isoformat()))
                
                # Добавляем пользователя, если его нет
                await self.add_user(added_by_user_id)
                
                await db.commit()
                logger.info(f"Чат {chat_id} ({title}) добавлен пользователем {added_by_user_id}")
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления чата {chat_id}: {e}")
            return False
    
    async def add_reward(self, user_id: int, chat_id: int, reward_amount: float) -> bool:
        """Добавление вознаграждения"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Добавляем запись о вознаграждении
                await db.execute('''
                    INSERT INTO rewards (user_id, chat_id, reward_amount, reward_date)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, chat_id, reward_amount, datetime.now().isoformat()))
                
                # Обновляем общую сумму вознаграждений пользователя
                await db.execute('''
                    UPDATE users SET total_rewards = total_rewards + ?
                    WHERE user_id = ?
                ''', (reward_amount, user_id))
                
                await db.commit()
                logger.info(f"Вознаграждение {reward_amount} выдано пользователю {user_id} за чат {chat_id}")
                return True
        except Exception as e:
            logger.error(f"Ошибка добавления вознаграждения: {e}")
            return False
    
    async def update_chat_activity(self, chat_id: int, user_id: int) -> bool:
        """Обновление активности пользователя в чате"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Добавляем или обновляем активность
                await db.execute('''
                    INSERT INTO chat_activity (chat_id, user_id, message_count, last_message_date)
                    VALUES (?, ?, 1, ?)
                    ON CONFLICT(chat_id, user_id) DO UPDATE SET
                        message_count = message_count + 1,
                        last_message_date = ?
                ''', (chat_id, user_id, datetime.now().isoformat(), datetime.now().isoformat()))
                
                # Обновляем дату последней активности чата
                await db.execute('''
                    UPDATE chats SET last_activity_date = ?
                    WHERE chat_id = ?
                ''', (datetime.now().isoformat(), chat_id))
                
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка обновления активности: {e}")
            return False
    
    async def get_chat_stats(self, chat_id: int) -> Dict:
        """Получение статистики чата за последние 24 часа"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Получаем количество уникальных активных пользователей за сутки
                cursor = await db.execute('''
                    SELECT COUNT(DISTINCT user_id) as active_users
                    FROM chat_activity
                    WHERE chat_id = ? AND last_message_date >= datetime('now', '-1 day')
                ''', (chat_id,))
                active_users = (await cursor.fetchone())[0]
                
                # Получаем общее количество сообщений за сутки
                cursor = await db.execute('''
                    SELECT SUM(message_count) as total_messages
                    FROM chat_activity
                    WHERE chat_id = ? AND last_message_date >= datetime('now', '-1 day')
                ''', (chat_id,))
                total_messages = (await cursor.fetchone())[0] or 0
                
                # Получаем информацию о чате
                cursor = await db.execute('''
                    SELECT member_count, value FROM chats WHERE chat_id = ?
                ''', (chat_id,))
                chat_info = await cursor.fetchone()
                member_count = chat_info[0] if chat_info else 0
                current_value = chat_info[1] if chat_info else 0.0
                
                return {
                    'active_users': active_users,
                    'total_messages': total_messages,
                    'member_count': member_count,
                    'current_value': current_value
                }
        except Exception as e:
            logger.error(f"Ошибка получения статистики чата {chat_id}: {e}")
            return {'active_users': 0, 'total_messages': 0, 'member_count': 0, 'current_value': 0.0}
    
    async def update_chat_value(self, chat_id: int, value: float) -> bool:
        """Обновление ценности чата"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE chats SET value = ? WHERE chat_id = ?
                ''', (value, chat_id))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка обновления ценности чата {chat_id}: {e}")
            return False
    
    async def get_all_chats(self) -> List[Dict]:
        """Получение списка всех чатов"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute('''
                    SELECT chat_id, title, added_date, value, member_count, last_activity_date
                    FROM chats ORDER BY value DESC
                ''')
                rows = await cursor.fetchall()
                return [{
                    'chat_id': row[0],
                    'title': row[1],
                    'added_date': row[2],
                    'value': row[3],
                    'member_count': row[4],
                    'last_activity_date': row[5]
                } for row in rows]
        except Exception as e:
            logger.error(f"Ошибка получения списка чатов: {e}")
            return []
    
    async def get_user_rewards(self, user_id: int = None) -> List[Dict]:
        """Получение списка вознаграждений"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if user_id:
                    cursor = await db.execute('''
                        SELECT r.user_id, r.chat_id, r.reward_amount, r.reward_date, c.title
                        FROM rewards r
                        JOIN chats c ON r.chat_id = c.chat_id
                        WHERE r.user_id = ?
                        ORDER BY r.reward_date DESC
                    ''', (user_id,))
                else:
                    cursor = await db.execute('''
                        SELECT r.user_id, r.chat_id, r.reward_amount, r.reward_date, c.title
                        FROM rewards r
                        JOIN chats c ON r.chat_id = c.chat_id
                        ORDER BY r.reward_date DESC
                    ''')
                
                rows = await cursor.fetchall()
                return [{
                    'user_id': row[0],
                    'chat_id': row[1],
                    'reward_amount': row[2],
                    'reward_date': row[3],
                    'chat_title': row[4]
                } for row in rows]
        except Exception as e:
            logger.error(f"Ошибка получения вознаграждений: {e}")
            return []
    
    async def get_stats(self) -> Dict:
        """Получение общей статистики"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Общее количество пользователей
                cursor = await db.execute('SELECT COUNT(*) FROM users')
                total_users = (await cursor.fetchone())[0]
                
                # Общее количество чатов
                cursor = await db.execute('SELECT COUNT(*) FROM chats')
                total_chats = (await cursor.fetchone())[0]
                
                # Общая сумма вознаграждений
                cursor = await db.execute('SELECT SUM(reward_amount) FROM rewards')
                total_rewards = (await cursor.fetchone())[0] or 0.0
                
                # Средняя ценность чатов
                cursor = await db.execute('SELECT AVG(value) FROM chats WHERE value > 0')
                avg_chat_value = (await cursor.fetchone())[0] or 0.0
                
                return {
                    'total_users': total_users,
                    'total_chats': total_chats,
                    'total_rewards': total_rewards,
                    'avg_chat_value': avg_chat_value
                }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {'total_users': 0, 'total_chats': 0, 'total_rewards': 0.0, 'avg_chat_value': 0.0}