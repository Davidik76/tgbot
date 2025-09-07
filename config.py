import os
from typing import Optional

# Загружаем переменные окружения из .env файла
try:
    from load_env import load_env_file
    load_env_file()
except ImportError:
    pass

# Токен бота (получите у @BotFather)
BOT_TOKEN: Optional[str] = os.getenv('BOT_TOKEN')

# ID администратора (ваш Telegram ID)
try:
    ADMIN_ID: Optional[int] = int(os.getenv('ADMIN_ID', '0'))
except ValueError:
    ADMIN_ID: Optional[int] = None

# Настройки базы данных
DATABASE_PATH = 'bot_database.db'

# Коэффициенты для расчета вознаграждений
REWARD_COEFFICIENT = 0.1  # Базовый коэффициент вознаграждения
MIN_CHAT_VALUE = 1.0      # Минимальная ценность чата
MAX_CHAT_VALUE = 100.0    # Максимальная ценность чата

# Настройки логирования
LOG_LEVEL = 'INFO'
LOG_FILE = 'bot.log'