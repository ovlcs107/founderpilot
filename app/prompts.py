from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BusinessMode:
    key: str
    title: str
    description: str
    instruction: str
    icon: str = "tools"
    placeholder: str = ""
    fields: tuple[dict[str, str], ...] = ()


SYSTEM_PROMPT = """
Ты FounderPilot AI — практичный AI-помощник для предпринимателей, малого бизнеса, селлеров WB/Ozon, маркетологов и основателей проектов.
Твоя задача — помогать с офферами, продажами, карточками товаров, расчётом маржи, анализом конкурентов, контентом, стратегией, идеями роста и планом действий.
Отвечай на русском.
Пиши понятно, структурно, без воды.
Форматируй ответы в аккуратном Markdown: короткие заголовки, списки, нумерованные шаги, таблицы только когда они реально помогают.
Код, формулы, JSON и конфиги всегда оформляй fenced code block.
Не используй HTML. Не используй emoji.
Если данных не хватает — задай 2-4 уточняющих вопроса.
Если можно дать пример — дай пример.
Фокусируйся на действиях, цифрах, рисках и конкретных шагах.
Не используй устаревшую дату: текущая дата и время передаются отдельным runtime-контекстом backend.
Если вопрос зависит от актуальных событий, цен, законов, API или платежных правил, честно предупреждай, что без онлайн-поиска данные могут быть неполными.
Для финансовых расчетов показывай формулы и предупреждай, что это приблизительная модель.
""".strip()


CHAT_SYSTEM_PROMPT = """
Ты FounderPilot AI — практичный AI-помощник для предпринимателей, малого бизнеса, селлеров WB/Ozon, маркетологов и основателей проектов.
Твоя задача — помогать с офферами, продажами, карточками товаров, расчётом маржи, анализом конкурентов, контентом, стратегией, идеями роста и планом действий.
Отвечай на русском.
Пиши понятно, структурно, без воды.
Форматируй ответы в аккуратном Markdown: короткие заголовки, списки, нумерованные шаги, таблицы только когда они реально помогают.
Код, формулы, JSON и конфиги всегда оформляй fenced code block.
Не используй HTML. Не используй emoji.
Если данных не хватает — задай 2-4 уточняющих вопроса.
Если можно дать пример — дай пример.
Фокусируйся на действиях, цифрах, рисках и конкретных шагах.
Не используй устаревшую дату: текущая дата и время передаются отдельным runtime-контекстом backend.
Если вопрос зависит от актуальных событий, цен, законов, API или платежных правил, честно предупреждай, что без онлайн-поиска данные могут быть неполными.
""".strip()


def field(
    key: str,
    label: str,
    placeholder: str,
    kind: str = "text",
    required: bool = True,
    inputmode: str = "text",
) -> dict[str, str]:
    return {
        "key": key,
        "label": label,
        "placeholder": placeholder,
        "type": kind,
        "required": "true" if required else "false",
        "inputmode": inputmode,
    }


MODES: dict[str, BusinessMode] = {
    "wb_ozon_card": BusinessMode(
        key="wb_ozon_card",
        title="WB/Ozon карточка товара",
        description="SEO-название, описание, буллеты, ключи, фото и инфографика.",
        instruction=(
            "Пользователь заполняет поля: товар, цена, целевая аудитория, преимущества, недостатки, конкуренты. "
            "Верни строго по разделам: SEO-название; описание карточки; 5 буллетов преимуществ; ключевые слова; "
            "идеи фото; идеи инфографики; ошибки карточки; рекомендации для роста продаж."
        ),
        icon="product",
        placeholder="Опишите товар, нишу, текущую карточку и главную задачу.",
        fields=(
            field("product", "Товар", "Например: органайзер для кухни"),
            field("price", "Цена", "Например: 1290 руб.", inputmode="decimal"),
            field("target_audience", "Целевая аудитория", "Кто покупает и зачем", "textarea"),
            field("advantages", "Преимущества", "Что у товара сильного", "textarea"),
            field("disadvantages", "Недостатки", "Что может мешать продаже", "textarea", required=False),
            field("competitors", "Конкуренты", "Названия, ссылки или описание", "textarea", required=False),
        ),
    ),
    "margin_calc": BusinessMode(
        key="margin_calc",
        title="Расчет маржи",
        description="Прибыль, маржа, ROI, точка безубыточности и рекомендации по цене.",
        instruction=(
            "Backend уже посчитал прибыль с единицы, маржу, ROI и ориентир безубыточной цены, если данных хватило. "
            "На основе расчета дай пояснение, риски, рекомендации по цене и что улучшить в экономике."
        ),
        icon="calculator",
        placeholder="Укажите все расходы на единицу товара.",
        fields=(
            field("purchase_price", "Закупочная цена", "Например: 430", "number", inputmode="decimal"),
            field("sale_price", "Цена продажи", "Например: 990", "number", inputmode="decimal"),
            field("commission", "Комиссия", "Например: 18% или 180", "text", inputmode="decimal"),
            field("logistics", "Логистика", "Например: 95", "number", inputmode="decimal"),
            field("packaging", "Упаковка", "Например: 25", "number", required=False, inputmode="decimal"),
            field("ads", "Реклама", "Например: 120", "number", required=False, inputmode="decimal"),
            field("taxes_other", "Налоги/прочее", "Например: 6% или 50", "text", required=False, inputmode="decimal"),
        ),
    ),
    "product_idea": BusinessMode(
        key="product_idea",
        title="Идея товара",
        description="5 идей товаров с рисками, конкуренцией и оффером.",
        instruction=(
            "Верни 5 идей товаров. Для каждой идеи укажи: почему может продаваться; риски; конкуренция; "
            "как выделиться; примерный оффер."
        ),
        icon="target",
        placeholder="Ниша, бюджет, опыт, ограничения, желаемый чек.",
        fields=(
            field("niche", "Ниша", "Например: товары для дома"),
            field("budget", "Бюджет", "Например: 150000", inputmode="decimal"),
            field("target_audience", "Аудитория", "Кому хотите продавать", "textarea", required=False),
            field("restrictions", "Ограничения", "Что нельзя или сложно делать", "textarea", required=False),
        ),
    ),
    "product_description": BusinessMode(
        key="product_description",
        title="Описание товара",
        description="Продающее описание, преимущества, SEO-ключи и заголовки.",
        instruction=(
            "Верни: продающее описание; короткое описание; преимущества; SEO-ключи; варианты заголовков."
        ),
        icon="content",
        placeholder="Товар, характеристики, аудитория, преимущества.",
        fields=(
            field("product", "Товар", "Название или категория"),
            field("features", "Характеристики", "Материал, размер, комплект", "textarea"),
            field("audience", "Аудитория", "Кому подходит товар", "textarea", required=False),
            field("benefits", "Преимущества", "Что важно подчеркнуть", "textarea", required=False),
        ),
    ),
    "ad_offer": BusinessMode(
        key="ad_offer",
        title="Реклама и оффер",
        description="Оффер, заголовки, объявления, боли ЦА и триггеры покупки.",
        instruction=(
            "Верни: главный оффер; 5 рекламных заголовков; 5 коротких объявлений; варианты для Telegram, ВК и маркетплейсов; "
            "боли целевой аудитории; триггеры покупки."
        ),
        icon="chart",
        placeholder="Продукт, аудитория, цена, площадка и тон.",
        fields=(
            field("product", "Продукт", "Что продаете"),
            field("audience", "Целевая аудитория", "Кому продаете", "textarea"),
            field("price", "Цена", "Например: 1990 руб.", required=False, inputmode="decimal"),
            field("channel", "Канал", "Telegram, ВК, WB, Ozon", required=False),
            field("benefit", "Главная выгода", "Почему должны купить", "textarea", required=False),
        ),
    ),
    "review_reply": BusinessMode(
        key="review_reply",
        title="Ответ на отзыв",
        description="Вежливый ответ, короткая версия и выводы по товару.",
        instruction=(
            "Пользователь вставляет отзыв. Верни: вежливый ответ; короткий ответ; более теплый ответ; "
            "что улучшить в товаре или карточке."
        ),
        icon="chat",
        placeholder="Вставьте отзыв покупателя и контекст по товару.",
        fields=(
            field("review", "Отзыв", "Вставьте текст отзыва", "textarea"),
            field("product", "Товар", "Название товара", required=False),
            field("tone", "Тон ответа", "Например: спокойно, заботливо, официально", required=False),
        ),
    ),
    "competitor_analysis": BusinessMode(
        key="competitor_analysis",
        title="Анализ конкурента",
        description="Сильные и слабые стороны, отстройка, идеи карточки и оффера.",
        instruction=(
            "Пользователь описывает конкурента или вставляет текст карточки. Верни: сильные стороны конкурента; слабые стороны; "
            "как отстроиться; идеи для оффера; идеи для карточки; риски."
        ),
        icon="search",
        placeholder="Описание конкурента, текст карточки, цена, рейтинг, отзывы.",
        fields=(
            field("competitor", "Конкурент", "Описание, ссылка или текст карточки", "textarea"),
            field("competitor_price", "Цена конкурента", "Например: 1190", required=False, inputmode="decimal"),
            field("your_product", "Ваш товар", "Чем вы отличаетесь", "textarea", required=False),
            field("your_price", "Ваша цена", "Если известна", required=False, inputmode="decimal"),
        ),
    ),
    "swot": BusinessMode(
        key="swot",
        title="SWOT-анализ",
        description="Сильные стороны, слабости, возможности, угрозы и первые шаги.",
        instruction=(
            "Верни: сильные стороны; слабые стороны; возможности; угрозы; вывод; первые шаги."
        ),
        icon="check",
        placeholder="Опишите бизнес, товар, рынок, конкурентов и ограничения.",
        fields=(
            field("business", "Бизнес или товар", "Коротко опишите проект", "textarea"),
            field("market", "Рынок", "Ниша, конкуренты, спрос", "textarea", required=False),
            field("goal", "Цель", "Что хотите улучшить", required=False),
        ),
    ),
    "content_plan": BusinessMode(
        key="content_plan",
        title="Контент-план",
        description="7 постов, Reels/Shorts, CTA и темы для прогрева.",
        instruction=(
            "Верни: 7 постов; идеи Reels/Shorts; короткие тексты постов; CTA; темы для прогрева."
        ),
        icon="list",
        placeholder="Ниша, продукт, аудитория, площадки, цель контента.",
        fields=(
            field("niche", "Ниша", "Например: товары для дома"),
            field("product", "Продукт", "Что продвигаем", "textarea"),
            field("platform", "Площадка", "Telegram, ВК, Reels, Shorts", required=False),
            field("audience", "Аудитория", "Кому пишем", "textarea", required=False),
        ),
    ),
    "sales_plan": BusinessMode(
        key="sales_plan",
        title="План продаж",
        description="План на 14 дней, метрики, тесты и быстрые гипотезы роста.",
        instruction=(
            "Верни: план на 14 дней; действия по дням; какие метрики смотреть; что тестировать; быстрые гипотезы роста."
        ),
        icon="trending",
        placeholder="Что продаете, кому, цена, текущие каналы, цель и бюджет.",
        fields=(
            field("product", "Продукт", "Что продаете"),
            field("goal", "Цель", "Например: 30 продаж за 14 дней"),
            field("channels", "Каналы продаж", "Что уже используете", "textarea", required=False),
            field("budget", "Бюджет", "Например: 20000", required=False, inputmode="decimal"),
        ),
    ),
    "business_idea": BusinessMode(
        key="business_idea",
        title="Проверка бизнес-идеи",
        description="Плюсы, минусы, монетизация, первые шаги и проверка за 7 дней.",
        instruction=(
            "Верни: плюсы; минусы; кому продавать; как монетизировать; первые 5 шагов; риски; как проверить идею за 7 дней."
        ),
        icon="settings",
        placeholder="Опишите идею, аудиторию, продукт, цену, ресурсы и главный риск.",
        fields=(
            field("idea", "Идея", "Опишите бизнес-идею", "textarea"),
            field("audience", "Кому продавать", "Целевая аудитория", "textarea", required=False),
            field("monetization", "Монетизация", "Как планируете зарабатывать", required=False),
            field("resources", "Ресурсы", "Бюджет, команда, сроки", "textarea", required=False),
        ),
    ),
    "strategy": BusinessMode(
        key="strategy",
        title="Стратегия запуска",
        description="Приоритеты, каналы, MVP и план запуска на 7-30 дней.",
        instruction="Собери реалистичную стратегию запуска. Дай ICP, оффер, каналы, MVP, план на 7 дней и план на 30 дней.",
        icon="target",
        placeholder="Опишите продукт, рынок, аудиторию, цель и ограничения.",
    ),
    "offer": BusinessMode(
        key="offer",
        title="Оффер",
        description="Коммерческое предложение для рекламы, продаж и лендинга.",
        instruction="Создай сильный оффер. Дай 10 вариантов заголовка, 5 вариантов подзаголовка, боли клиента, выгоды, доказательства и CTA.",
        icon="chart",
    ),
    "sales_script": BusinessMode(
        key="sales_script",
        title="Скрипт продаж",
        description="Структура диалога для переписки, звонка или Telegram-продаж.",
        instruction="Сделай скрипт продаж: первый контакт, выявление боли, презентация, работа с возражениями, закрытие и follow-up.",
        icon="chat",
    ),
    "content": BusinessMode(
        key="content",
        title="Контент-план",
        description="Контент как воронка: доверие, экспертность, кейсы и продажи.",
        instruction="Сделай контент-план на 14 дней. Раздели посты на доверие, экспертность, продажи, кейсы и вовлечение.",
        icon="list",
    ),
    "unit": BusinessMode(
        key="unit",
        title="Unit-экономика",
        description="Цена, CAC, маржа, окупаемость и точки безубыточности.",
        instruction="Разбери unit-экономику. Покажи формулы, какие цифры нужны, примерный расчет, точки безубыточности и риски.",
        icon="calculator",
    ),
    "pitch": BusinessMode(
        key="pitch",
        title="Pitch инвестору",
        description="Структура презентации для инвестора, партнера или совета директоров.",
        instruction="Собери pitch: проблема, решение, рынок, продукт, бизнес-модель, traction, команда, конкуренты, запрос, риски.",
        icon="chart",
    ),
    "positioning": BusinessMode(
        key="positioning",
        title="Позиционирование",
        description="Сегменты, конкурирующие альтернативы, отличие и рыночный фокус.",
        instruction="Найди позиционирование. Дай сегменты клиентов, конкурирующие альтернативы, уникальность, тон бренда и 5 слоганов.",
        icon="target",
    ),
    "next_step": BusinessMode(
        key="next_step",
        title="Следующий шаг",
        description="Короткое решение: что сделать сегодня и как измерить результат.",
        instruction="Дай максимально конкретный следующий шаг. Ответ должен быть коротким: диагноз, 3 действия сегодня, 3 метрики, один риск.",
        icon="check",
    ),
}

DEFAULT_MODE = "strategy"
MINI_APP_TOOL_IDS = (
    "wb_ozon_card",
    "margin_calc",
    "product_idea",
    "product_description",
    "ad_offer",
    "review_reply",
    "competitor_analysis",
    "swot",
    "content_plan",
    "sales_plan",
    "business_idea",
)


def get_mode(mode_key: str | None) -> BusinessMode:
    if not mode_key:
        return MODES[DEFAULT_MODE]
    return MODES.get(mode_key, MODES[DEFAULT_MODE])


def get_mini_app_tools() -> list[BusinessMode]:
    return [MODES[tool_id] for tool_id in MINI_APP_TOOL_IDS]


def _format_optional_fields(optional_fields: dict[str, Any] | None) -> str:
    if not optional_fields:
        return "Дополнительные поля не заполнены."

    lines: list[str] = []
    for key, value in optional_fields.items():
        if value is None:
            continue
        clean_value = str(value).strip()
        if clean_value:
            lines.append(f"- {key}: {clean_value}")
    return "\n".join(lines) if lines else "Дополнительные поля не заполнены."


def build_user_prompt(mode_key: str | None, user_text: str, optional_fields: dict[str, Any] | None = None) -> str:
    mode = get_mode(mode_key)
    return f"""
Режим: {mode.title}
Инструкция режима: {mode.instruction}

Дополнительные поля:
{_format_optional_fields(optional_fields)}

Описание от пользователя:
{user_text.strip()}

Сформируй ответ в Markdown для деловой аудитории.
Структура: краткий вывод, ключевые рекомендации, риски, план ближайших действий.
Не используй emoji.
Не растягивай, но не теряй важные детали.
""".strip()
