import asyncio
import logging
from datetime import datetime
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, ChatMemberUpdatedFilter, KICKED, LEFT, MEMBER, ADMINISTRATOR, CREATOR
from aiogram.types import ChatMemberUpdated, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BOT_TOKEN, ADMIN_ID, REWARD_COEFFICIENT
from database import Database
from chat_analyzer import ChatAnalyzer
from admin_commands import AdminCommands

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Инициализация базы данных и анализатора
db = Database()
analyzer = ChatAnalyzer()
admin_commands = AdminCommands(bot, db, analyzer)

@dp.message(Command("start"))
async def start_command(message: Message):
    """Обработчик команды /start"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        
        # Добавляем пользователя в базу данных
        await db.add_user(user_id, username)
        
        welcome_text = (
            "🤖 <b>Добро пожаловать в Reward Bot!</b>\n\n"
            "Я бот для анализа активности чатов и выдачи вознаграждений.\n\n"
            "<b>Как это работает:</b>\n"
            "• Добавьте меня в чат\n"
            "• Я буду анализировать активность участников\n"
            "• За активные чаты вы получите вознаграждение\n\n"
            "<b>Команды:</b>\n"
            "/start - Начать работу\n"
            "/help - Помощь\n"
            "/my_rewards - Мои вознаграждения\n\n"
            "Для администраторов доступны дополнительные команды."
        )
        
        await message.answer(welcome_text, parse_mode="HTML")
        logger.info(f"Пользователь {user_id} ({username}) запустил бота")
        
    except Exception as e:
        logger.error(f"Ошибка в команде /start: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

@dp.message(Command("help"))
async def help_command(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "📖 <b>Справка по боту</b>\n\n"
        "<b>Основные функции:</b>\n"
        "• Анализ активности чатов\n"
        "• Выдача вознаграждений за активные чаты\n"
        "• Защита от накрутки\n\n"
        "<b>Как получить вознаграждение:</b>\n"
        "1. Добавьте бота в чат\n"
        "2. Участники чата должны быть активными\n"
        "3. Чем больше сообщений и активных пользователей, тем больше награда\n\n"
        "<b>Команды:</b>\n"
        "/start - Начать работу\n"
        "/my_rewards - Посмотреть мои вознаграждения\n"
        "/help - Эта справка\n\n"
        "Вознаграждения рассчитываются автоматически на основе активности чата."
    )
    
    await message.answer(help_text, parse_mode="HTML")

@dp.message(Command("my_rewards"))
async def my_rewards_command(message: Message):
    """Показать вознаграждения пользователя"""
    try:
        user_id = message.from_user.id
        rewards = await db.get_user_rewards(user_id)
        
        if not rewards:
            await message.answer("У вас пока нет вознаграждений. Добавьте бота в активный чат!")
            return
        
        # Подсчитываем общую сумму
        total_amount = sum(reward['reward_amount'] for reward in rewards)
        
        text = f"💰 <b>Ваши вознаграждения</b>\n\n"
        text += f"Общая сумма: <b>{total_amount:.2f}</b>\n\n"
        
        for reward in rewards[:10]:  # Показываем последние 10
            date = datetime.fromisoformat(reward['reward_date']).strftime("%d.%m.%Y %H:%M")
            text += f"• {reward['reward_amount']:.2f} - {reward['chat_title']}\n"
            text += f"  <i>{date}</i>\n\n"
        
        if len(rewards) > 10:
            text += f"... и еще {len(rewards) - 10} вознаграждений"
        
        await message.answer(text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка получения вознаграждений: {e}")
        await message.answer("Произошла ошибка при получении данных.")

# Административные команды
@dp.message(Command("stats"))
async def stats_command(message: Message):
    """Команда /stats - общая статистика"""
    await admin_commands.stats_command(message)

@dp.message(Command("chats"))
async def chats_command(message: Message):
    """Команда /chats - список чатов"""
    await admin_commands.chats_command(message)

@dp.message(Command("rewards"))
async def rewards_command(message: Message):
    """Команда /rewards - список вознаграждений"""
    await admin_commands.rewards_command(message)

@dp.message(Command("analyze_chat"))
async def analyze_chat_command(message: Message):
    """Команда /analyze_chat - анализ конкретного чата"""
    await admin_commands.analyze_chat_command(message)

@dp.message(Command("user_rewards"))
async def user_rewards_command(message: Message):
    """Команда /user_rewards - вознаграждения конкретного пользователя"""
    await admin_commands.user_rewards_command(message)

@dp.message(Command("admin_help"))
async def admin_help_command(message: Message):
    """Команда /admin_help - справка по админ-командам"""
    await admin_commands.help_admin_command(message)

@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED >> MEMBER))
async def bot_added_to_chat(event: ChatMemberUpdated):
    """Обработчик добавления бота в чат"""
    try:
        chat = event.chat
        new_member = event.new_chat_member
        
        # Проверяем, что это добавление бота
        if new_member.user.id != bot.id:
            return
        
        # Получаем информацию о том, кто добавил бота
        # В Telegram API нет прямого способа узнать, кто добавил бота
        # Поэтому будем использовать администратора чата как "добавившего"
        admins = await bot.get_chat_administrators(chat.id)
        added_by_user = None
        
        for admin in admins:
            if admin.status in [ADMINISTRATOR, CREATOR]:
                added_by_user = admin.user
                break
        
        if not added_by_user:
            logger.warning(f"Не удалось определить, кто добавил бота в чат {chat.id}")
            return
        
        # Добавляем чат в базу данных
        chat_title = chat.title or f"Чат {chat.id}"
        success = await db.add_chat(chat.id, chat_title, added_by_user.id)
        
        if success:
            # Отправляем приветственное сообщение
            welcome_text = (
                f"👋 <b>Привет, {chat_title}!</b>\n\n"
                "Я Reward Bot - бот для анализа активности чатов.\n\n"
                "📊 <b>Что я делаю:</b>\n"
                "• Анализирую активность участников\n"
                "• Рассчитываю ценность чата\n"
                "• Выдаю вознаграждения за активность\n\n"
                "💡 <b>Совет:</b> Чем активнее участники, тем больше вознаграждение!\n\n"
                "Используйте /help для получения справки."
            )
            
            await bot.send_message(chat.id, welcome_text, parse_mode="HTML")
            
            # Анализируем чат и выдаем первое вознаграждение
            await analyze_and_reward_chat(chat.id, added_by_user.id)
            
            logger.info(f"Бот добавлен в чат {chat.id} ({chat_title}) пользователем {added_by_user.id}")
        else:
            logger.error(f"Ошибка добавления чата {chat.id} в базу данных")
            
    except Exception as e:
        logger.error(f"Ошибка обработки добавления в чат: {e}")

@dp.chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER >> KICKED))
async def bot_removed_from_chat(event: ChatMemberUpdated):
    """Обработчик удаления бота из чата"""
    try:
        chat = event.chat
        old_member = event.old_chat_member
        
        if old_member.user.id == bot.id:
            logger.info(f"Бот удален из чата {chat.id} ({chat.title})")
            
    except Exception as e:
        logger.error(f"Ошибка обработки удаления из чата: {e}")

@dp.message()
async def handle_message(message: Message):
    """Обработчик всех сообщений для анализа активности"""
    try:
        # Игнорируем сообщения от ботов
        if message.from_user.is_bot:
            return
        
        # Игнорируем приватные сообщения
        if message.chat.type == "private":
            return
        
        # Обновляем активность пользователя в чате
        await db.update_chat_activity(message.chat.id, message.from_user.id)
        
        # Периодически анализируем чат (каждое 10-е сообщение)
        if message.message_id % 10 == 0:
            await analyze_and_reward_chat(message.chat.id)
            
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")

async def analyze_and_reward_chat(chat_id: int, added_by_user_id: int = None):
    """Анализ чата и выдача вознаграждения"""
    try:
        # Получаем статистику чата
        stats = await db.get_chat_stats(chat_id)
        
        # Рассчитываем ценность чата
        chat_value = analyzer.calculate_chat_value(stats)
        
        # Обновляем ценность в базе данных
        await db.update_chat_value(chat_id, chat_value)
        
        # Если указан пользователь, который добавил бота, выдаем ему вознаграждение
        if added_by_user_id and chat_value > 0:
            reward_amount = chat_value * REWARD_COEFFICIENT
            
            # Выдаем вознаграждение
            success = await db.add_reward(added_by_user_id, chat_id, reward_amount)
            
            if success:
                # Уведомляем пользователя о вознаграждении
                try:
                    await bot.send_message(
                        added_by_user_id,
                        f"🎉 <b>Получено вознаграждение!</b>\n\n"
                        f"💰 Сумма: <b>{reward_amount:.2f}</b>\n"
                        f"📊 Ценность чата: <b>{chat_value:.2f}</b>\n"
                        f"👥 Активных пользователей: <b>{stats['active_users']}</b>\n"
                        f"💬 Сообщений за сутки: <b>{stats['total_messages']}</b>\n\n"
                        f"Спасибо за добавление активного чата!",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.warning(f"Не удалось отправить уведомление пользователю {added_by_user_id}: {e}")
        
        logger.info(f"Анализ чата {chat_id}: ценность {chat_value}, активных {stats['active_users']}, сообщений {stats['total_messages']}")
        
    except Exception as e:
        logger.error(f"Ошибка анализа чата {chat_id}: {e}")

async def main():
    """Основная функция запуска бота"""
    try:
        # Проверяем наличие токена
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN не установлен! Установите переменную окружения BOT_TOKEN")
            return
        
        # Инициализируем базу данных
        await db.init_db()
        logger.info("База данных инициализирована")
        
        # Запускаем бота
        logger.info("Запуск бота...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())