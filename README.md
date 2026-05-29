# FounderPilot AI Bot + Mini App

Готовый backend на FastAPI + aiogram и Telegram Mini App в стиле утверждённых макетов FounderPilot: чистый светлый SaaS, desktop sidebar, mobile bottom nav, профиль в Apple Settings стиле, подписка, кредиты, команда, история, уведомления и платежи.

## Что исправлено в этой сборке

- Починена покупка подписки: добавлены стабильные alias-роуты `/api/billing/create-order`, `/api/billing/checkout`, `/api/billing/orders`, `/api/subscription/checkout`.
- Исправлено автоопределение способа оплаты: frontend и backend теперь умеют выбирать доступный provider автоматически.
- YooKassa больше не показывается как рабочий способ оплаты без `YOOKASSA_SHOP_ID` и `YOOKASSA_SECRET_KEY`.
- Исправлена тарифная сетка, которую согласовали для экономики сервиса: `Free — 0 ₽`, `Go — 399 ₽`, `Plus — 990 ₽`, `Pro — 2 490 ₽`, `Business — 7 990 ₽`.
- Исправлен баг, когда frontend вне Telegram отправлял `telegram_user_id: "dev"` и ломал запросы валидацией.
- Обновлён визуал desktop/mobile: аккуратнее карточки, планы, provider-кнопки, пакеты кредитов, фокус-состояния, hover/active анимации.
- Улучшены защитные заголовки, лимит тела запроса, CORS по публичному домену, проверка владельца заказа, безопасное хранение платёжных токенов.
- Из архива убраны секреты, `.env`, локальная `.venv`, sqlite-база и кэш-файлы.

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

### Telegram Stars

```env
BILLING_ENABLE_STARS=true
```

Работает через Telegram Bot API invoices. Открывать Mini App лучше из Telegram, чтобы `openInvoice` сработал красиво.

### YooKassa

Заполните реальные ключи:

```env
BILLING_ENABLE_YOOKASSA=true
YOOKASSA_SHOP_ID=ваш_shop_id
YOOKASSA_SECRET_KEY=ваш_secret_key
YOOKASSA_RETURN_URL=https://ваш-домен/app
YOOKASSA_ENABLE_SAVED_PAYMENT_METHOD=true
```

В кабинете YooKassa укажите HTTP notification URL:

```text
https://ваш-домен/api/billing/webhooks/yookassa
```

Важно: если ключи YooKassa пустые, кнопка карты/СБП не будет показываться как активная. Это специально, чтобы пользователь не тыкал в кнопку-пустышку и не ловил `Not found`, как будто сервис решил сыграть в прятки.

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
```

В этой сборке проверено:

```text
python -m compileall app run.py tests  ✅
node --check static/app.js             ✅
pytest                                 ✅ 18 passed
```

## Важные ограничения

- Реальные платежи требуют рабочие кабинеты YooKassa/BTCPay, Telegram Bot API и публичный HTTPS URL.
- Backend не хранит номера карт/CVV. Для автопродления сохраняется только токен платёжного метода от YooKassa в зашифрованном виде.
- Не коммитьте `.env`, `.venv`, `*.sqlite3`, `__pycache__`.
