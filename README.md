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
pytest                                 ✅ 22 passed
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
