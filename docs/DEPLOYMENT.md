# Руководство по развёртыванию

## Обзор

Данное руководство описывает процесс развёртывания AUTOFLOW OS на production-сервере.

---

## Требования

### Аппаратные требования

| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Disk | 40 GB SSD | 100 GB SSD |
| Network | 100 Mbit/s | 1 Gbit/s |

### Программные требования

| Компонент | Версия |
|-----------|--------|
| OS | Ubuntu 22.04 LTS / Debian 12 |
| Docker | 24.0+ |
| Docker Compose | 2.20+ |
| Git | 2.40+ |

### Внешние сервисы

- Telegram Bot Token (от @BotFather)
- OpenAI API Key или Anthropic API Key
- Доступ к 1С:Предприятие (HTTP Services)
- SMS Gateway API (опционально)

---

## Способ 1: Docker Compose (рекомендуется)

### Шаг 1: Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Установка Docker Compose
sudo apt install docker-compose-plugin -y

# Перелогиниться для применения групп
exit
```

### Шаг 2: Клонирование репозитория

```bash
# Создание директории
sudo mkdir -p /opt/autoflow
sudo chown $USER:$USER /opt/autoflow
cd /opt/autoflow

# Клонирование
git clone https://github.com/hkd7148-blip/autoflow-os.git .
```

### Шаг 3: Настройка окружения

```bash
# Копирование примера конфигурации
cp .env.example .env

# Редактирование конфигурации
nano .env
```

**Обязательные параметры в .env:**

```env
# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ADMIN_IDS=123456789

# Database (изменить пароль!)
POSTGRES_PASSWORD=YourStrongPassword123!
DATABASE_URL=postgresql://autoflow:YourStrongPassword123!@db:5432/autoflow_db

# AI (один из двух)
OPENAI_API_KEY=sk-...
# или
ANTHROPIC_API_KEY=sk-ant-...

# 1C Integration
ONEC_API_URL=http://192.168.1.100:8080/api/v1
ONEC_API_TOKEN=your_1c_token

# Security
SECRET_KEY=your-very-long-random-secret-key-change-me
```

### Шаг 4: Запуск

```bash
# Сборка и запуск
docker compose up -d

# Проверка статуса
docker compose ps

# Просмотр логов
docker compose logs -f bot
```

### Шаг 5: Проверка работоспособности

```bash
# Проверка контейнеров
docker compose ps

# Ожидаемый вывод:
# NAME              STATUS          PORTS
# autoflow-bot      Up 2 minutes    
# autoflow-api      Up 2 minutes    0.0.0.0:8000->8000/tcp
# autoflow-db       Up 2 minutes    0.0.0.0:5432->5432/tcp
# autoflow-redis    Up 2 minutes    0.0.0.0:6379->6379/tcp
```

Отправьте `/start` вашему боту в Telegram — он должен ответить.

---

## Способ 2: Ручная установка

### Шаг 1: Установка зависимостей

```bash
# Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# PostgreSQL
sudo apt install postgresql-15 postgresql-contrib -y

# Redis
sudo apt install redis-server -y
```

### Шаг 2: Настройка PostgreSQL

```bash
# Вход под postgres
sudo -u postgres psql

# Создание БД и пользователя
CREATE USER autoflow WITH PASSWORD 'YourPassword123!';
CREATE DATABASE autoflow_db OWNER autoflow;
GRANT ALL PRIVILEGES ON DATABASE autoflow_db TO autoflow;
\q
```

### Шаг 3: Настройка Redis

```bash
# Редактирование конфига
sudo nano /etc/redis/redis.conf

# Изменить:
# supervised systemd
# maxmemory 256mb
# maxmemory-policy allkeys-lru

# Перезапуск
sudo systemctl restart redis
sudo systemctl enable redis
```

### Шаг 4: Установка приложения

```bash
# Клонирование
cd /opt
sudo mkdir autoflow && sudo chown $USER:$USER autoflow
cd autoflow
git clone https://github.com/hkd7148-blip/autoflow-os.git .

# Виртуальное окружение
python3.11 -m venv venv
source venv/bin/activate

# Зависимости
pip install -r requirements.txt

# Конфигурация
cp .env.example .env
nano .env
```

### Шаг 5: Systemd сервис

```bash
# Создание сервиса для бота
sudo nano /etc/systemd/system/autoflow-bot.service
```

```ini
[Unit]
Description=AUTOFLOW OS Telegram Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=autoflow
Group=autoflow
WorkingDirectory=/opt/autoflow
Environment=PATH=/opt/autoflow/venv/bin
ExecStart=/opt/autoflow/venv/bin/python -m src.bot
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Запуск
sudo systemctl daemon-reload
sudo systemctl enable autoflow-bot
sudo systemctl start autoflow-bot

# Проверка
sudo systemctl status autoflow-bot
```

---

## Настройка Nginx (для API)

```bash
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/autoflow
```

```nginx
server {
    listen 80;
    server_name api.autoflow.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/autoflow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.autoflow.example.com
```

---

## Резервное копирование

### Автоматический бэкап PostgreSQL

```bash
# Создание скрипта
sudo nano /opt/autoflow/scripts/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/autoflow/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="autoflow_backup_$DATE.sql.gz"

mkdir -p $BACKUP_DIR

# Бэкап
docker compose exec -T db pg_dump -U autoflow autoflow_db | gzip > "$BACKUP_DIR/$FILENAME"

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup created: $FILENAME"
```

```bash
chmod +x /opt/autoflow/scripts/backup.sh

# Добавление в cron (ежедневно в 3:00)
crontab -e
# Добавить строку:
0 3 * * * /opt/autoflow/scripts/backup.sh >> /var/log/autoflow-backup.log 2>&1
```

### Восстановление из бэкапа

```bash
# Остановка приложения
docker compose stop bot api

# Восстановление
gunzip < backups/autoflow_backup_20250113_030000.sql.gz | \
  docker compose exec -T db psql -U autoflow autoflow_db

# Запуск
docker compose start bot api
```

---

## Обновление

### Обновление через Git

```bash
cd /opt/autoflow

# Остановка
docker compose down

# Получение обновлений
git pull origin main

# Пересборка и запуск
docker compose up -d --build

# Проверка логов
docker compose logs -f bot
```

### Откат к предыдущей версии

```bash
# Просмотр истории
git log --oneline -10

# Откат к конкретному коммиту
git checkout abc1234

# Пересборка
docker compose up -d --build
```

---

## Мониторинг

### Просмотр логов

```bash
# Все сервисы
docker compose logs -f

# Только бот
docker compose logs -f bot

# Последние 100 строк
docker compose logs --tail=100 bot
```

### Проверка здоровья

```bash
# Статус контейнеров
docker compose ps

# Использование ресурсов
docker stats

# Проверка БД
docker compose exec db pg_isready -U autoflow

# Проверка Redis
docker compose exec redis redis-cli ping
```

### Метрики (опционально)

Для продвинутого мониторинга рекомендуется установить:
- Prometheus + Grafana
- или Datadog
- или New Relic

---

## Устранение неполадок

### Бот не отвечает

```bash
# Проверка статуса
docker compose ps bot

# Проверка логов
docker compose logs --tail=50 bot

# Перезапуск
docker compose restart bot
```

### Ошибка подключения к БД

```bash
# Проверка PostgreSQL
docker compose logs db

# Проверка подключения
docker compose exec db psql -U autoflow -d autoflow_db -c "SELECT 1;"

# Перезапуск БД
docker compose restart db
```

### Ошибка интеграции с 1С

```bash
# Проверка доступности 1С
curl -v http://192.168.1.100:8080/api/v1/ping

# Проверка токена
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://192.168.1.100:8080/api/v1/clients
```

### Нехватка памяти

```bash
# Проверка использования
free -h
docker stats --no-stream

# Очистка Docker
docker system prune -a
```

---

## Контакты поддержки

При возникновении проблем:

1. Проверьте логи: `docker compose logs -f`
2. Проверьте Issues на GitHub
3. Создайте новый Issue с описанием проблемы
4. Telegram: @username
