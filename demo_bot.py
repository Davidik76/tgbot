#!/usr/bin/env python3
"""
Демонстрационная версия Reward Bot без aiogram
Показывает основную функциональность системы
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List

from database import Database
from chat_analyzer import ChatAnalyzer
from utils import BotUtils

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DemoBot:
    """Демонстрационная версия бота"""
    
    def __init__(self):
        self.db = Database()
        self.analyzer = ChatAnalyzer()
        self.utils = BotUtils(self.db)
    
    async def demo_workflow(self):
        """Демонстрация основного рабочего процесса"""
        print("🚀 Демонстрация Reward Bot\n")
        
        # 1. Инициализация базы данных
        print("1️⃣ Инициализация базы данных...")
        await self.db.init_db()
        print("✅ База данных инициализирована\n")
        
        # 2. Добавление тестовых пользователей
        print("2️⃣ Добавление тестовых пользователей...")
        test_users = [
            (1147574990, "admin_user"),
            (123456789, "test_user_1"),
            (987654321, "test_user_2"),
            (555666777, "test_user_3")
        ]
        
        for user_id, username in test_users:
            await self.db.add_user(user_id, username)
            print(f"   ✅ Пользователь {username} ({user_id}) добавлен")
        print()
        
        # 3. Добавление тестовых чатов
        print("3️⃣ Добавление тестовых чатов...")
        test_chats = [
            (-1001234567890, "Активный чат разработчиков", 1147574990),
            (-1001234567891, "Чат с низкой активностью", 123456789),
            (-1001234567892, "Очень активный чат", 987654321)
        ]
        
        for chat_id, title, added_by in test_chats:
            await self.db.add_chat(chat_id, title, added_by)
            print(f"   ✅ Чат '{title}' ({chat_id}) добавлен пользователем {added_by}")
        print()
        
        # 4. Симуляция активности в чатах
        print("4️⃣ Симуляция активности в чатах...")
        
        # Активный чат - много сообщений
        active_chat = -1001234567890
        for i in range(50):
            user_id = test_users[i % len(test_users)][0]
            await self.db.update_chat_activity(active_chat, user_id)
        print(f"   ✅ Активный чат: 50 сообщений от {len(test_users)} пользователей")
        
        # Чат с низкой активностью
        low_activity_chat = -1001234567891
        for i in range(5):
            user_id = test_users[i % 2][0]  # Только 2 пользователя
            await self.db.update_chat_activity(low_activity_chat, user_id)
        print(f"   ✅ Чат с низкой активностью: 5 сообщений от 2 пользователей")
        
        # Очень активный чат
        very_active_chat = -1001234567892
        for i in range(100):
            user_id = test_users[i % len(test_users)][0]
            await self.db.update_chat_activity(very_active_chat, user_id)
        print(f"   ✅ Очень активный чат: 100 сообщений от {len(test_users)} пользователей")
        print()
        
        # 5. Анализ ценности чатов
        print("5️⃣ Анализ ценности чатов...")
        for chat_id, title, _ in test_chats:
            stats = await self.db.get_chat_stats(chat_id)
            value = self.analyzer.calculate_chat_value(stats)
            health = self.analyzer.analyze_chat_health(stats)
            
            await self.db.update_chat_value(chat_id, value)
            
            print(f"   📊 Чат: {title}")
            print(f"      💎 Ценность: {value:.2f}")
            print(f"      👥 Активных пользователей: {stats['active_users']}")
            print(f"      💬 Сообщений: {stats['total_messages']}")
            print(f"      🏥 Здоровье: {health['health_status']} ({health['health_score']}/100)")
            print(f"      📈 Вовлеченность: {health['engagement_level']}")
            print()
        
        # 6. Выдача вознаграждений
        print("6️⃣ Выдача вознаграждений...")
        for chat_id, title, added_by in test_chats:
            stats = await self.db.get_chat_stats(chat_id)
            value = self.analyzer.calculate_chat_value(stats)
            reward_amount = value * 0.1  # 10% от ценности
            
            if reward_amount > 0:
                await self.db.add_reward(added_by, chat_id, reward_amount)
                print(f"   💰 {added_by}: {reward_amount:.2f} за чат '{title}'")
        print()
        
        # 7. Показать статистику
        print("7️⃣ Общая статистика...")
        stats = await self.db.get_stats()
        print(f"   👥 Всего пользователей: {stats['total_users']}")
        print(f"   💬 Всего чатов: {stats['total_chats']}")
        print(f"   💰 Общая сумма вознаграждений: {stats['total_rewards']:.2f}")
        print(f"   📈 Средняя ценность чата: {stats['avg_chat_value']:.2f}")
        print()
        
        # 8. Показать вознаграждения пользователей
        print("8️⃣ Вознаграждения пользователей...")
        for user_id, username in test_users:
            rewards = await self.db.get_user_rewards(user_id)
            if rewards:
                total = sum(r['reward_amount'] for r in rewards)
                print(f"   👤 {username} ({user_id}): {total:.2f} ({len(rewards)} вознаграждений)")
        print()
        
        # 9. Проверка здоровья системы
        print("9️⃣ Проверка здоровья системы...")
        health = await self.utils.health_check()
        print(f"   🏥 Общее состояние: {'✅ Здорово' if health['overall_health'] else '❌ Проблемы'}")
        print(f"   🗄️  База данных: {'✅ Доступна' if health['database_accessible'] else '❌ Недоступна'}")
        print(f"   📋 Таблицы: {'✅ Существуют' if health['tables_exist'] else '❌ Отсутствуют'}")
        print(f"   📈 Активность: {'✅ Есть' if health['recent_activity'] else '❌ Нет'}")
        print()
        
        # 10. Экспорт данных
        print("🔟 Экспорт данных...")
        success = await self.utils.export_data_to_csv("demo_exports")
        if success:
            print("   ✅ Данные экспортированы в папку demo_exports/")
        else:
            print("   ❌ Ошибка экспорта данных")
        print()
        
        print("🎉 Демонстрация завершена!")
        print("\n📋 Что было продемонстрировано:")
        print("   • Инициализация базы данных")
        print("   • Добавление пользователей и чатов")
        print("   • Симуляция активности")
        print("   • Анализ ценности чатов")
        print("   • Выдача вознаграждений")
        print("   • Статистика и мониторинг")
        print("   • Экспорт данных")
        print("\n💡 Для полноценной работы установите aiogram с Python 3.11/3.12")

async def main():
    """Основная функция демонстрации"""
    try:
        demo = DemoBot()
        await demo.demo_workflow()
    except Exception as e:
        logger.error(f"Ошибка демонстрации: {e}")
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())