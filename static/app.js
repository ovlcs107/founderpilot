const tg = window.Telegram?.WebApp || null;

const iconPaths = {
  home: '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
  chat: '<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7A8.4 8.4 0 0 1 4 11.5a8.5 8.5 0 0 1 17 0Z"/>',
  tools: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/>',
  history: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
  user: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
  send: '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
  close: '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
  back: '<line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>',
  'credit-card': '<rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/>',
  tg_stars: '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
  ton: '<path d="M12 2L3 9l9 13 9-13L12 2zm0 4.5L17.5 10H6.5L12 6.5zM6.8 12h10.4l-5.2 7.5-5.2-7.5z"/>',
  btc: '<path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="M10 8h2.5a1.5 1.5 0 0 1 0 3H10V8z"/><path d="M10 13h3a1.5 1.5 0 0 1 0 3h-3v-3z"/><path d="M12 5v2"/><path d="M12 17v2"/>'
};

const state = {
  user: null,
  tools: [],
  plans: {},
  history: [],
  currentMode: "strategy",
  historyFilter: "all",
  activePlanKey: null,
  activePlan: null,
  isSending: false,
  messages: [],
  pollingTimers: new Set(),
  onboardingStep: 0,
  onboardingData: {},
  onboardingConfig: [
    {
      id: "role",
      title: "Кто вы?",
      type: "choices",
      options: [
        { key: "wb_seller", label: "Селлер Wildberries" },
        { key: "ozon_seller", label: "Селлер Ozon" },
        { key: "multi_seller", label: "Мультиселлер" },
        { key: "beginner", label: "Выбираю нишу" },
        { key: "other", label: "Другое" }
      ]
    },
    {
      id: "pain",
      title: "Что хотите улучшить?",
      type: "choices",
      options: [
        { key: "sales", label: "Продажи" },
        { key: "cards", label: "Карточки товара" },
        { key: "ads", label: "Рекламу" },
        { key: "ideas", label: "Идеи товара" },
        { key: "strategy", label: "Стратегию" },
        { key: "unit", label: "Расчёты" }
      ]
    },
    {
      id: "business_description",
      title: "Коротко опишите бизнес",
      type: "textarea",
      placeholder: "Например: продаю товары для кухни на Ozon, хочу улучшить карточки и рекламу"
    }
  ]
};

function $(id) {
  return document.getElementById(id);
}

function escapeHTML(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function normalizeErrorPayload(payload) {
  if (!payload) return "Системная ошибка";
  return payload.error || payload.detail || payload.message || "Системная ошибка";
}

function injectIcons(root = document) {
  root.querySelectorAll("[data-icon]").forEach((el) => {
    const name = el.dataset.icon;
    if (iconPaths[name] && !el.querySelector("svg")) {
      el.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${iconPaths[name]}</svg>`;
    }
  });
}

function initTelegram() {
  if (!tg) return;
  tg.ready?.();
  tg.expand?.();
  if (tg.setHeaderColor) tg.setHeaderColor("secondary_bg_color");
  document.body.classList.add("tg-theme");
}

function getTelegramUser() {
  return tg?.initDataUnsafe?.user || null;
}

function showToast(text) {
  const el = $("toast");
  if (!el) return;
  el.textContent = text;
  el.classList.add("visible");
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => el.classList.remove("visible"), 2500);
}

async function request(url, options = {}) {
  const initData = tg?.initData || "";
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) headers["Content-Type"] = "application/json";
  if (initData) headers["X-Telegram-Init-Data"] = initData;

  const res = await fetch(url, { ...options, headers });
  const text = await res.text();
  let data = null;
  if (text) {
    try { data = JSON.parse(text); } catch { data = { detail: text }; }
  }
  if (!res.ok || data?.ok === false) {
    throw new Error(normalizeErrorPayload(data));
  }
  return data ?? {};
}

async function requestMaybe(url, options = {}, fallback = null) {
  try {
    return await request(url, options);
  } catch (err) {
    return fallback;
  }
}

function normalizeUser(data) {
  const tgUser = getTelegramUser();
  const root = data?.user || data || {};
  const dailyLimit = root.daily_limit ?? root.limit_today ?? root.dailyLimit ?? 20;
  const dailyUsed = root.daily_used ?? root.used_today ?? root.usedToday ?? 0;
  const remaining = root.remaining ?? (Number.isFinite(Number(dailyLimit)) ? Math.max(0, Number(dailyLimit) - Number(dailyUsed)) : null);

  return {
    ...root,
    telegram_id: root.telegram_id || root.telegram_user_id || tgUser?.id || "dev",
    first_name: root.first_name || root.name || tgUser?.first_name || "пользователь",
    username: root.username || tgUser?.username || "",
    plan: root.plan || root.plan_name || "free",
    daily_limit: dailyLimit,
    used_today: dailyUsed,
    remaining,
    business_profile: root.business_profile || root.description || root.business_description || "",
    onboarding_required: Boolean(data?.onboarding_required ?? root.onboarding_required)
  };
}

function getTelegramUserId() {
  return String(state.user?.telegram_id || state.user?.telegram_user_id || getTelegramUser()?.id || "dev");
}

function normalizeTools(data) {
  const raw = Array.isArray(data) ? data : (Array.isArray(data?.tools) ? data.tools : []);
  return raw.map((tool, index) => ({
    id: tool.id || tool.tool_id || `tool_${index}`,
    title: tool.title || tool.name || "Инструмент",
    description: tool.description || tool.subtitle || "",
    prompt_template: tool.prompt_template || tool.prompt || tool.template || ""
  }));
}

function normalizePlans(data) {
  const fallback = {
    free: { title: "Free", description: "Базовый доступ", price_monthly: 0, providers: [] },
    pro: { title: "Pro", description: "Для регулярной работы", price_monthly: 299, providers: [] },
    business: { title: "Business", description: "Для активной работы", price_monthly: 999, providers: [] }
  };

  const providerPool = Array.isArray(data?.providers) ? data.providers : [];
  const normalizeProvider = (provider) => {
    const id = provider.id || provider.provider || provider.key || "yookassa";
    return {
      id,
      title: provider.title || provider.name || provider.label || providerTitle(id),
      description: provider.description || provider.subtitle || "",
      price_formatted: provider.price_formatted || provider.price_text || provider.price || ""
    };
  };

  if (Array.isArray(data?.plans)) {
    return data.plans.reduce((acc, plan) => {
      const key = plan.key || plan.id || plan.plan;
      if (!key) return acc;
      const planProviders = Array.isArray(plan.providers) ? plan.providers : providerPool;
      acc[key] = {
        title: plan.title || plan.name || key.toUpperCase(),
        description: plan.description || "",
        price_monthly: plan.price_monthly ?? plan.price_rub ?? plan.price ?? 0,
        price_text: plan.price_text || plan.price_formatted || null,
        providers: planProviders.map(normalizeProvider)
      };
      return acc;
    }, {});
  }

  if (data?.plans && typeof data.plans === "object") {
    return Object.fromEntries(Object.entries(data.plans).map(([key, plan]) => {
      const planProviders = Array.isArray(plan.providers) ? plan.providers : providerPool;
      return [key, {
        title: plan.title || plan.name || key.toUpperCase(),
        description: plan.description || "",
        price_monthly: plan.price_monthly ?? plan.price_rub ?? plan.price ?? 0,
        price_text: plan.price_text || plan.price_formatted || null,
        providers: planProviders.map(normalizeProvider)
      }];
    }));
  }

  return fallback;
}

function providerTitle(id) {
  const titles = {
    telegram_stars: "Telegram Stars",
    stars: "Telegram Stars",
    yookassa: "ЮKassa / ЮMoney",
    yoo_money: "ЮKassa / ЮMoney",
    ton: "TON / Tonkeeper",
    crypto: "TON / Tonkeeper",
    btc: "Bitcoin",
    btcpay_btc: "Bitcoin"
  };
  return titles[id] || id;
}

function normalizeHistory(data) {
  const raw = Array.isArray(data) ? data : (Array.isArray(data?.history) ? data.history : []);
  return raw.map((item, index) => {
    const type = item.type || item.mode || "chat";
    const title = item.title || item.mode || item.tool_id || "Запрос";
    const text = item.text || item.prompt || item.user_input || item.input || "";
    const answer = item.answer || item.result || item.result_text || item.content || item.response || "";
    const ts = item.timestamp || item.created_at || item.date || null;
    return { ...item, id: item.id || index, type, mode: item.mode || type, title, text, answer, timestamp: ts };
  });
}

function formatDate(value) {
  if (!value) return "";
  const numeric = Number(value);
  const date = Number.isFinite(numeric)
    ? new Date(numeric > 100000000000 ? numeric : numeric * 1000)
    : new Date(value);
  return Number.isNaN(date.getTime()) ? String(value) : date.toLocaleDateString("ru-RU");
}

function switchView(target) {
  document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach((btn) => btn.classList.toggle("active", btn.dataset.target === target));

  const targetView = $(`view-${target}`);
  if (targetView) targetView.classList.add("active");

  const titles = { home: "Главная", chat: "AI Чат", tools: "Инструменты", history: "История", profile: "Профиль" };
  const title = $("pageTitle");
  if (title) title.textContent = titles[target] || "FounderPilot AI";

  if (target === "tools") loadTools().catch(() => {});
  if (target === "history") loadHistory().catch(() => {});
}

function autoResizeTextarea(textarea) {
  if (!textarea) return;
  textarea.style.height = "auto";
  textarea.style.height = `${textarea.scrollHeight}px`;
}

function updateChatSendButton(textareaId, buttonId) {
  const txt = $(textareaId);
  const btn = $(buttonId);
  if (txt && btn) btn.disabled = state.isSending || !txt.value.trim();
}

function clearChatEmpty(scroll) {
  scroll?.querySelector(".chat-empty")?.remove();
}

function appendChatMessage(scrollId, role, text, id = null) {
  const scroll = $(scrollId);
  if (!scroll) return null;
  clearChatEmpty(scroll);
  const el = document.createElement("div");
  el.className = role === "user" ? "msg user" : role === "assistant" || role === "bot" ? "msg bot" : "msg bot system-msg";
  if (id) el.id = id;
  el.textContent = text;
  scroll.appendChild(el);
  scroll.scrollTop = scroll.scrollHeight;
  return el;
}

function renderChat(scrollId, messages) {
  const scroll = $(scrollId);
  if (!scroll) return;
  scroll.textContent = "";
  if (!messages || !messages.length) {
    scroll.innerHTML = `<div class="chat-empty"><span data-icon="chat"></span><p>История диалога пуста. Введите запрос ниже.</p></div>`;
    injectIcons(scroll);
    return;
  }
  messages.forEach((message) => appendChatMessage(scrollId, message.role, message.text));
}

async function askAI(text) {
  const chatPayload = {
    telegram_user_id: getTelegramUserId(),
    message: text,
    mode: state.currentMode
  };

  try {
    return await request("/api/chat", { method: "POST", body: JSON.stringify(chatPayload) });
  } catch (chatError) {
    return await request("/api/ask", {
      method: "POST",
      body: JSON.stringify({ mode: state.currentMode, text, message: text, telegram_user_id: getTelegramUserId() })
    });
  }
}

function extractAnswer(res) {
  return res?.answer || res?.response || res?.result || res?.text || res?.message || "";
}

async function handleChatSend(inputId, scrollId, sendBtnId) {
  const input = $(inputId);
  const text = input?.value.trim();
  if (!input || !text || state.isSending) return;

  state.isSending = true;
  input.value = "";
  autoResizeTextarea(input);
  updateChatSendButton(inputId, sendBtnId);

  state.messages.push({ role: "user", text });
  appendChatMessage(scrollId, "user", text);
  const statusId = `status_${Date.now()}`;
  appendChatMessage(scrollId, "system", "Выполняется анализ...", statusId);

  try {
    const res = await askAI(text);
    $(statusId)?.remove();
    const answer = extractAnswer(res);
    if (!answer) throw new Error("Пустой ответ от AI");
    state.messages.push({ role: "assistant", text: answer });
    appendChatMessage(scrollId, "assistant", answer);

    if (state.user) {
      const used = res.used_today ?? res.daily_used ?? res.usage?.daily_used;
      const remaining = res.remaining ?? res.usage?.remaining;
      if (used !== undefined) state.user.used_today = used;
      if (remaining !== undefined) state.user.remaining = remaining;
      updateProfileUI();
    }
    loadHistory().catch(() => {});
  } catch (err) {
    const st = $(statusId);
    if (st) {
      st.classList.remove("system-msg");
      st.classList.add("text-danger");
      st.textContent = err.message;
    }
  } finally {
    state.isSending = false;
    updateChatSendButton(inputId, sendBtnId);
  }
}

function updateProfileUI() {
  if (!state.user) return;
  const firstName = state.user.first_name || "пользователь";
  const initial = firstName.charAt(0).toUpperCase();

  if ($("homeGreeting")) $("homeGreeting").textContent = `Здравствуйте, ${firstName}`;
  if ($("profileUserTitle")) {
    $("profileUserTitle").textContent = state.user.username ? `@${state.user.username}` : `ID: ${state.user.telegram_id}`;
  }
  if ($("headerUserAvatar")) $("headerUserAvatar").textContent = initial;
  if ($("profileUserAvatar")) $("profileUserAvatar").textContent = initial;
  if ($("userAvatar")) $("userAvatar").textContent = initial;

  const label = $("profilePlanLabel");
  if (label) {
    const p = state.user.plan ? String(state.user.plan).toUpperCase() : "FREE";
    const rem = state.user.remaining === null || state.user.remaining === undefined ? "Безлимитно" : `Осталось: ${state.user.remaining}`;
    label.innerHTML = `${escapeHTML(p)} <small style="display:block; font-weight:normal; margin-top:1px; opacity:0.7;">${escapeHTML(rem)}</small>`;
  }
  if ($("profileBusinessDescription")) $("profileBusinessDescription").value = state.user.business_profile || "";
}

async function loadMe() {
  const data = await request("/api/me");
  state.user = normalizeUser(data);
  updateProfileUI();
  if (data?.onboarding_required || state.user.onboarding_required) openOnboarding();
}

function openOnboarding() {
  state.onboardingStep = 0;
  state.onboardingData = {};
  const modal = $("onboardingModal");
  if (!modal) return;
  modal.hidden = false;
  renderOnboardingStep();
}

function renderOnboardingStep() {
  const cfg = state.onboardingConfig[state.onboardingStep];
  if (!cfg) return;
  const title = $("onboardingTitle");
  if (title) title.textContent = cfg.title;

  const dots = $("onboardingModal")?.querySelectorAll(".progress-row span") || [];
  dots.forEach((dot, idx) => dot.classList.toggle("active", idx <= state.onboardingStep));

  const body = $("onboardingBody");
  if (!body) return;
  body.textContent = "";

  if (cfg.type === "textarea") {
    const textarea = document.createElement("textarea");
    textarea.className = "profile-textarea";
    textarea.rows = 4;
    textarea.placeholder = cfg.placeholder || "";
    textarea.value = state.onboardingData[cfg.id] || "";
    textarea.addEventListener("input", () => {
      state.onboardingData[cfg.id] = textarea.value.trim();
      const err = $("onboardingError");
      if (err) err.hidden = true;
    });
    body.appendChild(textarea);
  } else {
    const savedKey = state.onboardingData[cfg.id];
    cfg.options.forEach((o) => {
      const btn = document.createElement("button");
      btn.className = `onboarding-option ${savedKey === o.key ? "active" : ""}`;
      btn.dataset.key = o.key;
      btn.type = "button";
      btn.textContent = o.label;
      body.appendChild(btn);
    });
  }

  const err = $("onboardingError");
  if (err) err.hidden = true;
  if ($("onboardingBackBtn")) $("onboardingBackBtn").disabled = state.onboardingStep === 0;
  if ($("onboardingNextBtn")) {
    $("onboardingNextBtn").disabled = false;
    $("onboardingNextBtn").textContent = state.onboardingStep === state.onboardingConfig.length - 1 ? "Готово" : "Далее";
  }
}

async function nextOnboarding() {
  const cfg = state.onboardingConfig[state.onboardingStep];
  if (!cfg) return;
  const value = state.onboardingData[cfg.id];
  if (!value || (typeof value === "string" && !value.trim())) {
    const err = $("onboardingError");
    if (err) {
      err.textContent = cfg.type === "textarea" ? "Заполните поле." : "Выберите один из вариантов.";
      err.hidden = false;
    }
    return;
  }

  if (state.onboardingStep < state.onboardingConfig.length - 1) {
    state.onboardingStep++;
    renderOnboardingStep();
    return;
  }

  const nextBtn = $("onboardingNextBtn");
  if (nextBtn) nextBtn.disabled = true;
  try {
    const res = await request("/api/onboarding", { method: "POST", body: JSON.stringify(state.onboardingData) });
    if (res.user) state.user = normalizeUser(res);
    else await loadMe().catch(() => {});
    updateProfileUI();
    if ($("onboardingModal")) $("onboardingModal").hidden = true;
    showToast("Готово!");
  } catch (e) {
    if ($("onboardingModal")) $("onboardingModal").hidden = true;
    showToast("Профиль можно заполнить позже.");
  } finally {
    if (nextBtn) nextBtn.disabled = false;
  }
}

function previousOnboarding() {
  if (state.onboardingStep > 0) {
    state.onboardingStep--;
    renderOnboardingStep();
  }
}

async function loadTools() {
  const data = await requestMaybe("/api/tools", { method: "GET" }, { tools: [] });
  state.tools = normalizeTools(data);
  renderTools();
}

function renderTools() {
  const grid = $("toolsGrid");
  if (!grid) return;
  if (!state.tools.length) {
    grid.innerHTML = `<p class="muted" style="text-align:center; padding:30px 0;">Инструменты временно недоступны.</p>`;
    return;
  }

  grid.innerHTML = state.tools.map((t) => `
    <div class="tool-item-row" data-prompt="${escapeHTML(t.prompt_template)}">
      <div class="tool-icon-box"><span data-icon="tools"></span></div>
      <div class="tool-text-box">
        <h4>${escapeHTML(t.title)}</h4>
        <p class="muted">${escapeHTML(t.description)}</p>
      </div>
    </div>
  `).join("");
  injectIcons(grid);
}

async function loadBillingPlans() {
  const data = await requestMaybe("/api/billing/plans", { method: "GET" }, { plans: {} });
  state.plans = normalizePlans(data);
}

function openBillingModal() {
  const modal = $("billingModal");
  if (!modal) return;
  modal.hidden = false;
  renderBillingPlans();
}

function closeBillingModal() {
  const modal = $("billingModal");
  if (modal) modal.hidden = true;
}

function renderBillingPlans() {
  if ($("paymentProviderBox")) $("paymentProviderBox").hidden = true;
  const planList = $("billingPlanList");
  if (!planList) return;
  planList.hidden = false;
  if ($("billingTitle")) $("billingTitle").textContent = "Тарифные планы";

  const keys = Object.keys(state.plans || {});
  if (!keys.length) {
    planList.innerHTML = `<p class="muted" style="text-align:center; padding:16px;">Нет доступных тарифов.</p>`;
    return;
  }

  planList.innerHTML = keys.map((k) => {
    const p = state.plans[k];
    const isCurrent = state.user && String(state.user.plan).toLowerCase() === k.toLowerCase();
    const price = p.price_text || (Number(p.price_monthly || 0) ? `${p.price_monthly} ₽` : "0 ₽");
    return `
      <button class="plan-item-row ${isCurrent ? "muted-plan" : ""}" data-plan-key="${escapeHTML(k)}" type="button">
        <div class="plan-main">
          <h4>${escapeHTML(p.title)}</h4>
          <small>${escapeHTML(p.description)}</small>
        </div>
        <div class="plan-price">${escapeHTML(price)}</div>
      </button>
    `;
  }).join("");
}

function selectPlan(planKey) {
  state.activePlanKey = planKey;
  state.activePlan = state.plans[planKey];
  if (!state.activePlan) return;

  const planList = $("billingPlanList");
  if (planList) planList.hidden = true;
  if ($("billingTitle")) $("billingTitle").textContent = `Оплата: ${state.activePlan.title}`;
  if ($("billingError")) $("billingError").hidden = true;

  const box = $("paymentProviderBox");
  if (box) box.hidden = false;

  const provList = $("providerList");
  if (!provList) return;
  const providers = Array.isArray(state.activePlan.providers) ? state.activePlan.providers : [];
  if (!providers.length) {
    provList.innerHTML = `<p class="muted" style="text-align:center; padding:16px;">Способы оплаты временно недоступны.</p>`;
    return;
  }

  provList.innerHTML = providers.map((p) => {
    const id = p.id || p.provider;
    let iconName = "credit-card";
    let premiumCls = "";
    if (id === "telegram_stars" || id === "stars") { iconName = "tg_stars"; premiumCls = "provider-row-stars"; }
    if (id === "ton" || id === "crypto") { iconName = "ton"; premiumCls = "provider-row-ton"; }
    if (id === "btc" || id === "btcpay_btc") { iconName = "btc"; premiumCls = "provider-row-btc"; }
    const price = p.price_formatted || state.activePlan.price_text || (Number(state.activePlan.price_monthly || 0) ? `${state.activePlan.price_monthly} ₽` : "");

    return `
      <button class="provider-item-row ${premiumCls}" data-provider="${escapeHTML(id)}" type="button">
        <span class="provider-icon" data-icon="${iconName}"></span>
        <div class="provider-info">
          <strong>${escapeHTML(p.title || providerTitle(id))}</strong>
          <small>${escapeHTML(p.description || "")}</small>
        </div>
        <div class="provider-price-tag">${escapeHTML(price)}</div>
      </button>
    `;
  }).join("");
  injectIcons(provList);
}

async function createPaymentOrder(providerId) {
  const payload = {
    plan: state.activePlanKey,
    provider: providerId,
    telegram_user_id: getTelegramUserId()
  };
  try {
    return await request("/api/billing/create-order", { method: "POST", body: JSON.stringify(payload) });
  } catch (err) {
    return await request("/api/billing/checkout", { method: "POST", body: JSON.stringify(payload) });
  }
}

async function checkout(providerId) {
  const pBox = $("paymentProviderBox");
  const errEl = $("billingError");
  if (errEl) errEl.hidden = true;

  try {
    pBox?.classList.add("loading-state");
    const res = await createPaymentOrder(providerId);
    const invoiceLink = res.invoice_link || res.payment_link;
    const paymentUrl = res.invoice_url || res.payment_url || res.url || res.confirmation_url;
    const orderId = res.order_id || res.id;

    if ((providerId === "telegram_stars" || providerId === "stars") && invoiceLink) {
      if (tg?.openInvoice) {
        tg.openInvoice(invoiceLink, (status) => {
          if (status === "paid") {
            showToast("Успешно оплачено!");
            closeBillingModal();
            loadMe().catch(() => {});
          } else if (status === "cancelled") {
            showToast("Оплата отменена");
          } else {
            showToast("Не удалось проверить оплату");
          }
        });
      } else {
        showToast("Оплата Stars работает внутри Telegram");
      }
      return;
    }

    if (paymentUrl) {
      if (tg?.openLink) tg.openLink(paymentUrl);
      else window.open(paymentUrl, "_blank", "noopener,noreferrer");
      showToast(providerId === "ton" || providerId === "crypto" ? "Оплата TON будет подтверждена после проверки транзакции." : "Ссылка на оплату открыта");
      if (orderId) pollOrderStatus(orderId);
      closeBillingModal();
      return;
    }

    if (res.success || res.ok || res.status === "paid") {
      showToast("Подписка активирована!");
      closeBillingModal();
      await loadMe();
      return;
    }

    throw new Error("Не удалось получить ссылку на оплату");
  } catch (err) {
    if (errEl) {
      errEl.textContent = err.message;
      errEl.hidden = false;
    } else {
      showToast(err.message);
    }
  } finally {
    pBox?.classList.remove("loading-state");
  }
}

function pollOrderStatus(orderId) {
  if (!orderId) return;
  let attempts = 0;
  const timer = window.setInterval(async () => {
    attempts++;
    if (attempts > 30) {
      clearInterval(timer);
      state.pollingTimers.delete(timer);
      showToast("Не удалось проверить оплату автоматически. Проверьте профиль позже.");
      return;
    }
    const data = await requestMaybe(`/api/billing/order/${encodeURIComponent(orderId)}`, { method: "GET" }, null);
    const status = String(data?.status || data?.order?.status || "").toLowerCase();
    if (["paid", "success", "succeeded", "completed", "active"].includes(status)) {
      clearInterval(timer);
      state.pollingTimers.delete(timer);
      showToast("Оплата прошла успешно!");
      loadMe().catch(() => {});
    } else if (["failed", "canceled", "cancelled", "expired"].includes(status)) {
      clearInterval(timer);
      state.pollingTimers.delete(timer);
      showToast("Оплата отменена или не прошла");
    }
  }, 4000);
  state.pollingTimers.add(timer);
}

async function loadHistory() {
  const data = await requestMaybe("/api/history", { method: "GET" }, { history: [] });
  state.history = normalizeHistory(data);
  renderHistory();
}

function renderHistory() {
  const list = $("historyList");
  if (!list) return;

  let filtered = state.history;
  if (state.historyFilter !== "all") {
    filtered = state.history.filter((h) => h.mode === state.historyFilter || h.type === state.historyFilter);
  }

  if (!filtered.length) {
    list.innerHTML = `<div class="chat-empty"><span data-icon="history"></span><p>Записей нет.</p></div>`;
    injectIcons(list);
    return;
  }

  list.innerHTML = filtered.map((h) => `
    <article class="history-row">
      <div class="history-meta-line">
        <span class="badge">${escapeHTML(String(h.mode || h.type || "AI").toUpperCase())}</span>
        <time class="muted small">${escapeHTML(formatDate(h.timestamp))}</time>
      </div>
      <p class="history-prompt">Запрос: ${escapeHTML(h.text || h.title || "")}</p>
      <div class="history-answer">${escapeHTML(h.answer || "")}</div>
    </article>
  `).join("");
}

function bindEvents() {
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => switchView(btn.dataset.target));
  });

  document.querySelectorAll("[data-open-view]").forEach((btn) => {
    btn.addEventListener("click", () => switchView(btn.dataset.openView));
  });

  const txtHome = $("homeChatInput"), btnHome = $("homeChatSendBtn");
  if (txtHome && btnHome) {
    txtHome.addEventListener("input", () => {
      autoResizeTextarea(txtHome);
      updateChatSendButton("homeChatInput", "homeChatSendBtn");
    });
    btnHome.addEventListener("click", () => handleChatSend("homeChatInput", "homeChatScroll", "homeChatSendBtn"));
    txtHome.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleChatSend("homeChatInput", "homeChatScroll", "homeChatSendBtn");
      }
    });
  }

  const txtMain = $("mainChatInput"), btnMain = $("mainChatSendBtn");
  if (txtMain && btnMain) {
    txtMain.addEventListener("input", () => {
      autoResizeTextarea(txtMain);
      updateChatSendButton("mainChatInput", "mainChatSendBtn");
    });
    btnMain.addEventListener("click", () => handleChatSend("mainChatInput", "mainChatScroll", "mainChatSendBtn"));
  }

  document.querySelectorAll(".chat-mode-selector .mode-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".chat-mode-selector .mode-tab").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      state.currentMode = tab.dataset.mode;
    });
  });

  $("quickStrip")?.addEventListener("click", (e) => {
    const act = e.target.closest(".quick-action");
    if (!act) return;
    const targetInput = $("mainChatInput") || $("homeChatInput");
    if ($("mainChatInput")) switchView("chat");
    if (targetInput) {
      targetInput.value = act.dataset.prompt || "";
      autoResizeTextarea(targetInput);
      updateChatSendButton(targetInput.id, targetInput.id === "mainChatInput" ? "mainChatSendBtn" : "homeChatSendBtn");
      targetInput.focus();
    }
  });

  $("toolsGrid")?.addEventListener("click", (e) => {
    const card = e.target.closest(".tool-item-row");
    if (!card) return;
    const targetInput = $("mainChatInput") || $("homeChatInput");
    if ($("mainChatInput")) switchView("chat");
    if (targetInput) {
      targetInput.value = card.dataset.prompt || "";
      autoResizeTextarea(targetInput);
      updateChatSendButton(targetInput.id, targetInput.id === "mainChatInput" ? "mainChatSendBtn" : "homeChatSendBtn");
      targetInput.focus();
    }
  });

  $("onboardingBody")?.addEventListener("click", (e) => {
    const opt = e.target.closest(".onboarding-option");
    if (!opt) return;
    const cfg = state.onboardingConfig[state.onboardingStep];
    state.onboardingData[cfg.id] = opt.dataset.key;
    renderOnboardingStep();
  });

  $("saveProfileBtn")?.addEventListener("click", async () => {
    const profileText = $("profileBusinessDescription")?.value.trim() || "";
    try {
      let res;
      try {
        res = await request("/api/profile/save", { method: "POST", body: JSON.stringify({ business_profile: profileText }) });
      } catch {
        res = await request("/api/business-profile", { method: "POST", body: JSON.stringify({ telegram_user_id: getTelegramUserId(), description: profileText }) });
      }
      state.user = normalizeUser(res.user ? res : { ...state.user, business_profile: profileText });
      updateProfileUI();
      showToast("Сохранено!");
    } catch (err) {
      showToast(err.message);
    }
  });

  $("submitAppFeedbackBtn")?.addEventListener("click", async () => {
    const msg = $("appFeedbackText")?.value.trim() || "";
    if (!msg) {
      showToast("Напишите текст");
      return;
    }
    try {
      await request("/api/feedback", { method: "POST", body: JSON.stringify({ message: msg, type: "app", telegram_user_id: getTelegramUserId() }) });
      $("appFeedbackText").value = "";
      showToast("Спасибо за отзыв!");
    } catch (err) {
      showToast(err.message);
    }
  });

  $("openBillingBtn")?.addEventListener("click", openBillingModal);
  $("closeBillingBtn")?.addEventListener("click", closeBillingModal);
  $("backToPlansBtn")?.addEventListener("click", renderBillingPlans);

  $("billingModal")?.addEventListener("click", (e) => {
    if (e.target === $("billingModal")) closeBillingModal();
  });

  $("billingPlanList")?.addEventListener("click", (e) => {
    const card = e.target.closest("[data-plan-key]");
    if (card) selectPlan(card.dataset.planKey);
  });

  $("providerList")?.addEventListener("click", (e) => {
    const card = e.target.closest("[data-provider]");
    if (card) checkout(card.dataset.provider);
  });

  $("onboardingNextBtn")?.addEventListener("click", nextOnboarding);
  $("onboardingBackBtn")?.addEventListener("click", previousOnboarding);

  $("historyFilters")?.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-filter]");
    if (!btn) return;
    state.historyFilter = btn.dataset.filter;
    $("historyFilters").querySelectorAll("button").forEach((n) => n.classList.toggle("active", n === btn));
    renderHistory();
  });

  $("headerProfileBtn")?.addEventListener("click", () => switchView("profile"));
}

(async function boot() {
  injectIcons();
  initTelegram();
  bindEvents();
  updateChatSendButton("homeChatInput", "homeChatSendBtn");
  updateChatSendButton("mainChatInput", "mainChatSendBtn");

  await Promise.allSettled([loadTools(), loadBillingPlans(), loadHistory()]);
  try {
    await loadMe();
  } catch (error) {
    state.user = normalizeUser({});
    updateProfileUI();
    showToast(error.message);
  }
})();
