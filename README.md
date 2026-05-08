# 🍕 Bitcoin Pizza Fest 2026 — Telegram Bot

Бот для регистрации участников мероприятия. Поддерживает 3 языка: RU, UZ, EN.

## Структура проекта

```
pizza_bot/
├── bot.py              # точка входа
├── config.py           # токен и admin IDs из .env
├── db.py               # работа с SQLite
├── texts.py            # все тексты на 3 языках
├── keyboards.py        # клавиатуры
├── handlers/
│   ├── user.py         # регистрация пользователей
│   └── admin.py        # админ-команды
├── .env                # секреты (не коммитить в git!)
├── requirements.txt
└── README.md
```

## Быстрый старт (локально)

### 1. Клонируй репозиторий / распакуй архив

### 2. Создай и активируй виртуальное окружение
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Установи зависимости
```bash
pip install -r requirements.txt
```

### 4. Настрой .env
```
BOT_TOKEN=твой_токен_от_BotFather
ADMIN_IDS=твой_telegram_id
```

Несколько админов — через запятую:
```
ADMIN_IDS=123456789,987654321
```

### 5. Запусти бота
```bash
python bot.py
```

---

## Деплой на Railway (бесплатный хостинг)

1. Зарегистрируйся на [railway.app](https://railway.app)
2. Создай новый проект → Deploy from GitHub repo
3. Добавь переменные окружения в Settings → Variables:
   - `BOT_TOKEN`
   - `ADMIN_IDS`
4. Railway сам установит зависимости из `requirements.txt` и запустит `bot.py`

---

## Деплой на VPS (Ubuntu)

```bash
# 1. Установи Python
sudo apt update && sudo apt install python3 python3-pip python3-venv -y

# 2. Скопируй файлы на сервер и войди в папку
cd pizza_bot

# 3. Создай окружение
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Создай .env файл
nano .env

# 5. Запусти как systemd-сервис (работает 24/7)
sudo nano /etc/systemd/system/pizza_bot.service
```

Содержимое сервиса:
```ini
[Unit]
Description=Bitcoin Pizza Fest Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/pizza_bot
ExecStart=/home/ubuntu/pizza_bot/venv/bin/python bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable pizza_bot
sudo systemctl start pizza_bot
sudo systemctl status pizza_bot
```

---

## Команды бота

### Для пользователей
- `/start` — начать регистрацию

### Для администраторов
- `/admin` — панель с статистикой
- `/users` — количество участников
- `/export` — скачать базу в Excel
- `/broadcast` — рассылка (с выбором аудитории: все / RU / UZ / EN)

---

## База данных

Хранится в файле `users.db` (SQLite).

Таблица `users`:
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Автоинкремент |
| telegram_id | INTEGER | Уникальный ID пользователя |
| username | TEXT | @username |
| language | TEXT | ru / uz / en |
| full_name | TEXT | Имя и фамилия |
| phone | TEXT | Номер телефона |
| registered_at | TEXT | Дата и время регистрации |
| is_active | INTEGER | 1 = активен, 0 = заблокировал бота |
