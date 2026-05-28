# FounderPilot AI

FounderPilot AI — Telegram-бот, FastAPI backend, SQLite и Telegram Mini App для предпринимателей, селлеров WB/Ozon, маркетологов и малого бизнеса.

Главный экран теперь сделан как рабочий чат: минимум рекламного текста, быстрые действия сверху и AI Chat прямо на главной.

## Что внутри

- Telegram-бот на aiogram;
- FastAPI backend;
- SQLite база с пользователями, диалогами, инструментами, историей, сохранёнными результатами и feedback;
- Telegram Mini App на vanilla HTML/CSS/JS;
- AI Chat на главной странице;
- бизнес-инструменты: маржа, WB/Ozon карточка, оффер, конкурент, SWOT, контент-план, план продаж и другое;
- бизнес-профиль пользователя;
- онбординг первого запуска;
- рефералка и лимиты;
- admin stats endpoint;
- Railway config: `railway.json`, `Procfile`, `/health`, `.railwayignore`.

## Структура

```text
app/
  bot.py                # Telegram bot: /start, /app, /help, admin commands
  config.py             # настройки .env / Railway env variables
  db.py                 # SQLite schema, миграции, история, лимиты
  main.py               # FastAPI endpoints и запуск сервера + bot polling
  openrouter_client.py  # OpenRouter Chat Completions
  prompts.py            # system prompts и список инструментов
  rate_limit.py         # дневной лимит и антиспам
  telegram_auth.py      # Telegram WebApp initData validation
static/
  index.html            # Mini App
  styles.css            # Telegram-style UI
  app.js                # frontend логика
tests/
railway.json
Procfile
.env.example
```

## Локальный запуск Windows

```powershell
cd D:\founderpilot_ai_bot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env
python run.py
```

Для локальной проверки в браузере поставьте в `.env`:

```env
DEV_MODE=true
WEBAPP_PUBLIC_URL=http://127.0.0.1:8000
HOST=0.0.0.0
PORT=8000
```

Откройте:

```text
http://127.0.0.1:8000/app
```

## .env

Минимум:

```env
BOT_TOKEN=123456:YOUR_TELEGRAM_BOT_TOKEN
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
OPENROUTER_MODEL=openrouter/free
WEBAPP_PUBLIC_URL=https://your-app.up.railway.app
ADMIN_SECRET=change-this-admin-secret
APP_SECRET=change-this-app-secret
DATABASE_PATH=founderpilot.sqlite3
DEV_MODE=false
DEV_SKIP_TELEGRAM_AUTH=false
HOST=0.0.0.0
PORT=8000
FREE_TRIAL_REQUESTS=20
SUBSCRIBER_MONTHLY_LIMIT=300
PER_MINUTE_LIMIT=6
ADMIN_TELEGRAM_IDS=
```

Секреты храните только в `.env` или Railway Variables. В архиве `.env` не поставляется.

## Telegram Mini App через ngrok

Telegram Web App кнопка работает только с публичным HTTPS URL.

```powershell
python run.py
ngrok http 8000
```

Скопируйте HTTPS адрес без `/app`:

```env
WEBAPP_PUBLIC_URL=https://abc123.ngrok-free.app
```

Перезапустите проект и отправьте боту `/start` или `/app`.

## Railway deployment

Проект подготовлен под Railway:

- `railway.json` использует Nixpacks;
- start command: `python run.py`;
- healthcheck: `/health`;
- приложение слушает `0.0.0.0` и порт из `PORT`;
- `.railwayignore` исключает `.env`, `.venv`, SQLite и мусорные файлы.

Шаги:

1. Загрузите проект в GitHub.
2. В Railway создайте New Project → Deploy from GitHub repo.
3. В Variables добавьте:

```env
BOT_TOKEN=...
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=openrouter/free
WEBAPP_PUBLIC_URL=https://your-app.up.railway.app
ADMIN_SECRET=...
APP_SECRET=...
DEV_MODE=false
HOST=0.0.0.0
```

4. После первого деплоя скопируйте публичный домен Railway и поставьте его в `WEBAPP_PUBLIC_URL` без `/app`.
5. Redeploy.
6. Откройте бота в Telegram и отправьте `/start`.

Для постоянной SQLite базы на Railway лучше подключить Volume и поставить:

```env
DATABASE_PATH=/data/founderpilot.sqlite3
```

Без volume SQLite может потерять данные после redeploy/rebuild.

## AI Chat

Главная страница сразу открывает чат. Пользователь может написать задачу обычным текстом:

```text
Посчитай маржу: закупка 430, продажа 990, комиссия 18%, логистика 95, реклама 120.
```

Backend создаёт или продолжает диалог, добавляет бизнес-профиль в контекст и отправляет в OpenRouter последние сообщения.

Endpoint:

```http
POST /api/chat
```

## Инструменты

Основной endpoint:

```http
POST /api/tools/run
```

Пример:

```json
{
  "telegram_user_id": 123456789,
  "tool_id": "margin_calc",
  "input": {
    "purchase_price": "430",
    "sale_price": "990",
    "commission": "18%",
    "logistics": "95",
    "packaging": "25",
    "ads": "120",
    "taxes_other": "6%"
  }
}
```

Для `margin_calc` backend сам считает прибыль, маржу, ROI и ориентир безубыточной цены, а AI даёт пояснения и рекомендации.

## Проверка

```powershell
python -m compileall app run.py tests
pytest
```

Проверьте вручную:

- `/health` возвращает `{"status":"ok"}`;
- `/app` открывает Mini App;
- чат на главной странице виден сразу;
- быстрые действия открывают инструменты;
- история и сохранённые результаты отображаются;
- `/api/admin/stats` требует `X-Admin-Secret`.

## Частые ошибки

- Mini App кнопка не появляется: `WEBAPP_PUBLIC_URL` должен быть публичным HTTPS.
- API возвращает ошибку initData: локально включите `DEV_MODE=true`, в Telegram проверьте `BOT_TOKEN`.
- AI не отвечает: проверьте `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` и доступ модели.
- Railway healthcheck падает: проверьте, что `HOST=0.0.0.0`, а `PORT` не забит неверным значением.
- SQLite не сохраняет данные между деплоями: подключите Railway Volume и используйте `DATABASE_PATH=/data/founderpilot.sqlite3`.
