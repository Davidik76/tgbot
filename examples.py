"""
Примеры использования Reward Bot
"""

import asyncio
from database import Database
from chat_analyzer import ChatAnalyzer
from utils import BotUtils

async def example_usage():
    """Примеры использования компонентов бота"""
    
    # Инициализация
    db = Database()
    analyzer = ChatAnalyzer()
    utils = BotUtils(db)
    
    print("🔧 Примеры использования Reward Bot\n")
    
    # 1. Добавление пользователя
    print("1. Добавление пользователя:")
    success = await db.add_user(123456789, "example_user")
    print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
    
    # 2. Добавление чата
    print("\n2. Добавление чата:")
    success = await db.add_chat(-1001234567890, "Пример чата", 123456789)
    print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
    
    # 3. Обновление активности
    print("\n3. Обновление активности:")
    success = await db.update_chat_activity(-1001234567890, 123456789)
    print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
    
    # 4. Получение статистики чата
    print("\n4. Статистика чата:")
    stats = await db.get_chat_stats(-1001234567890)
    print(f"   Активных пользователей: {stats['active_users']}")
    print(f"   Сообщений: {stats['total_messages']}")
    print(f"   Участников: {stats['member_count']}")
    
    # 5. Анализ ценности чата
    print("\n5. Анализ ценности чата:")
    chat_value = analyzer.calculate_chat_value(stats)
    print(f"   Ценность чата: {chat_value}")
    
    # 6. Анализ здоровья чата
    print("\n6. Анализ здоровья чата:")
    health = analyzer.analyze_chat_health(stats)
    print(f"   Оценка здоровья: {health['health_score']}/100")
    print(f"   Статус: {health['health_status']}")
    print(f"   Уровень вовлеченности: {health['engagement_level']}")
    
    # 7. Выдача вознаграждения
    print("\n7. Выдача вознаграждения:")
    reward_amount = chat_value * 0.1  # 10% от ценности
    success = await db.add_reward(123456789, -1001234567890, reward_amount)
    print(f"   Сумма вознаграждения: {reward_amount:.2f}")
    print(f"   Результат: {'✅ Успешно' if success else '❌ Ошибка'}")
    
    # 8. Получение статистики
    print("\n8. Общая статистика:")
    stats = await db.get_stats()
    print(f"   Всего пользователей: {stats['total_users']}")
    print(f"   Всего чатов: {stats['total_chats']}")
    print(f"   Общая сумма вознаграждений: {stats['total_rewards']:.2f}")
    print(f"   Средняя ценность чата: {stats['avg_chat_value']:.2f}")
    
    # 9. Проверка здоровья системы
    print("\n9. Проверка здоровья системы:")
    health = await utils.health_check()
    print(f"   Общее состояние: {'✅ Здорово' if health['overall_health'] else '❌ Проблемы'}")
    print(f"   База данных: {'✅ Доступна' if health['database_accessible'] else '❌ Недоступна'}")
    print(f"   Таблицы: {'✅ Существуют' if health['tables_exist'] else '❌ Отсутствуют'}")
    
    print("\n✅ Примеры выполнены!")

def example_config():
    """Пример конфигурации"""
    print("⚙️  Пример конфигурации (.env файл):")
    print("""
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID=123456789
    """)
    
    print("📋 Объяснение параметров:")
    print("• BOT_TOKEN - токен бота от @BotFather")
    print("• ADMIN_ID - ваш Telegram ID (получить у @userinfobot)")

def example_commands():
    """Примеры команд"""
    print("🤖 Примеры команд бота:")
    print("""
Пользовательские команды:
/start - Начать работу с ботом
/help - Справка по использованию
/my_rewards - Посмотреть свои вознаграждения

Административные команды:
/stats - Общая статистика бота
/chats - Список всех чатов
/rewards - Статистика вознаграждений
/analyze_chat -1001234567890 - Анализ конкретного чата
/user_rewards 123456789 - Вознаграждения пользователя
/admin_help - Справка по админ-командам
    """)

def example_maintenance():
    """Примеры обслуживания"""
    print("🔧 Примеры обслуживания:")
    print("""
# Создание резервной копии
python maintenance.py backup

# Очистка старых данных (старше 7 дней)
python maintenance.py cleanup --days 7

# Оптимизация базы данных
python maintenance.py optimize

# Экспорт данных в CSV
python maintenance.py export

# Проверка здоровья системы
python maintenance.py health

# Показать статистику
python maintenance.py stats

# Полное обслуживание
python maintenance.py all
    """)

if __name__ == "__main__":
    print("📚 Примеры использования Reward Bot\n")
    
    print("Выберите пример:")
    print("1. Примеры использования компонентов")
    print("2. Пример конфигурации")
    print("3. Примеры команд")
    print("4. Примеры обслуживания")
    print("5. Все примеры")
    
    choice = input("\nВведите номер (1-5): ").strip()
    
    if choice == "1":
        asyncio.run(example_usage())
    elif choice == "2":
        example_config()
    elif choice == "3":
        example_commands()
    elif choice == "4":
        example_maintenance()
    elif choice == "5":
        asyncio.run(example_usage())
        print("\n" + "="*50 + "\n")
        example_config()
        print("\n" + "="*50 + "\n")
        example_commands()
        print("\n" + "="*50 + "\n")
        example_maintenance()
    else:
        print("❌ Неверный выбор")