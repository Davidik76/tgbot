#!/bin/bash

# Скрипт запуска Reward Bot

echo "🚀 Запуск Reward Bot..."

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

# Проверяем наличие pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден. Установите pip"
    exit 1
fi

# Создаем виртуальное окружение, если его нет
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Устанавливаем зависимости
echo "📚 Установка зависимостей..."
pip install -r requirements.txt

# Проверяем наличие файла .env
if [ ! -f ".env" ]; then
    echo "⚠️  Файл .env не найден. Создаю из примера..."
    cp .env.example .env
    echo "📝 Отредактируйте файл .env и добавьте BOT_TOKEN и ADMIN_ID"
    echo "   Затем запустите скрипт снова"
    exit 1
fi

# Инициализируем базу данных
echo "🗄️  Инициализация базы данных..."
python init_db.py

# Запускаем бота
echo "🤖 Запуск бота..."
python run.py