import logging
from datetime import datetime, timedelta
from typing import Dict
from config import MIN_CHAT_VALUE, MAX_CHAT_VALUE

logger = logging.getLogger(__name__)

class ChatAnalyzer:
    """Класс для анализа активности чатов и расчета их ценности"""
    
    def __init__(self):
        self.min_value = MIN_CHAT_VALUE
        self.max_value = MAX_CHAT_VALUE
    
    def calculate_chat_value(self, stats: Dict) -> float:
        """
        Расчет ценности чата на основе статистики
        
        Args:
            stats: Словарь со статистикой чата
                - active_users: количество активных пользователей за сутки
                - total_messages: общее количество сообщений за сутки
                - member_count: общее количество участников чата
        
        Returns:
            float: Ценность чата
        """
        try:
            active_users = stats.get('active_users', 0)
            total_messages = stats.get('total_messages', 0)
            member_count = stats.get('member_count', 0)
            
            # Если нет активности, ценность минимальная
            if active_users == 0 or total_messages == 0:
                return self.min_value
            
            # Защита от накрутки: проверяем соотношение активных к общему количеству участников
            if member_count > 0:
                activity_ratio = active_users / member_count
                
                # Если активных пользователей меньше 5% от общего количества - подозрительно
                if activity_ratio < 0.05:
                    logger.warning(f"Подозрительно низкая активность: {activity_ratio:.2%}")
                    # Снижаем ценность
                    activity_penalty = activity_ratio * 2  # Максимум 10% от обычной ценности
                else:
                    activity_penalty = 1.0
            else:
                activity_penalty = 1.0
            
            # Базовый расчет ценности
            # Учитываем количество активных пользователей и сообщений
            base_value = (active_users * 2) + (total_messages * 0.5)
            
            # Коэффициент вовлеченности (сообщения на активного пользователя)
            engagement_ratio = total_messages / active_users if active_users > 0 else 0
            
            # Бонус за высокую вовлеченность
            if engagement_ratio > 10:  # Более 10 сообщений на пользователя
                engagement_bonus = 1.5
            elif engagement_ratio > 5:  # Более 5 сообщений на пользователя
                engagement_bonus = 1.2
            else:
                engagement_bonus = 1.0
            
            # Итоговая ценность с учетом всех факторов
            final_value = base_value * engagement_bonus * activity_penalty
            
            # Ограничиваем значение в заданных пределах
            final_value = max(self.min_value, min(final_value, self.max_value))
            
            logger.info(f"Ценность чата: {final_value:.2f} "
                       f"(активных: {active_users}, сообщений: {total_messages}, "
                       f"участников: {member_count}, вовлеченность: {engagement_ratio:.2f})")
            
            return round(final_value, 2)
            
        except Exception as e:
            logger.error(f"Ошибка расчета ценности чата: {e}")
            return self.min_value
    
    def get_engagement_level(self, stats: Dict) -> str:
        """Определение уровня вовлеченности чата"""
        try:
            active_users = stats.get('active_users', 0)
            total_messages = stats.get('total_messages', 0)
            member_count = stats.get('member_count', 0)
            
            if active_users == 0 or total_messages == 0:
                return "Нет активности"
            
            engagement_ratio = total_messages / active_users
            activity_ratio = active_users / member_count if member_count > 0 else 0
            
            if engagement_ratio > 15 and activity_ratio > 0.3:
                return "Очень высокая"
            elif engagement_ratio > 10 and activity_ratio > 0.2:
                return "Высокая"
            elif engagement_ratio > 5 and activity_ratio > 0.1:
                return "Средняя"
            elif engagement_ratio > 2 and activity_ratio > 0.05:
                return "Низкая"
            else:
                return "Очень низкая"
                
        except Exception as e:
            logger.error(f"Ошибка определения уровня вовлеченности: {e}")
            return "Неизвестно"
    
    def analyze_chat_health(self, stats: Dict) -> Dict:
        """Комплексный анализ здоровья чата"""
        try:
            active_users = stats.get('active_users', 0)
            total_messages = stats.get('total_messages', 0)
            member_count = stats.get('member_count', 0)
            
            # Основные метрики
            engagement_ratio = total_messages / active_users if active_users > 0 else 0
            activity_ratio = active_users / member_count if member_count > 0 else 0
            
            # Оценка здоровья чата
            health_score = 0
            
            # Оценка по активности (0-40 баллов)
            if activity_ratio > 0.3:
                health_score += 40
            elif activity_ratio > 0.2:
                health_score += 30
            elif activity_ratio > 0.1:
                health_score += 20
            elif activity_ratio > 0.05:
                health_score += 10
            
            # Оценка по вовлеченности (0-40 баллов)
            if engagement_ratio > 15:
                health_score += 40
            elif engagement_ratio > 10:
                health_score += 30
            elif engagement_ratio > 5:
                health_score += 20
            elif engagement_ratio > 2:
                health_score += 10
            
            # Оценка по количеству сообщений (0-20 баллов)
            if total_messages > 100:
                health_score += 20
            elif total_messages > 50:
                health_score += 15
            elif total_messages > 20:
                health_score += 10
            elif total_messages > 5:
                health_score += 5
            
            # Определение статуса здоровья
            if health_score >= 80:
                health_status = "Отличное"
            elif health_score >= 60:
                health_status = "Хорошее"
            elif health_score >= 40:
                health_status = "Удовлетворительное"
            elif health_score >= 20:
                health_status = "Плохое"
            else:
                health_status = "Критическое"
            
            return {
                'health_score': health_score,
                'health_status': health_status,
                'engagement_ratio': round(engagement_ratio, 2),
                'activity_ratio': round(activity_ratio, 2),
                'engagement_level': self.get_engagement_level(stats),
                'recommendations': self._get_recommendations(health_score, activity_ratio, engagement_ratio)
            }
            
        except Exception as e:
            logger.error(f"Ошибка анализа здоровья чата: {e}")
            return {
                'health_score': 0,
                'health_status': 'Неизвестно',
                'engagement_ratio': 0,
                'activity_ratio': 0,
                'engagement_level': 'Неизвестно',
                'recommendations': ['Ошибка анализа']
            }
    
    def _get_recommendations(self, health_score: int, activity_ratio: float, engagement_ratio: float) -> list:
        """Получение рекомендаций по улучшению чата"""
        recommendations = []
        
        if activity_ratio < 0.1:
            recommendations.append("Низкая активность участников - рассмотрите способы мотивации")
        
        if engagement_ratio < 3:
            recommendations.append("Низкая вовлеченность - попробуйте более интересные темы для обсуждения")
        
        if health_score < 40:
            recommendations.append("Общее состояние чата требует внимания - проведите модерацию")
        
        if not recommendations:
            recommendations.append("Чат в хорошем состоянии, продолжайте в том же духе!")
        
        return recommendations