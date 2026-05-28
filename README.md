# FounderPilot AI

FounderPilot AI - Telegram-бот, FastAPI backend, SQLite и Telegram Mini App для предпринимателей, селлеров WB/Ozon, маркетологов и владельцев малого бизнеса.

Mini App работает как AI-кабинет внутри Telegram: AI Chat, готовые бизнес-инструменты, история, сохраненные результаты, бизнес-профиль, обратная связь, рефералка и лимиты Free/Pro/Business.

## Что добавлено

- мобильный Telegram-like Mini App на vanilla HTML/CSS/JS;
- нижняя навигация: Главная, AI Chat, Инструменты, История, Профиль;
- AI Chat с историей диалогов, copy/save, feedback и улучшением ответов;
- 11 инструментов: WB/Ozon карточка, маржа, идея товара, описание, реклама, отзыв, конкурент, SWOT, контент-план, план продаж, проверка идеи;
- серверный расчет маржи: прибыль, маржа, ROI, ориентир безубыточной цены;
- onboarding первого запуска и бизнес-профиль;
- сохраненные результаты и feedback;
- простая реферальная система с bonus_requests;
- Free-лимит 20 запросов в день и заготовка под подписки/платежи;
- админ-статистика `GET /api/admin/stats`;
- безопасное расширение SQLite через `CREATE TABLE IF NOT EXISTS` и миграции колонок.

## Структура

```text
app/
  bot.py                # Telegram bot: /start, /app, /help, admin commands
  config.py             # настройки .env
  db.py                 # SQLite schema, миграции, история, лимиты
  main.py               # FastAPI endpoints и запуск сервера
  openrouter_client.py  # OpenRouter Chat Completions
  prompts.py            # system prompts и список инструментов
  rate_limit.py         # дневной лимит и антиспам
  telegram_auth.py      # Telegram WebApp initData validation
static/
  index.html
  styles.css
  app.js
tests/
```

## .env

Создайте `.env` из `.env.example`:

```env
BOT_TOKEN=123456:YOUR_TELEGRAM_BOT_TOKEN
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
OPENROUTER_MODEL=openrouter/free
WEBAPP_PUBLIC_URL=https://your-ngrok-url.ngrok-free.app
ADMIN_SECRET=change-this-admin-secret
DEV_MODE=false
DATABASE_PATH=founderpilot.sqlite3
FREE_TRIAL_REQUESTS=20
SUBSCRIBER_MONTHLY_LIMIT=300
PER_MINUTE_LIMIT=6
ADMIN_TELEGRAM_IDS=
HOST=127.0.0.1
PORT=8000
```

Для локальной проверки в браузере без Telegram initData:

```env
DEV_MODE=true
WEBAPP_PUBLIC_URL=http://127.0.0.1:8000
```

В production оставьте `DEV_MODE=false`: Mini App API будет требовать валидный Telegram `initData`.

## Локальный запуск

```powershell
cd D:\founderpilot_ai_bot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Mini App локально:

```text
http://127.0.0.1:8000/app
```

## Ngrok и Telegram Mini App

Telegram Web App кнопка работает только с публичным HTTPS URL.

```powershell
python run.py
ngrok http 8000
```

Скопируйте HTTPS адрес ngrok и вставьте без `/app`:

```env
WEBAPP_PUBLIC_URL=https://abc123.ngrok-free.app
```

Перезапустите проект и отправьте боту `/start` или `/app`. Кнопка откроет:

```text
https://abc123.ngrok-free.app/app
```

## AI Chat

`POST /api/chat` принимает сообщение и optional `conversation_id`. Backend создает или продолжает диалог, добавляет бизнес-профиль в system/context prompt и отправляет в OpenRouter последние 10-20 сообщений.

В Mini App доступны:

- новый чат;
- продолжение старого чата;
- copy/save у ответов AI;
- кнопки: Сделай короче, Сделай подробнее, Добавь примеры, Сделай продающе;
- feedback thumbs up/down;
- история диалогов.

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

Для `margin_calc` backend сам считает экономику и передает расчет AI для пояснений, рисков и рекомендаций.

## Бизнес-профиль и onboarding

Первый запуск показывает onboarding:

1. Кто вы?
2. Что хотите улучшить?
3. Короткое описание бизнеса.

Данные сохраняются в `business_profiles` и используются в AI Chat и инструментах. Профиль можно редактировать или очистить в разделе `Профиль`.

## Сохраненное и feedback

Ответы AI и результаты инструментов можно сохранить через `POST /api/saved`. Список доступен в профиле и в истории. Feedback сохраняется через `POST /api/feedback`; для негативной оценки Mini App открывает поле "Что улучшить?".

## Рефералка

У каждого пользователя есть `referral_code`. Если новый пользователь приходит через `/start <referral_code>`, backend сохраняет связь и добавляет бонусные запросы пригласившему. Статистика доступна в профиле через `GET /api/referral`.

## Админ-статистика

Endpoint:

```http
GET /api/admin/stats
X-Admin-Secret: <ADMIN_SECRET>
```

Возвращает пользователей, запросы за день, chat/tool активность, популярные инструменты, сохраненные результаты, негативный feedback, ошибки и активных пользователей. При неверном секрете возвращается `403`.

## Команды бота

- `/start` - описание продукта и кнопка Mini App;
- `/app` - открыть Mini App;
- `/help` - что умеет бот и как открыть Mini App;
- `/stats` - лимиты и статус доступа;
- любой текст - быстрый AI-ответ в Telegram-чате.

## Проверка

```powershell
python -m compileall .
pytest
```

Дополнительно проверьте:

- `/app` открывает Mini App;
- нижняя навигация переключает разделы;
- AI Chat виден и показывает error state без alert, если нет токена;
- инструменты открываются и валидируют формы;
- бизнес-профиль сохраняется;
- saved и feedback пишутся в SQLite;
- `/api/admin/stats` требует `X-Admin-Secret`.

## Частые ошибки

- Mini App кнопка не появляется: `WEBAPP_PUBLIC_URL` должен быть публичным HTTPS и проект нужно перезапустить.
- API возвращает ошибку initData: для браузера включите `DEV_MODE=true`, для Telegram проверьте `BOT_TOKEN`.
- AI не отвечает: проверьте `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` и доступ модели.
- Лимит исчерпан: Free дает 20 запросов в день плюс бонусные запросы за рефералов.
