# FounderPilot AI

Telegram bot + Telegram Mini App + FastAPI backend + SQLite + OpenRouter AI.

Проект заточен под предпринимателей, селлеров WB/Ozon и малый бизнес: чат на главной странице Mini App, инструменты, история, бизнес-профиль, сохранённые результаты, лимиты и платежи.

## Что добавлено в этой версии

- Главная Mini App стала короче: без маркетинговой простыни, сразу быстрые действия и AI Chat.
- AI Chat находится прямо на главной странице.
- Нижняя навигация упрощена: Главная, Инструменты, История, Профиль.
- Проект подготовлен под Railway: `railway.json`, `Procfile`, `.railwayignore`, `/health`.
- Добавлена единая billing-система для подписок:
  - Telegram Stars;
  - ЮKassa / ЮMoney;
  - TON / Tonkeeper через TON Connect;
  - BTC через BTCPay Server.
- В профиле добавлен красивый блок тарифа и модальное окно выбора тарифа/способа оплаты.
- Подписка активируется только после backend-подтверждения оплаты: webhook/Telegram successful_payment/TON verify.
- Вместо простых “запросов” добавлена система кредитов: backend оценивает стоимость запроса по длине текста, истории, инструменту и модели, резервирует кредиты и списывает их только после успешного ответа AI.

## Быстрый локальный запуск Windows

```powershell
setup_windows.bat
copy .env.example .env
notepad .env
start_windows.bat
```

Локальный адрес Mini App:

```text
http://127.0.0.1:8000/app
```

Для открытия Mini App внутри Telegram нужен HTTPS. Для локального теста можно использовать ngrok:

```powershell
ngrok http 8000
```

В `.env` вставьте HTTPS URL ngrok без `/app`:

```env
WEBAPP_PUBLIC_URL=https://xxxx.ngrok-free.app
```

## Railway деплой

1. Залейте проект на GitHub.
2. Создайте Railway project из GitHub repo.
3. В Variables добавьте значения из `.env.example`.
4. После первого деплоя скопируйте публичный Railway домен.
5. Установите:

```env
WEBAPP_PUBLIC_URL=https://your-app.up.railway.app
HOST=0.0.0.0
DATABASE_PATH=/app/data/founderpilot.sqlite3
DEV_MODE=false
```

6. Сделайте redeploy.
7. У BotFather укажите Web App URL, если используете меню/кнопку Mini App.

Проверка healthcheck:

```text
https://your-app.up.railway.app/health
```

## Основные переменные окружения

```env
BOT_TOKEN=
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openrouter/free
WEBAPP_PUBLIC_URL=https://your-app.up.railway.app
APP_SECRET=
ADMIN_SECRET=
DEV_MODE=false
DATABASE_PATH=/app/data/founderpilot.sqlite3
HOST=0.0.0.0
PORT=8000
```

## Платежи и подписки

Тарифы по умолчанию:

- Free: 100 кредитов в день.
- Pro: 500 кредитов в день и 10 000 кредитов в месяц на 30 дней.
- Business: 3 000 кредитов в день и 60 000 кредитов в месяц на 30 дней.

Пользователь видит просто “Кредиты”. Токены и себестоимость считаются только внутри backend/админской аналитики.

Примерное списание:

- обычный вопрос в чате: от 2 кредитов;
- оффер/короткий текст: около 4–6 кредитов;
- карточка WB/Ozon: около 10–20 кредитов;
- анализ конкурента или большой бизнес-разбор: 20–40+ кредитов.

Если AI-запрос упал, зарезервированные кредиты возвращаются.

Кредитные лимиты меняются в `.env`:

```env
FREE_DAILY_CREDITS=100
PRO_DAILY_CREDITS=500
PRO_MONTHLY_CREDITS=10000
BUSINESS_DAILY_CREDITS=3000
BUSINESS_MONTHLY_CREDITS=60000
PER_MINUTE_LIMIT=6
```

Цены меняются в `.env`:

```env
PRO_PRICE_RUB=299
BUSINESS_PRICE_RUB=999
PRO_PRICE_STARS=299
BUSINESS_PRICE_STARS=999
PRO_PRICE_TON=3
BUSINESS_PRICE_TON=10
PRO_PRICE_BTC=0.00005
BUSINESS_PRICE_BTC=0.00015
```

### Включение способов оплаты

```env
BILLING_ENABLE_STARS=true
BILLING_ENABLE_YOOKASSA=true
BILLING_ENABLE_TON=true
BILLING_ENABLE_BTCPAY=true
```

Если способ оплаты отключён, он не показывается в Mini App.

### Telegram Stars

Включите:

```env
BILLING_ENABLE_STARS=true
```

Отдельный provider token не нужен. Бот создаёт invoice link, а подписка активируется после `successful_payment` в Telegram bot handler.

### ЮKassa / ЮMoney

Заполните:

```env
BILLING_ENABLE_YOOKASSA=true
YOOKASSA_SHOP_ID=
YOOKASSA_SECRET_KEY=
YOOKASSA_RETURN_URL=https://your-app.up.railway.app/app?payment_return=1
```

Webhook URL для кабинета ЮKassa:

```text
https://your-app.up.railway.app/api/billing/webhooks/yookassa
```

Подписка активируется после события `payment.succeeded` или статуса `succeeded`.

### TON / Tonkeeper

Заполните:

```env
BILLING_ENABLE_TON=true
TON_RECEIVER_ADDRESS=
TON_API_KEY=
TON_NETWORK=mainnet
```

Mini App подключает TON Connect UI и отправляет транзакцию на `TON_RECEIVER_ADDRESS` с `order_id` в payload/comment. Backend не активирует тариф без проверки транзакции. Если `TON_API_KEY` не задан, backend вернёт понятную ошибку и оставит заказ `pending`.

### BTC через BTCPay Server

Заполните:

```env
BILLING_ENABLE_BTCPAY=true
BTCPAY_URL=https://your-btcpay.example.com
BTCPAY_STORE_ID=
BTCPAY_API_KEY=
BTCPAY_WEBHOOK_SECRET=
```

Webhook URL для BTCPay:

```text
https://your-app.up.railway.app/api/billing/webhooks/btcpay
```

Подписка активируется только после подтверждённого/settled/paid invoice события.

## Billing API

```text
GET  /api/billing/plans
GET  /api/billing/status
POST /api/billing/create-order
GET  /api/billing/order/{order_id}
POST /api/billing/ton/verify
POST /api/billing/webhooks/yookassa
POST /api/billing/webhooks/btcpay
```

## Админ-статистика

```text
GET /api/admin/stats
Header: X-Admin-Secret: ваш ADMIN_SECRET
```

Возвращает пользователей, запросы, списанные кредиты, активные подписки, pending orders, payments by provider и ошибки.

## Проверка проекта

```powershell
python -m compileall app run.py tests
pytest
```

Если зависимости не установлены, сначала:

```powershell
pip install -r requirements.txt
```

## Важные ограничения

- Реальные платежи требуют настроенные кабинеты YooKassa/BTCPay, TON API и публичный HTTPS Railway/ngrok URL.
- TON verification сделан безопасно: если backend не может подтвердить транзакцию, подписка не активируется автоматически.
- BTC подписка активируется только по webhook от BTCPay.
- Секреты нельзя хранить в GitHub. Используйте Railway Variables и `.env` локально.

## FounderPilot system upgrade: projects, memory, credits, anti-abuse

This build keeps the existing Gemini frontend files and adds the product/backend layer for a more complete SaaS system.

### New backend capabilities

- Multi-project workspace API: `/api/projects`, `/api/projects/current`, `/api/projects/{project_id}`
- Project memory API: `/api/memory`, project-specific AI context injection into chat/tools/generation
- User templates API: `/api/templates`
- Credit pack catalog and admin grant flow: `/api/credits/packs`, `/api/credits/packs/order`, `/api/credits/packs/{order_id}/grant`
- Analytics API: `/api/analytics/summary`
- Text export: `/api/export/history.txt`
- Notification preferences API: `/api/notifications/preferences`
- Admin overview and users API: `/api/admin/overview`, `/api/admin/users`
- Basic anti-abuse event logging and IP burst protection for AI endpoints
- Frontend compatibility fixes: `/api/profile/save`, flexible `/api/saved`, flexible `/api/feedback`, `/api/me` now returns credits inside `user` as well as `usage`

### Important notes

The new backend APIs are ready for the interface to use, but the current visual layout was intentionally not redesigned in this patch. The existing Mini App UI remains the Gemini version you provided.

Credit-pack payment is currently prepared as backend order/grant flow. Real external checkout for credit packs can be connected next to the same billing providers used for subscriptions.

### Local launch

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
```

Edit `.env` and set at minimum:

```env
BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_key
WEBAPP_PUBLIC_URL=https://your-railway-domain.up.railway.app
APP_SECRET=generate-a-long-random-secret
ADMIN_SECRET=generate-a-long-random-admin-secret
DEV_MODE=false
```

Run locally:

```powershell
python run.py
```

Local Mini App URL:

```text
http://127.0.0.1:8000/app
```

### Railway deploy

1. Push the project to GitHub.
2. Connect the repo to Railway.
3. Add variables from `.env.example` in Railway Variables.
4. Deploy.
5. In BotFather, set the Mini App URL to:

```text
https://your-railway-domain.up.railway.app/app
```

### Verification commands

```powershell
python -m compileall app run.py tests
pytest -q
node --check static/app.js
```

## Обновление backend: Telegram profile, безопасные реквизиты и автоподписка

В этой версии backend дополнительно поддерживает:

- корректное имя Telegram из Mini App `initData`, без hardcoded имени в API;
- `photo_url` из Telegram WebApp user и возврат `photo_url/avatar_url` в `/api/me`;
- безопасное сохранение банковских реквизитов для выплат: полный 20-значный счёт хранится только зашифрованно, во frontend возвращается только маска;
- настройки автоподписки через ЮKassa: FounderPilot хранит только токен `payment_method_id`, а не данные карты;
- проверку YooKassa webhook через запрос к YooKassa API перед активацией тарифа;
- endpoint для безопасного админского запуска автопродлений.

Дополнительная переменная:

```env
YOOKASSA_ENABLE_SAVED_PAYMENT_METHOD=true
```

Новые API:

```text
GET    /api/billing/payout-method
POST   /api/billing/payout-method
DELETE /api/billing/payout-method

GET    /api/billing/autopay
POST   /api/billing/autopay
POST   /api/billing/autopay/run-due  # только с X-Admin-Secret
```

Важно: FounderPilot не хранит номера банковских карт, CVV и полные данные платёжных карт. Для автосписаний используется токен ЮKassa.
