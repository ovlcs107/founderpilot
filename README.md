# FounderPilot AI Bot + Mini App

Готовый backend на FastAPI + aiogram и Telegram Mini App в стиле утверждённых макетов FounderPilot: чистый светлый SaaS, desktop sidebar, mobile bottom nav, профиль в Apple Settings стиле, подписка, кредиты, команда, история, уведомления, платежи и серверная экономика тарифов.

## Что исправлено и усилено в этой сборке

- Тарифная сетка закреплена на сервере: `Free — 0 ₽`, `Go — 399 ₽`, `Plus — 990 ₽`, `Pro — 2 490 ₽`, `Business — 7 990 ₽`.
- Добавлен `Profit Guard`: backend считает себестоимость AI-запросов по токенам, курсу, комиссии OpenRouter, комиссии оплаты, налогу и резерву возвратов. Если модель становится дороже, запрос автоматически стоит больше кредитов.
- Добавлены admin-endpoint'ы для проверки экономики: `/api/economics/plans` и `/api/economics/credit-packs`.
- Telegram Stars теперь выключен по умолчанию. Его нельзя случайно продавать как рубли: нужно задать `TELEGRAM_STARS_RUB_VALUE` или явно разрешить риск через `BILLING_ALLOW_UNPRICED_STARS=true`.
- YooKassa больше не показывается как рабочий способ оплаты без `YOOKASSA_SHOP_ID` и `YOOKASSA_SECRET_KEY`.
- Автопродление через YooKassa выключено по умолчанию, потому что recurring-платежи требуют отдельного разрешения магазина; разовая покупка подписки работает без recurring.
- Починена покупка подписки: стабильные alias-роуты `/api/billing/create-order`, `/api/billing/checkout`, `/api/billing/orders`, `/api/subscription/checkout`.
- Исправлено автоопределение provider'а: frontend и backend выбирают только реально доступные способы оплаты.
- Исправлен баг, когда frontend вне Telegram отправлял кривой `telegram_user_id`.
- Пакеты кредитов теперь тоже проходят проверку прибыльности перед созданием оплаты.
- Визуал подписки улучшен по макету: тарифы показывают лимиты/фичи, current-plan блок обновляется при выборе плана, добавлена заметка о серверной защите лимитов.
- Убрана визуальная ошибка с повторяющимся subtitle в мобильном профиле.
- Усилены защитные заголовки, CORS, лимит тела запроса, проверка владельца заказа, безопасное хранение платёжных токенов.
- Из архива убраны секреты, `.env`, локальная `.venv`, sqlite-база и кэш-файлы.
- Добавлен полноценный Support Center: пользователь создаёт тикет в Mini App, бот отправляет его в Telegram-группу поддержки, саппорты отвечают строго reply на сообщение бота, ответ сохраняется в backend и появляется у пользователя в отдельном чате поддержки.
- Главная очищена от быстрых действий: теперь это центрированный AI-чат, который после первого сообщения раскрывается на весь экран.
- Все декоративные кнопки без backend-действия теперь дают понятный feedback, а не молчат как кнопка лифта в заброшенном ТЦ.


## AI Quality Core

В этой сборке усилена главная часть продукта — AI-ответы и стабильность запросов:

- добавлен детерминированный intent-router: обычное общение, бизнес, расчёты, код, тексты;
- чат больше не превращает короткие фразы вроде “привет” в бизнес-допрос;
- AI получает серверный контекст тарифа, лимитов, проекта, бизнес-профиля и активной организации;
- тариф влияет на глубину ответа и выбранную модель, но пользователь не видит внутреннюю кухню;
- добавлен plan-specific model routing через env: `OPENROUTER_MODEL_FREE/GO/PLUS/PRO/BUSINESS`;
- добавлены retry/backoff на 429/5xx/timeout от OpenRouter;
- сырые JSON-ошибки провайдера больше не уходят во frontend;
- история диалога компактно обрезается по количеству сообщений и символов, чтобы старые сообщения не ломали новый ответ;
- добавлен endpoint `/api/ai/status` для быстрой проверки активной модели, тарифа и лимитов пользователя.

Пример настройки моделей:

```env
OPENROUTER_MODEL=openrouter/free
OPENROUTER_MODEL_FREE=openrouter/free
OPENROUTER_MODEL_GO=deepseek/deepseek-chat-v3.1
OPENROUTER_MODEL_PLUS=deepseek/deepseek-chat-v3.1
OPENROUTER_MODEL_PRO=anthropic/claude-3.5-sonnet
OPENROUTER_MODEL_BUSINESS=anthropic/claude-3.5-sonnet
AI_REQUEST_TIMEOUT_SECONDS=90
AI_MAX_RETRIES=2
AI_CHAT_HISTORY_MESSAGES=24
AI_CHAT_HISTORY_CHARS=12000
```

Если ставите дорогую модель на Pro/Business, обязательно обновите `AI_INPUT_COST_USD_PER_M_TOKENS` и `AI_OUTPUT_COST_USD_PER_M_TOKENS`, иначе Profit Guard будет считать себестоимость слишком мягко.

## Как работает математика, чтобы не уходить в минус

Сервис считает экономику на backend, а не доверяет frontend.

Формула для платного тарифа:

```text
gross_revenue = цена тарифа
net_revenue = gross_revenue - комиссия оплаты - налог - резерв возвратов
max_ai_budget = net_revenue * MAX_AI_COST_SHARE_BY_PLAN[plan]
credit_value = max_ai_budget / monthly_credits
request_ai_cost = токены_входа * INPUT_PRICE + токены_выхода * OUTPUT_PRICE
request_ai_cost *= USD_RUB_RATE
request_ai_cost *= (1 + OPENROUTER_FEE_RATE)
request_ai_cost *= AI_COST_SAFETY_MULTIPLIER
safe_credits_for_request = ceil(request_ai_cost / credit_value)
final_credits = max(base_credits, safe_credits_for_request)
```

То есть пользователь не может сжечь больше AI-бюджета, чем тарифу разрешено. Когда лимит кредитов заканчивается — backend режет запросы, даже если frontend нарисует красивые кнопки. Финансовый гоблин заперт на сервере, всё честно.

Проверить расчёт можно так:

```bash
curl -H "X-Admin-Secret: ваш_ADMIN_SECRET" https://ваш-домен/api/economics/plans
curl -H "X-Admin-Secret: ваш_ADMIN_SECRET" https://ваш-домен/api/economics/credit-packs
```

Главные env-переменные:

```env
PROFIT_GUARD_ENABLED=true
YOOKASSA_FEE_RATE=0.035
TELEGRAM_STARS_FEE_RATE=0.30
TAX_RATE=0.06
REFUND_RISK_RATE=0.03
MAX_AI_COST_SHARE_BY_PLAN=free:0,go:0.35,plus:0.38,pro:0.42,business:0.35,default:0.40
AI_INPUT_COST_USD_PER_M_TOKENS=1.0
AI_OUTPUT_COST_USD_PER_M_TOKENS=4.0
OPENROUTER_FEE_RATE=0.055
USD_RUB_RATE=100
AI_COST_SAFETY_MULTIPLIER=2.0
ESTIMATE_FREE_MODEL_COST=false
MINIMUM_CREDIT_VALUE_RUB=0.01
```

Если меняете модель на дорогую — обновите `AI_INPUT_COST_USD_PER_M_TOKENS` и `AI_OUTPUT_COST_USD_PER_M_TOKENS`. Лучше завысить, чем потом кормить API своими деньгами.

## Быстрый запуск на Windows

```powershell
cd founderpilot_fixed_project
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
notepad .env
python run.py
```

После запуска откройте:

```text
http://127.0.0.1:8000/app
```

Для локального браузера без Telegram можно временно поставить в `.env`:

```env
DEV_MODE=true
DEV_SKIP_TELEGRAM_AUTH=true
WEBAPP_PUBLIC_URL=http://127.0.0.1:8000
DATABASE_PATH=founderpilot.sqlite3
```

Для публичного деплоя верните:

```env
DEV_MODE=false
DEV_SKIP_TELEGRAM_AUTH=false
WEBAPP_PUBLIC_URL=https://ваш-домен
```

## Настройка платежей

### YooKassa

Заполните реальные ключи:

```env
BILLING_ENABLE_YOOKASSA=true
YOOKASSA_SHOP_ID=ваш_shop_id
YOOKASSA_SECRET_KEY=ваш_secret_key
YOOKASSA_RETURN_URL=https://ваш-домен/app
YOOKASSA_ENABLE_SAVED_PAYMENT_METHOD=false
```

В кабинете YooKassa укажите HTTP notification URL:

```text
https://ваш-домен/api/billing/webhooks/yookassa
```

Если ключи YooKassa пустые, кнопка карты/СБП не будет показываться как активная.

### Telegram Stars

Stars включайте только после финансовой настройки:

```env
BILLING_ENABLE_STARS=true
TELEGRAM_STARS_RUB_VALUE=0.80
```

`TELEGRAM_STARS_RUB_VALUE` — ваша консервативная оценка, сколько рублей реально остаётся FounderPilot за 1 Star после всех комиссий/вывода. Если не знаете — оставьте Stars выключенным и принимайте оплату через YooKassa.

## Настройка поддержки через Telegram-группу

1. Создайте приватную группу для саппортов.
2. Добавьте туда вашего бота FounderPilot.
3. Дайте боту право читать сообщения и отправлять ответы.
4. Узнайте chat id группы и добавьте в `.env`:

```env
SUPPORT_GROUP_CHAT_ID=-1001234567890
SUPPORT_GROUP_THREAD_ID=
SUPPORT_PUBLIC_NAME=FounderPilot Support
```

Сценарий работы:

```text
Mini App → Профиль → Поддержка → пользователь создаёт тикет
backend сохраняет тикет и просит бота отправить сообщение в группу
саппорт отвечает именно reply на сообщение бота
бот сохраняет ответ в backend
пользователь видит ответ в Mini App → Профиль → Поддержка
```

Важно: для приёма reply из группы нужен отдельный Railway worker с `RUN_BOT_POLLING=true`. Web-сервис оставьте с `RUN_BOT_POLLING=false`, чтобы healthcheck не зависел от Telegram polling.

## Railway deploy

1. Загрузите проект на GitHub без `.env`.
2. Создайте Railway service из репозитория.
3. В Variables перенесите значения из `.env.example` и замените секреты на реальные.
4. Убедитесь, что `WEBAPP_PUBLIC_URL` равен публичному Railway-домену без `/app` в конце.
5. В BotFather укажите Mini App URL: `https://ваш-домен/app`.

Файлы деплоя уже есть:

```text
Procfile
railway.json
nixpacks.toml
.railwayignore
```

## Основные API

```text
GET  /health
GET  /app
GET  /api/me
GET  /api/tools
POST /api/chat
GET  /api/history
GET  /api/billing/plans
POST /api/billing/create-order
GET  /api/billing/order/{order_id}
POST /api/billing/autopay
POST /api/billing/webhooks/yookassa
POST /api/billing/webhooks/btcpay
GET  /api/credits/packs
POST /api/credits/packs/order
GET  /api/economics/plans              admin only
GET  /api/economics/credit-packs       admin only
GET  /api/notifications/preferences
POST /api/notifications/preferences
GET  /api/support/tickets
POST /api/support/tickets
GET  /api/support/tickets/{ticket_id}
POST /api/support/tickets/{ticket_id}/messages
POST /api/support/tickets/{ticket_id}/status
GET  /api/organizations
POST /api/organizations
```

## Проверка проекта

```powershell
python -m compileall app run.py tests
pip install -r requirements-dev.txt
pytest
node --check static/app.js
```

В этой сборке проверено:

```text
python -m compileall app run.py tests  ✅
node --check static/app.js             ✅
pytest                                 ✅ 25 passed
```

## Важные ограничения

- Реальные платежи требуют рабочие кабинеты YooKassa/BTCPay, Telegram Bot API и публичный HTTPS URL.
- Backend не хранит номера карт/CVV. Для автопродления сохраняется только токен платёжного метода от YooKassa в зашифрованном виде.
- Не коммитьте `.env`, `.venv`, `*.sqlite3`, `__pycache__`.


## Railway / production

Основной web-сервис: `RUN_BOT_POLLING=false`. Для команд бота запускайте отдельный worker с `RUN_BOT_POLLING=true`.

### Fix Railway healthcheck

В этой сборке `/health` специально сделан лёгким: он не зависит от Telegram polling, OpenRouter, YooKassa и долгой проверки внешних сервисов. На Railway код автоматически слушает `0.0.0.0`, даже если в старых Variables случайно остался `HOST=127.0.0.1` или `HOST=localhost`. Именно такие старые значения часто дают вечное `Network > Performing healthchecks...` при полностью успешной сборке.

Для Railway web-сервиса держите так:

```env
RUN_BOT_POLLING=false
BOT_POLLING_STRICT=false
STRICT_RUNTIME_VALIDATION=false
```

`PORT` в Railway Variables лучше не задавать вручную: Railway передаёт его сам. Локально порт по умолчанию — `8000`.

Дополнительная проверка:

```text
GET /health  -> лёгкий healthcheck для Railway
GET /ready   -> строгая готовность базы
```

## Final polish 1.3.0

В этой сборке добавлены и отполированы:

- чистый чат на главной без лишних быстрых действий;
- исправлен фокус input/textarea без раздражающей синей рамки;
- профиль показывает реальный Telegram ID и дату регистрации из таблицы `users.created_at`;
- кнопка выхода из аккаунта убрана;
- страница поддержки разделена на вкладки: новое обращение, история, чат;
- ответы саппорта из Telegram-группы через reply сохраняются в backend и появляются в Mini App;
- добавлена серверная лента уведомлений `/api/notifications`;
- уведомления создаются для поддержки и успешной активации подписки;
- история подтягивает реальные диалоги, tool runs и сохранённые документы;
- страницу подписки разделили на вкладки `Подписки` и `Кредиты`;
- страница `О FounderPilot` показывает версию и дату обновления из env (`APP_VERSION`, `APP_UPDATED_AT`), форма обратной связи убрана;
- визуальные SVG-иконки уменьшены и унифицированы;
- добавлены мягкие анимации появления, карточек, вкладок и сообщений.

Для production оставь веб-сервис с `RUN_BOT_POLLING=false`, а Telegram worker для поддержки запускай отдельно с `RUN_BOT_POLLING=true`.

## Диалоги и расширенное администрирование

В этой сборке AI-диалоги сохраняются надёжнее: frontend заранее создаёт conversation_id и хранит его локально, а backend записывает сообщение пользователя до обращения к AI-провайдеру. Если пользователь закрыл Mini App во время генерации ответа, открытый диалог всё равно появится в истории и восстановится при следующем входе.

Расширенные админ-команды Telegram-бота:

```text
/admin
/users [limit]
/user <telegram_id>
/setplan <id> <free|go|plus|pro|business> [days] [note]
/addcredits <id> <amount> [note]
/takecredits <id> <amount> [note]
/credits <id> [limit]
/grant <id> <days> [monthly_limit] [note]
/unlimited <id> [note]
/revoke <id> [note]
/free_limit <id> <count> [note]
/block <id> [note]
/unblock <id> [note]
/orders [limit] [status]
/payments [limit]
/errors [limit]
/admin_stats
/user_history <id> [limit]
/clear_history <id> [note]
```

Для работы команд укажи свой Telegram ID в переменной `ADMIN_TELEGRAM_IDS` и запусти отдельный worker с `RUN_BOT_POLLING=true`.

---

## PostgreSQL production mode

Проект теперь умеет работать в двух режимах:

```text
Локально / тесты: SQLite через DATABASE_PATH
Продакшен / Railway: PostgreSQL через DATABASE_URL
```

Для Railway больше не нужен общий Volume между web-сервисом и bot-worker. Оба сервиса должны смотреть в одну PostgreSQL-базу.

### Railway: правильная схема сервисов

```text
founderpilot-web        HTTP backend + Mini App
founderpilot-bot-worker Telegram polling + support/admin commands
PostgreSQL             общая база для web и worker
```

### Переменные для web-сервиса

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
RUN_BOT_POLLING=false
BOT_POLLING_STRICT=false
WEBAPP_PUBLIC_URL=https://your-app.up.railway.app
APP_SECRET=your_unique_random_secret_24_chars_min
ADMIN_SECRET=your_unique_admin_secret_24_chars_min
```

Healthcheck для web-сервиса:

```text
/health
```

Start command:

```bash
python run.py
```

### Переменные для bot-worker

Создайте второй Railway-сервис из того же репозитория. Он должен иметь тот же `DATABASE_URL`, но другой режим запуска:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
RUN_BOT_POLLING=true
BOT_POLLING_STRICT=true
BOT_TOKEN=your_bot_token
ADMIN_TELEGRAM_IDS=your_telegram_id
SUPPORT_GROUP_CHAT_ID=-100xxxxxxxxxx
```

Для worker healthcheck не нужен.

### Что удалить после перехода с SQLite

Если перешли на PostgreSQL, не используйте в продакшене:

```env
DATABASE_PATH=/app/data/founderpilot.sqlite3
DATABASE_PATH=${{MySQL.MYSQL_URL}}
DATABASE_PATH=${{Postgres.DATABASE_URL}}
```

Правильно:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

`DATABASE_PATH` оставлен только для локального SQLite и старых тестов.

### Миграция старой SQLite-базы в PostgreSQL

Если у вас уже были пользователи/подписки/история в `founderpilot.sqlite3`, скачайте файл и выполните:

```bash
python scripts/migrate_sqlite_to_postgres.py --sqlite founderpilot.sqlite3 --postgres "$DATABASE_URL"
```

Скрипт сначала создаёт PostgreSQL-схему, потом копирует совпадающие таблицы и колонки.

После миграции запустите web и worker с одним и тем же `DATABASE_URL`.

### Проверка после деплоя

В логах должно быть примерно так:

```text
Database initialized at postgresql://...
FounderPilot AI web service is running
Telegram bot polling is disabled
```

У worker должно быть:

```text
Telegram bot polling started
```

Если Mini App работает, а бот молчит — почти всегда worker не запущен или у него `RUN_BOT_POLLING=false`.


## Combined Mini App + Telegram bot mode

FounderPilot now supports a single Railway service that runs both parts at once:

```env
BOT_SERVICE_MODE=combined
RUN_BOT_POLLING=false
BOT_TOKEN=...
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

In this mode Uvicorn serves `/app`, `/api/*`, `/health`, and the Telegram bot polling runs in a background supervisor inside the same process. If Telegram polling temporarily fails, the Mini App keeps working and the bot retries automatically.

Use `BOT_SERVICE_MODE=web` only if you intentionally want a web-only service. Use `BOT_SERVICE_MODE=bot` only for a separate bot worker.

## AI quality and failover

Plan-specific models still work through:

```env
OPENROUTER_MODEL_FREE=
OPENROUTER_MODEL_GO=
OPENROUTER_MODEL_PLUS=
OPENROUTER_MODEL_PRO=
OPENROUTER_MODEL_BUSINESS=
```

You can add fallback models for temporary 429/5xx/timeouts:

```env
OPENROUTER_FALLBACK_MODELS=deepseek/deepseek-chat-v3.1,openai/gpt-4.1-mini
AI_MAX_RETRIES=2
AI_REQUEST_TIMEOUT_SECONDS=90
AI_ANSWER_QUALITY_MODE=balanced
```

Fallbacks are invisible to users and are used only by backend. Keep real model costs in `.env` aligned with Profit Guard before enabling expensive models.

### Telegram Mini App auth stability

The frontend now keeps Telegram `initData` in session storage and can recover it from Telegram launch parameters. `/api/me` still validates the signed Telegram data on the backend before creating/updating a user.

Recommended production values:

```env
DEV_MODE=false
DEV_SKIP_TELEGRAM_AUTH=false
TELEGRAM_INIT_DATA_MAX_AGE_SECONDS=604800
```

If Telegram profile data does not appear in the Mini App, check that `BOT_TOKEN` is the same bot that opens the Web App and that `WEBAPP_PUBLIC_URL` is the root domain without a duplicated `/app`.
