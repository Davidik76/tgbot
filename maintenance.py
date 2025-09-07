#!/usr/bin/env python3
"""
Скрипт для обслуживания бота
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Добавляем текущую директорию в путь для импорта модулей
sys.path.insert(0, str(Path(__file__).parent))

from utils import BotUtils
from database import Database
from config import DATABASE_PATH

async def cleanup_old_data(days: int = 7):
    """Очистка старых данных"""
    print(f"🧹 Очистка данных старше {days} дней...")
    
    utils = BotUtils()
    deleted_count = await utils.cleanup_old_activity(days)
    
    print(f"✅ Удалено {deleted_count} старых записей")
    return deleted_count

async def create_backup():
    """Создание резервной копии"""
    print("💾 Создание резервной копии...")
    
    utils = BotUtils()
    backup_path = await utils.backup_database()
    
    if backup_path:
        print(f"✅ Резервная копия создана: {backup_path}")
    else:
        print("❌ Ошибка создания резервной копии")
    
    return backup_path

async def optimize_database():
    """Оптимизация базы данных"""
    print("⚡ Оптимизация базы данных...")
    
    utils = BotUtils()
    success = await utils.optimize_database()
    
    if success:
        print("✅ База данных оптимизирована")
    else:
        print("❌ Ошибка оптимизации базы данных")
    
    return success

async def export_data():
    """Экспорт данных"""
    print("📤 Экспорт данных...")
    
    utils = BotUtils()
    success = await utils.export_data_to_csv()
    
    if success:
        print("✅ Данные экспортированы в папку exports/")
    else:
        print("❌ Ошибка экспорта данных")
    
    return success

async def health_check():
    """Проверка здоровья системы"""
    print("🏥 Проверка здоровья системы...")
    
    utils = BotUtils()
    health = await utils.health_check()
    
    print(f"📊 Общее состояние: {'✅ Здорово' if health['overall_health'] else '❌ Проблемы'}")
    print(f"🗄️  База данных: {'✅ Доступна' if health['database_accessible'] else '❌ Недоступна'}")
    print(f"📋 Таблицы: {'✅ Существуют' if health['tables_exist'] else '❌ Отсутствуют'}")
    print(f"📈 Активность: {'✅ Есть' if health['recent_activity'] else '❌ Нет'}")
    
    if health['errors']:
        print("⚠️  Ошибки:")
        for error in health['errors']:
            print(f"   • {error}")
    
    return health['overall_health']

async def show_stats():
    """Показать статистику"""
    print("📊 Статистика системы...")
    
    utils = BotUtils()
    stats = await utils.get_database_stats()
    
    if stats:
        print(f"📁 Размер БД: {utils.format_file_size(stats['file_size'])}")
        print(f"👥 Пользователей: {stats.get('users_count', 0)}")
        print(f"💬 Чатов: {stats.get('chats_count', 0)}")
        print(f"💰 Вознаграждений: {stats.get('rewards_count', 0)}")
        print(f"📝 Записей активности: {stats.get('chat_activity_count', 0)}")
        
        if stats.get('first_user_date'):
            print(f"📅 Первый пользователь: {stats['first_user_date']}")
        if stats.get('last_user_date'):
            print(f"📅 Последний пользователь: {stats['last_user_date']}")
    else:
        print("❌ Ошибка получения статистики")

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Скрипт обслуживания Reward Bot")
    parser.add_argument('action', choices=[
        'cleanup', 'backup', 'optimize', 'export', 'health', 'stats', 'all'
    ], help='Действие для выполнения')
    parser.add_argument('--days', type=int, default=7, 
                       help='Количество дней для очистки (по умолчанию: 7)')
    
    args = parser.parse_args()
    
    async def run_action():
        try:
            if args.action == 'cleanup':
                await cleanup_old_data(args.days)
            elif args.action == 'backup':
                await create_backup()
            elif args.action == 'optimize':
                await optimize_database()
            elif args.action == 'export':
                await export_data()
            elif args.action == 'health':
                await health_check()
            elif args.action == 'stats':
                await show_stats()
            elif args.action == 'all':
                print("🔄 Выполнение полного обслуживания...")
                await health_check()
                await create_backup()
                await cleanup_old_data(args.days)
                await optimize_database()
                await show_stats()
                print("✅ Полное обслуживание завершено")
                
        except Exception as e:
            print(f"❌ Ошибка выполнения действия: {e}")
            sys.exit(1)
    
    try:
        asyncio.run(run_action())
    except KeyboardInterrupt:
        print("\n⏹️  Операция прервана пользователем")
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()