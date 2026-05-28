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

- Free: 20 запросов в день.
- Pro: 300 запросов в день на 30 дней.
- Business: 1500 запросов в день на 30 дней.

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

Возвращает пользователей, запросы, активные подписки, pending orders, payments by provider и ошибки.

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
