# Инструкция по установке Reward Bot

## Проблема с Python 3.13

Текущая версия Python 3.13 слишком новая для библиотек aiogram и pydantic. Рекомендуется использовать Python 3.11 или 3.12.

## Рекомендуемые версии Python

- **Python 3.11** (рекомендуется)
- **Python 3.12** (также поддерживается)
- **Python 3.10** (минимальная версия)

## Установка на Ubuntu/Debian

### 1. Установка Python 3.11

```bash
# Обновление пакетов
sudo apt update

# Установка Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-pip

# Создание символической ссылки (опционально)
sudo ln -sf /usr/bin/python3.11 /usr/bin/python3
```

### 2. Создание виртуального окружения

```bash
# Переход в директорию проекта
cd /path/to/reward-bot

# Создание виртуального окружения
python3.11 -m venv venv

# Активация виртуального окружения
source venv/bin/activate

# Обновление pip
pip install --upgrade pip
```

### 3. Установка зависимостей

```bash
# Установка зависимостей
pip install -r requirements.txt
```

## Установка на Windows

### 1. Скачивание Python 3.11

1. Перейдите на https://www.python.org/downloads/
2. Скачайте Python 3.11.x
3. Установите с галочкой "Add Python to PATH"

### 2. Создание виртуального окружения

```cmd
# В командной строке
cd C:\path\to\reward-bot
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Установка на macOS

### 1. Установка через Homebrew

```bash
# Установка Homebrew (если не установлен)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установка Python 3.11
brew install python@3.11

# Создание виртуального окружения
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Альтернативный способ - Docker

Если у вас проблемы с установкой Python, используйте Docker:

### 1. Создание Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run.py"]
```

### 2. Сборка и запуск

```bash
# Сборка образа
docker build -t reward-bot .

# Запуск контейнера
docker run -d --name reward-bot \
  -e BOT_TOKEN=your_bot_token_here \
  -e ADMIN_ID=your_admin_id_here \
  reward-bot
```

## Проверка установки

После установки проверьте работоспособность:

```bash
# Активация виртуального окружения
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Проверка версии Python
python --version

# Проверка установленных пакетов
pip list

# Тестовый запуск
python -c "import aiogram, aiosqlite; print('Все пакеты установлены успешно!')"
```

## Настройка переменных окружения

1. Скопируйте `.env.example` в `.env`:
   ```bash
   cp .env.example .env
   ```

2. Отредактируйте `.env` файл:
   ```
   BOT_TOKEN=5711216312:AAHIk8FBpar0i69huSvwg1fzc0-zvx-xdN4
   ADMIN_ID=1147574990
   ```

## Запуск бота

```bash
# Инициализация базы данных
python init_db.py

# Запуск бота
python run.py
```

## Решение проблем

### Ошибка "No module named 'aiogram'"

```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate

# Переустановите зависимости
pip install -r requirements.txt
```

### Ошибка "Permission denied"

```bash
# На Linux/macOS
chmod +x run.py
chmod +x init_db.py
chmod +x maintenance.py
```

### Ошибка "BOT_TOKEN not found"

```bash
# Проверьте файл .env
cat .env

# Убедитесь, что токен указан правильно
```

## Поддержка

Если у вас возникли проблемы:

1. Проверьте версию Python: `python --version`
2. Убедитесь, что виртуальное окружение активировано
3. Проверьте логи: `tail -f bot.log`
4. Запустите проверку здоровья: `python maintenance.py health`