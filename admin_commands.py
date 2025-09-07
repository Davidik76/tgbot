import logging
from datetime import datetime
from typing import List, Dict

from aiogram import Bot, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_ID
from database import Database
from chat_analyzer import ChatAnalyzer

logger = logging.getLogger(__name__)

class AdminCommands:
    """Класс для обработки административных команд"""
    
    def __init__(self, bot: Bot, db: Database, analyzer: ChatAnalyzer):
        self.bot = bot
        self.db = db
        self.analyzer = analyzer
    
    def is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором"""
        return user_id == ADMIN_ID
    
    async def stats_command(self, message: Message):
        """Команда /stats - общая статистика"""
        if not self.is_admin(message.from_user.id):
            await message.answer("❌ У вас нет прав для выполнения этой команды.")
            return
        
        try:
            stats = await self.db.get_stats()
            
            # Получаем топ-5 чатов по ценности
            all_chats = await self.db.get_all_chats()
            top_chats = all_chats[:5]
            
            text = "📊 <b>Общая статистика бота</b>\n\n"
            text += f"👥 Всего пользователей: <b>{stats['total_users']}</b>\n"
            text += f"💬 Всего чатов: <b>{stats['total_chats']}</b>\n"
            text += f"💰 Общая сумма вознаграждений: <b>{stats['total_rewards']:.2f}</b>\n"
            text += f"📈 Средняя ценность чата: <b>{stats['avg_chat_value']:.2f}</b>\n\n"
            
            if top_chats:
                text += "🏆 <b>Топ-5 чатов по ценности:</b>\n"
                for i, chat in enumerate(top_chats, 1):
                    date = datetime.fromisoformat(chat['added_date']).strftime("%d.%m.%Y")
                    text += f"{i}. <b>{chat['title']}</b>\n"
                    text += f"   💎 Ценность: {chat['value']:.2f}\n"
                    text += f"   👥 Участников: {chat['member_count']}\n"
                    text += f"   📅 Добавлен: {date}\n\n"
            
            await message.answer(text, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            await message.answer("❌ Ошибка получения статистики.")
    
    async def chats_command(self, message: Message):
        """Команда /chats - список чатов"""
        if not self.is_admin(message.from_user.id):
            await message.answer("❌ У вас нет прав для выполнения этой команды.")
            return
        
        try:
            all_chats = await self.db.get_all_chats()
            
            if not all_chats:
                await message.answer("📭 Чатов пока нет.")
                return
            
            # Создаем клавиатуру для навигации
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(
                text="🔄 Обновить",
                callback_data="refresh_chats"
            ))
            
            text = f"💬 <b>Список чатов ({len(all_chats)})</b>\n\n"
            
            # Показываем первые 10 чатов
            for i, chat in enumerate(all_chats[:10], 1):
                date = datetime.fromisoformat(chat['added_date']).strftime("%d.%m.%Y")
                last_activity = datetime.fromisoformat(chat['last_activity_date']).strftime("%d.%m %H:%M") if chat['last_activity_date'] else "Неизвестно"
                
                text += f"{i}. <b>{chat['title']}</b>\n"
                text += f"   💎 Ценность: {chat['value']:.2f}\n"
                text += f"   👥 Участников: {chat['member_count']}\n"
                text += f"   📅 Добавлен: {date}\n"
                text += f"   🕐 Активность: {last_activity}\n\n"
            
            if len(all_chats) > 10:
                text += f"... и еще {len(all_chats) - 10} чатов"
            
            await message.answer(text, parse_mode="HTML", reply_markup=builder.as_markup())
            
        except Exception as e:
            logger.error(f"Ошибка получения списка чатов: {e}")
            await message.answer("❌ Ошибка получения списка чатов.")
    
    async def rewards_command(self, message: Message):
        """Команда /rewards - список вознаграждений"""
        if not self.is_admin(message.from_user.id):
            await message.answer("❌ У вас нет прав для выполнения этой команды.")
            return
        
        try:
            all_rewards = await self.db.get_user_rewards()
            
            if not all_rewards:
                await message.answer("💰 Вознаграждений пока нет.")
                return
            
            # Подсчитываем статистику
            total_amount = sum(reward['reward_amount'] for reward in all_rewards)
            unique_users = len(set(reward['user_id'] for reward in all_rewards))
            unique_chats = len(set(reward['chat_id'] for reward in all_rewards))
            
            text = f"💰 <b>Статистика вознаграждений</b>\n\n"
            text += f"💵 Общая сумма: <b>{total_amount:.2f}</b>\n"
            text += f"👥 Уникальных пользователей: <b>{unique_users}</b>\n"
            text += f"💬 Уникальных чатов: <b>{unique_chats}</b>\n"
            text += f"📊 Всего выдач: <b>{len(all_rewards)}</b>\n\n"
            
            text += "🏆 <b>Последние 10 вознаграждений:</b>\n"
            for reward in all_rewards[:10]:
                date = datetime.fromisoformat(reward['reward_date']).strftime("%d.%m %H:%M")
                text += f"• <b>{reward['reward_amount']:.2f}</b> - {reward['chat_title']}\n"
                text += f"  👤 Пользователь: {reward['user_id']}\n"
                text += f"  📅 {date}\n\n"
            
            if len(all_rewards) > 10:
                text += f"... и еще {len(all_rewards) - 10} вознаграждений"
            
            await message.answer(text, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Ошибка получения вознаграждений: {e}")
            await message.answer("❌ Ошибка получения вознаграждений.")
    
    async def analyze_chat_command(self, message: Message):
        """Команда /analyze_chat - анализ конкретного чата"""
        if not self.is_admin(message.from_user.id):
            await message.answer("❌ У вас нет прав для выполнения этой команды.")
            return
        
        try:
            # Извлекаем chat_id из команды
            command_parts = message.text.split()
            if len(command_parts) < 2:
                await message.answer("❌ Использование: /analyze_chat <chat_id>")
                return
            
            try:
                chat_id = int(command_parts[1])
            except ValueError:
                await message.answer("❌ Неверный формат chat_id. Используйте числовой ID.")
                return
            
            # Получаем статистику чата
            stats = await self.db.get_chat_stats(chat_id)
            
            if stats['active_users'] == 0 and stats['total_messages'] == 0:
                await message.answer(f"❌ Чат {chat_id} не найден или неактивен.")
                return
            
            # Анализируем чат
            chat_value = self.analyzer.calculate_chat_value(stats)
            health_analysis = self.analyzer.analyze_chat_health(stats)
            
            # Получаем информацию о чате
            all_chats = await self.db.get_all_chats()
            chat_info = next((chat for chat in all_chats if chat['chat_id'] == chat_id), None)
            
            text = f"🔍 <b>Анализ чата {chat_id}</b>\n\n"
            
            if chat_info:
                text += f"📝 Название: <b>{chat_info['title']}</b>\n"
                text += f"👥 Участников: <b>{chat_info['member_count']}</b>\n"
                text += f"📅 Добавлен: <b>{datetime.fromisoformat(chat_info['added_date']).strftime('%d.%m.%Y')}</b>\n\n"
            
            text += f"📊 <b>Статистика за 24 часа:</b>\n"
            text += f"👥 Активных пользователей: <b>{stats['active_users']}</b>\n"
            text += f"💬 Сообщений: <b>{stats['total_messages']}</b>\n"
            text += f"📈 Вовлеченность: <b>{health_analysis['engagement_ratio']}</b>\n"
            text += f"🎯 Активность: <b>{health_analysis['activity_ratio']:.1%}</b>\n\n"
            
            text += f"💎 <b>Оценка:</b>\n"
            text += f"Ценность чата: <b>{chat_value:.2f}</b>\n"
            text += f"Уровень вовлеченности: <b>{health_analysis['engagement_level']}</b>\n"
            text += f"Состояние здоровья: <b>{health_analysis['health_status']}</b>\n"
            text += f"Оценка здоровья: <b>{health_analysis['health_score']}/100</b>\n\n"
            
            text += f"💡 <b>Рекомендации:</b>\n"
            for recommendation in health_analysis['recommendations']:
                text += f"• {recommendation}\n"
            
            await message.answer(text, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Ошибка анализа чата: {e}")
            await message.answer("❌ Ошибка анализа чата.")
    
    async def user_rewards_command(self, message: Message):
        """Команда /user_rewards - вознаграждения конкретного пользователя"""
        if not self.is_admin(message.from_user.id):
            await message.answer("❌ У вас нет прав для выполнения этой команды.")
            return
        
        try:
            # Извлекаем user_id из команды
            command_parts = message.text.split()
            if len(command_parts) < 2:
                await message.answer("❌ Использование: /user_rewards <user_id>")
                return
            
            try:
                user_id = int(command_parts[1])
            except ValueError:
                await message.answer("❌ Неверный формат user_id. Используйте числовой ID.")
                return
            
            # Получаем вознаграждения пользователя
            user_rewards = await self.db.get_user_rewards(user_id)
            
            if not user_rewards:
                await message.answer(f"❌ У пользователя {user_id} нет вознаграждений.")
                return
            
            # Подсчитываем общую сумму
            total_amount = sum(reward['reward_amount'] for reward in user_rewards)
            
            text = f"💰 <b>Вознаграждения пользователя {user_id}</b>\n\n"
            text += f"💵 Общая сумма: <b>{total_amount:.2f}</b>\n"
            text += f"📊 Количество выдач: <b>{len(user_rewards)}</b>\n\n"
            
            text += "📋 <b>История вознаграждений:</b>\n"
            for reward in user_rewards[:15]:  # Показываем последние 15
                date = datetime.fromisoformat(reward['reward_date']).strftime("%d.%m.%Y %H:%M")
                text += f"• <b>{reward['reward_amount']:.2f}</b> - {reward['chat_title']}\n"
                text += f"  📅 {date}\n\n"
            
            if len(user_rewards) > 15:
                text += f"... и еще {len(user_rewards) - 15} вознаграждений"
            
            await message.answer(text, parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Ошибка получения вознаграждений пользователя: {e}")
            await message.answer("❌ Ошибка получения вознаграждений пользователя.")
    
    async def help_admin_command(self, message: Message):
        """Команда /admin_help - справка по админ-командам"""
        if not self.is_admin(message.from_user.id):
            await message.answer("❌ У вас нет прав для выполнения этой команды.")
            return
        
        help_text = (
            "🛠 <b>Административные команды</b>\n\n"
            "<b>Статистика и мониторинг:</b>\n"
            "/stats - Общая статистика бота\n"
            "/chats - Список всех чатов\n"
            "/rewards - Статистика вознаграждений\n\n"
            "<b>Анализ:</b>\n"
            "/analyze_chat <chat_id> - Детальный анализ чата\n"
            "/user_rewards <user_id> - Вознаграждения пользователя\n\n"
            "<b>Справка:</b>\n"
            "/admin_help - Эта справка\n\n"
            "Все команды доступны только администратору бота."
        )
        
        await message.answer(help_text, parse_mode="HTML")