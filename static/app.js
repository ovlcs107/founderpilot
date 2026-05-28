/**
 * FounderPilot AI - Frontend App (Vanilla JS)
 * Premium Minimal SaaS Edition
 */

const tg = window.Telegram?.WebApp || null;

// Strict Whitelist inline SVG icons (Apple/Linear style - 24x24 stroke)
const iconPaths = {
  home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline>',
  tools: '<rect x="3" y="3" width="7" height="7" rx="1"></rect><rect x="14" y="3" width="7" height="7" rx="1"></rect><rect x="14" y="14" width="7" height="7" rx="1"></rect><rect x="3" y="14" width="7" height="7" rx="1"></rect>',
  history: '<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>',
  user: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>',
  send: '<line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>',
  close: '<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>',
  back: '<line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline>',
  copy: '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>',
  save: '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline>',
  edit: '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>',
  chart: '<line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line>',
  wallet: '<path d="M22 12V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2"></path><rect x="18" y="10" width="4" height="4"></rect>',
  calculator: '<rect x="4" y="2" width="16" height="20" rx="2"></rect><line x1="8" y1="6" x2="16" y2="6"></line><line x1="8" y1="10" x2="8" y2="10"></line><line x1="12" y1="10" x2="12" y2="10"></line><line x1="16" y1="10" x2="16" y2="10"></line>',
  target: '<circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle>',
  search: '<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>',
  message: '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>',
  'credit-card': '<rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line>',
  stars: '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>',
  ton: '<polygon points="12 2 3 9 12 22 21 9 12 2"></polygon><polyline points="3 9 12 13 21 9"></polyline><line x1="12" y1="22" x2="12" y2="13"></line>',
  btc: '<path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path><path d="M10 8h2.5a1.5 1.5 0 0 1 0 3H10V8z"></path><path d="M10 13h3a1.5 1.5 0 0 1 0 3h-3v-3z"></path><path d="M12 5v2"></path><path d="M12 17v2"></path>',
  settings: '<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>',
  check: '<polyline points="20 6 9 17 4 12"></polyline>',
  warning: '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>'
};

// Global State
const state = {
  user: null,
  tools: [],
  plans: {},
  providers: [],
  history: [],
  historyFilter: "all",
  activeView: "home",
  activePlanKey: null,
  isSending: false,
  onboardingStep: 0,
  onboardingData: {},
  orderPollTimer: null,
  toastTimer: null,
  
  onboardingConfig: [
    { id: "role", title: "Чем вы занимаетесь?", type: "choices", options: [
      { key: "wb_seller", label: "Селлер WB/Ozon" },
      { key: "entrepreneur", label: "Предприниматель" },
      { key: "marketer", label: "Маркетолог" },
      { key: "beginner", label: "Новичок" },
      { key: "other", label: "Другое" }
    ]},
    { id: "pain", title: "Что хотите улучшить?", type: "choices", options: [
      { key: "sales", label: "Продажи" },
      { key: "cards", label: "Карточки товара" },
      { key: "ads", label: "Рекламу" },
      { key: "ideas", label: "Идеи товара" },
      { key: "strategy", label: "Стратегию" },
      { key: "unit", label: "Расчёты" }
    ]},
    { id: "desc", title: "Коротко опишите бизнес", type: "textarea", placeholder: "Например: продаю автотовары на WB, хочу поднять маржу" }
  ]
};

// DOM Utilities
const $ = (id) => document.getElementById(id);

function escapeHTML(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function injectIcons(root = document) {
  root.querySelectorAll("[data-icon]").forEach(el => {
    const name = el.getAttribute("data-icon");
    if (iconPaths[name] && !el.querySelector("svg")) {
      el.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${iconPaths[name]}</svg>`;
    }
  });
}

function showToast(msg) {
  const el = $("toast");
  if (!el) return;
  el.textContent = msg;
  el.classList.add("visible");
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => el.classList.remove("visible"), 2500);
}

// API Handlers
function getTelegramUserId() {
  return String(tg?.initDataUnsafe?.user?.id || state.user?.telegram_id || "dev");
}

async function apiRequest(url, options = {}) {
  const headers = { "Content-Type": "application/json" };
  if (tg?.initData) headers["X-Telegram-Init-Data"] = tg.initData;
  
  const res = await fetch(url, { ...options, headers: { ...headers, ...options.headers } });
  const text = await res.text();
  let data = null;
  try { data = JSON.parse(text); } catch { data = { detail: text }; }
  
  if (!res.ok || data?.ok === false) {
    throw new Error(data?.error || data?.detail || data?.message || "Ошибка сервера");
  }
  return data ?? {};
}

async function apiTry(urlPrimary, urlFallback, options = {}) {
  try { return await apiRequest(urlPrimary, options); }
  catch (err) {
    if (urlFallback) return await apiRequest(urlFallback, options);
    throw err;
  }
}

// Normalizers
function normalizeUserResponse(data) {
  const root = data?.user || data || {};
  const tgUser = tg?.initDataUnsafe?.user || {};

  const dailyLimit = Number(root.credits_daily_limit ?? root.daily_credits_limit ?? root.daily_limit ?? root.limit_today ?? 100);
  const monthlyLimit = Number(root.credits_monthly_limit ?? root.monthly_credits_limit ?? root.monthly_limit ?? root.period_limit ?? 0);

  let dailyUsed = Number(root.credits_used_today ?? root.used_today ?? root.daily_used ?? 0);
  let monthlyUsed = Number(root.credits_used_month ?? root.used_period ?? root.monthly_used ?? 0);

  if (root.remaining_credits_today !== undefined && dailyLimit) {
    dailyUsed = Math.max(0, dailyLimit - Number(root.remaining_credits_today));
  } else if (root.remaining !== undefined && dailyLimit) {
    dailyUsed = Math.max(0, dailyLimit - Number(root.remaining));
  }

  if (root.remaining_credits_month !== undefined && monthlyLimit) {
    monthlyUsed = Math.max(0, monthlyLimit - Number(root.remaining_credits_month));
  }
  
  return {
    telegram_id: root.telegram_id || root.id || tgUser.id || "dev",
    first_name: root.first_name || root.name || tgUser.first_name || "Пользователь",
    username: root.username || tgUser.username || "",
    plan: root.plan || root.plan_name || "Free",
    daily_limit: dailyLimit,
    daily_used: dailyUsed,
    monthly_limit: monthlyLimit,
    monthly_used: monthlyUsed,
    business_profile: root.business_profile || root.description || "",
    onboarding_required: Boolean(data?.onboarding_required || root.onboarding_required)
  };
}

function normalizeBillingPlans(data) {
  const rawPlans = data?.plans || data || {};
  const globalProviders = Array.isArray(data?.providers) ? data.providers : [];
  const result = {};

  if (Array.isArray(rawPlans)) {
    rawPlans.forEach((plan) => {
      const key = String(plan.key || plan.id || plan.slug || plan.name || plan.title || "").toLowerCase();
      if (!key) return;
      result[key] = {
        ...plan,
        key,
        providers: Array.isArray(plan.providers) && plan.providers.length ? plan.providers : globalProviders
      };
    });
  } else if (rawPlans && typeof rawPlans === "object") {
    Object.entries(rawPlans).forEach(([key, plan]) => {
      if (!plan || typeof plan !== "object") return;
      result[key] = {
        ...plan,
        key: plan.key || key,
        providers: Array.isArray(plan.providers) && plan.providers.length ? plan.providers : globalProviders
      };
    });
  }

  state.providers = globalProviders;
  return result;
}

function normalizeToolsResponse(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.tools)) return data.tools;
  if (Array.isArray(data?.items)) return data.items;
  return [];
}

function normalizeHistoryResponse(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.history)) return data.history;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

function getFallbackTools() {
  return [
    { id: "margin", title: "Расчёт маржи", description: "Быстрая юнит-экономика и прогноз", prompt_template: "Помоги рассчитать маржу товара. Данные: ", icon: "calculator" },
    { id: "product-card", title: "Карточка товара", description: "Описание и SEO для маркетплейсов", prompt_template: "Улучши описание и SEO карточки товара для WB/Ozon: ", icon: "edit" },
    { id: "offer", title: "Создать оффер", description: "Сильное предложение для акции", prompt_template: "Сделай сильный оффер для продукта: ", icon: "target" },
    { id: "competitor", title: "Анализ конкурента", description: "Разбор сильных и слабых сторон", prompt_template: "Разбери плюсы и минусы конкурента: ", icon: "search" },
    { id: "review", title: "Ответ на отзыв", description: "Спокойный и грамотный ответ клиенту", prompt_template: "Напиши ответ на этот отзыв клиента: ", icon: "message" },
    { id: "plan", title: "Контент-план", description: "План публикаций на неделю", prompt_template: "Составь контент-план на неделю для: ", icon: "history" }
  ];
}

function getPlanProviders(plan) {
  if (Array.isArray(plan?.providers) && plan.providers.length) return plan.providers;
  if (Array.isArray(state.providers) && state.providers.length) return state.providers;
  return [
    { id: "telegram_stars", title: "Telegram Stars", description: "Внутри Telegram" },
    { id: "yookassa", title: "Карта / СБП", description: "Банковские карты РФ" },
    { id: "ton", title: "TON", description: "Оплата криптовалютой" }
  ];
}

function updateSendButton() {
  const input = $("homeChatInput");
  const btn = $("homeChatSendBtn");
  if (input && btn) btn.disabled = !input.value.trim() || state.isSending;
}

// UI Updaters
function switchView(target) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(b => b.classList.toggle("active", b.dataset.target === target));
  
  const v = $(`view-${target}`);
  if (v) v.classList.add("active");
  
  const titles = { home: "Главная", tools: "Инструменты", history: "История", profile: "Профиль" };
  if ($("pageTitle")) $("pageTitle").textContent = titles[target] || "FounderPilot";
  
  state.activeView = target;
  if (target === "tools" && !state.tools.length) loadTools();
  if (target === "history" && !state.history.length) loadHistory();
}

function updateCreditsUI() {
  if (!state.user) return;
  const u = state.user;
  
  const format = (used, limit) => {
    if (!limit) return "Безлимит";
    const remain = Math.max(0, limit - used);
    return `${remain} / ${limit}`;
  };
  
  const calcPct = (used, limit) => limit ? Math.min(100, (used / limit) * 100) : 0;

  const tTxt = format(u.daily_used, u.daily_limit);
  const tPct = calcPct(u.daily_used, u.daily_limit);
  const mTxt = format(u.monthly_used, u.monthly_limit);
  const mPct = calcPct(u.monthly_used, u.monthly_limit);

  if ($("creditsTodayText")) $("creditsTodayText").textContent = tTxt;
  if ($("creditsTodayFill")) $("creditsTodayFill").style.width = `${tPct}%`;
  
  if ($("creditsMonthText")) $("creditsMonthText").textContent = mTxt;
  if ($("creditsMonthFill")) $("creditsMonthFill").style.width = `${mPct}%`;
  
  if ($("profileCreditsTodayText")) $("profileCreditsTodayText").textContent = tTxt;
  if ($("profileCreditsTodayFill")) $("profileCreditsTodayFill").style.width = `${tPct}%`;
  
  if ($("profileCreditsMonthText")) $("profileCreditsMonthText").textContent = mTxt;
  if ($("profileCreditsMonthFill")) $("profileCreditsMonthFill").style.width = `${mPct}%`;
}

function updateProfileUI() {
  if (!state.user) return;
  const u = state.user;
  const initial = u.first_name.charAt(0).toUpperCase() || "F";
  
  if ($("homeGreeting")) $("homeGreeting").textContent = `Здравствуйте, ${u.first_name}`;
  if ($("headerUserAvatar")) $("headerUserAvatar").textContent = initial;
  if ($("profileUserAvatar")) $("profileUserAvatar").textContent = initial;
  if ($("profileUserTitle")) $("profileUserTitle").textContent = u.username ? `@${u.username}` : u.first_name;
  if ($("profileUserSubtitle")) $("profileUserSubtitle").textContent = `ID: ${u.telegram_id}`;
  if ($("profilePlanLabel")) $("profilePlanLabel").textContent = String(u.plan).toUpperCase();
  if ($("profileBusinessDescription")) $("profileBusinessDescription").value = u.business_profile;
  
  updateCreditsUI();
}

// Chat Logic
function autoResizeTextarea(el) {
  if (!el) return;
  el.style.height = "20px";
  el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
}

function appendMessage(role, text, id = null) {
  const scroll = $("homeChatScroll");
  if (!scroll) return null;
  
  const empty = $("chatEmptyState");
  if (empty) empty.remove();
  
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;
  if (id) wrap.id = id;
  
  const txtDiv = document.createElement("div");
  txtDiv.textContent = text; 
  wrap.appendChild(txtDiv);
  
  if (role === "bot" && text !== "FounderPilot готовит ответ...") {
    const act = document.createElement("div");
    act.className = "message-actions";
    
    const copyBtn = document.createElement("button");
    copyBtn.type = "button";
    copyBtn.innerHTML = `<span data-icon="copy"></span> Скопировать`;
    copyBtn.addEventListener("click", () => {
      navigator.clipboard.writeText(text).then(() => showToast("Скопировано"));
    });
    
    const saveBtn = document.createElement("button");
    saveBtn.type = "button";
    saveBtn.innerHTML = `<span data-icon="save"></span> Сохранить`;
    saveBtn.addEventListener("click", async () => {
      try {
        await apiRequest("/api/saved", { method: "POST", body: JSON.stringify({ telegram_user_id: getTelegramUserId(), content: text }) });
        showToast("Сохранено в Историю");
      } catch {
        showToast("Не удалось сохранить");
      }
    });

    const shorterBtn = document.createElement("button");
    shorterBtn.type = "button";
    shorterBtn.innerHTML = `<span data-icon="edit"></span> Короче`;
    shorterBtn.addEventListener("click", () => {
        const input = $("homeChatInput");
        if(input) { input.value = "Сделай ответ короче"; input.focus(); autoResizeTextarea(input); updateSendButton(); }
    });

    const detailsBtn = document.createElement("button");
    detailsBtn.type = "button";
    detailsBtn.innerHTML = `<span data-icon="search"></span> Подробнее`;
    detailsBtn.addEventListener("click", () => {
        const input = $("homeChatInput");
        if(input) { input.value = "Распиши подробнее"; input.focus(); autoResizeTextarea(input); updateSendButton(); }
    });

    act.appendChild(copyBtn);
    act.appendChild(saveBtn);
    act.appendChild(shorterBtn);
    act.appendChild(detailsBtn);
    wrap.appendChild(act);
  }
  
  scroll.appendChild(wrap);
  scroll.scrollTop = scroll.scrollHeight;
  injectIcons(wrap);
  return wrap;
}

async function handleChatSend() {
  const input = $("homeChatInput");
  const text = input?.value.trim();
  if (!text || state.isSending) return;
  
  state.isSending = true;
  $("homeChatSendBtn").disabled = true;
  input.value = "";
  autoResizeTextarea(input);
  
  appendMessage("user", text);
  const sysId = `sys_${Date.now()}`;
  appendMessage("system", "FounderPilot готовит ответ...", sysId);
  
  try {
    const payload = { telegram_user_id: getTelegramUserId(), message: text, text: text, mode: "chat" };
    const res = await apiTry("/api/chat", "/api/ask", { method: "POST", body: JSON.stringify(payload) });
    
    $(sysId)?.remove();
    const answer = res.answer || res.response || res.result || res.text || "Пустой ответ";
    appendMessage("bot", answer);
    
    if (state.user) {
      if (res.usage?.credits_used_today !== undefined) state.user.daily_used = res.usage.credits_used_today;
      else if (res.used_today !== undefined) state.user.daily_used = res.used_today;
      else if (res.usage?.daily_used !== undefined) state.user.daily_used = res.usage.daily_used;
      
      if (res.usage?.credits_used_month !== undefined) state.user.monthly_used = res.usage.credits_used_month;
      else if (res.credits_used_month !== undefined) state.user.monthly_used = res.credits_used_month;
      else if (res.used_period !== undefined) state.user.monthly_used = res.used_period;
      else if (res.usage?.used_period !== undefined) state.user.monthly_used = res.usage.used_period;
      
      updateCreditsUI();
    }
  } catch (err) {
    const sys = $(sysId);
    if (sys) sys.textContent = "Ошибка: " + err.message;
    else showToast(err.message);
  } finally {
    state.isSending = false;
    updateSendButton();
  }
}

// API Loaders
async function loadMe() {
  try {
    const data = await apiRequest("/api/me");
    state.user = normalizeUserResponse(data);
    updateProfileUI();
    if (state.user.onboarding_required) openOnboarding();
  } catch (err) {
    console.error("loadMe fail:", err);
  }
}

async function loadTools() {
  const grid = $("toolsGrid");
  try {
    const data = await apiRequest("/api/tools");
    const tools = normalizeToolsResponse(data);
    state.tools = tools.length ? tools : getFallbackTools();
  } catch {
    state.tools = getFallbackTools();
  }

  if (!grid) return;
  if (!state.tools.length) {
    grid.innerHTML = `<div class="skeleton-state">Инструменты временно недоступны.</div>`;
    return;
  }

  grid.innerHTML = state.tools.map(t => {
    const iconKey = t.icon || "tools";
    return `
      <div class="tool-item-row" data-prompt="${escapeHTML(t.prompt_template || t.prompt || '')}">
        <div class="tool-icon-box"><span data-icon="${iconKey}"></span></div>
        <div class="tool-text-box">
          <h4>${escapeHTML(t.title || t.name || 'Инструмент')}</h4>
          <p class="muted">${escapeHTML(t.description || t.subtitle || 'Готовый сценарий')}</p>
        </div>
      </div>
    `;
  }).join("");
  injectIcons(grid);
}

async function loadHistory() {
  const list = $("historyList");
  try {
    const data = await apiRequest("/api/history");
    const arr = normalizeHistoryResponse(data);
    state.history = arr;
    renderHistory();
  } catch {
    if (list) list.innerHTML = `<div class="skeleton-state">Не удалось загрузить историю.</div>`;
  }
}

function renderHistory() {
  const list = $("historyList");
  if (!list) return;
  
  let filtered = state.history;
  
  if (state.historyFilter === "favorites") {
    filtered = state.history.filter(h => h.is_saved || h.is_favorite || h.type === "saved" || h.type === "favorites");
  } else if (state.historyFilter === "tools") {
    filtered = state.history.filter(h => {
      const type = String(h.mode || h.type || "").toLowerCase();
      return type === "tool" || type === "tools" || (type && type !== "chat" && type !== "message");
    });
  } else if (state.historyFilter !== "all") {
    filtered = state.history.filter(h => String(h.mode || h.type || "").toLowerCase() === state.historyFilter);
  }
  
  if (!filtered.length) {
    list.innerHTML = `
      <div class="empty-state">
        <span data-icon="history"></span>
        <h3>Истории пока нет</h3>
        <p>Ваши запросы и сохранённые ответы появятся здесь.</p>
      </div>`;
    injectIcons(list);
    return;
  }
  
  list.innerHTML = filtered.map(h => {
    const type = String(h.mode || h.type || "chat").toUpperCase();
    const title = h.title || h.prompt || h.text || "Запрос";
    const preview = h.answer || h.content || h.result || "";
    return `
      <article class="history-row">
        <span class="badge">${escapeHTML(type)}</span>
        <h4>${escapeHTML(title)}</h4>
        <p>${escapeHTML(preview)}</p>
      </article>
    `;
  }).join("");
}

// Billing
async function loadBillingPlans() {
  try {
    const data = await apiRequest("/api/billing/plans");
    state.plans = normalizeBillingPlans(data);
  } catch (err) {
    console.error("billing fail", err);
    state.plans = normalizeBillingPlans({
      plans: [
        { key: "free", title: "Free", description: "100 кредитов в день", price_text: "0 ₽", providers: [] },
        { key: "pro", title: "Pro", description: "500 кредитов в день · 10 000 в месяц", price_text: "299 ₽/мес" },
        { key: "business", title: "Business", description: "3 000 кредитов в день · 60 000 в месяц", price_text: "1 990 ₽/мес" }
      ]
    });
  }
}

function openBillingModal() {
  const m = $("billingModal");
  if (!m) return;
  m.hidden = false;
  
  const list = $("billingPlanList");
  const pBox = $("paymentProviderBox");
  list.hidden = false;
  pBox.hidden = true;
  $("billingTitle").textContent = "Тарифные планы";
  
  const keys = Object.keys(state.plans || {});
  if (!keys.length) {
    list.innerHTML = `<div class="skeleton-state">Тарифы временно недоступны.</div>`;
    return;
  }
  
  list.innerHTML = keys.map(k => {
    const p = state.plans[k];
    const isCurrent = state.user && String(state.user.plan).toLowerCase() === k.toLowerCase();
    const price = p.price_text || (p.price_monthly ? `${p.price_monthly} ₽` : "Бесплатно");
    return `
      <button class="plan-item-row ${isCurrent ? 'active' : ''}" data-plan="${escapeHTML(k)}" type="button">
        <div class="plan-main">
          <h4>${escapeHTML(p.title || k)}</h4>
          <small>${escapeHTML(p.description || '')}</small>
        </div>
        <div class="plan-price">${escapeHTML(price)}</div>
      </button>
    `;
  }).join("");
}

function selectPlan(key) {
  state.activePlanKey = key;
  const p = state.plans[key];
  if (!p) return;
  
  $("billingPlanList").hidden = true;
  $("paymentProviderBox").hidden = false;
  $("billingTitle").textContent = `Оплата: ${p.title}`;
  $("billingError").hidden = true;
  
  const provList = $("providerList");
  const providers = getPlanProviders(p);
  
  provList.innerHTML = providers.map(pr => {
    const id = String(pr.id || pr.provider).toLowerCase();
    
    let icon = "credit-card";
    if (id.includes("star")) icon = "stars";
    if (id.includes("sbp") || id.includes("yookassa")) icon = "target";
    if (id.includes("ton")) icon = "ton";
    if (id.includes("btc")) icon = "btc";
    
    return `
      <button class="provider-item-row" data-provider="${escapeHTML(id)}" type="button">
        <span class="provider-icon" data-icon="${icon}"></span>
        <div class="provider-info">
          <strong>${escapeHTML(pr.title || pr.name || id)}</strong>
          <small>${escapeHTML(pr.description || '')}</small>
        </div>
        ${pr.price_formatted ? `<div class="provider-price-tag">${escapeHTML(pr.price_formatted)}</div>` : ""}
      </button>
    `;
  }).join("");
  
  injectIcons(provList);
}

async function checkout(providerId) {
  const errEl = $("billingError");
  errEl.hidden = true;
  showToast("Создание платежа...");
  
  try {
    const payload = { plan: state.activePlanKey, provider: providerId, telegram_user_id: getTelegramUserId() };
    const res = await apiTry("/api/billing/create-order", "/api/billing/checkout", { method: "POST", body: JSON.stringify(payload) });
    
    const link = res.invoice_link || res.invoice_url || res.payment_url || res.url;
    const orderId = res.order_id || res.id;
    
    if ((providerId.includes("star")) && link && tg?.openInvoice) {
      tg.openInvoice(link, (status) => {
        if (status === "paid") { showToast("Оплата прошла"); loadMe(); $("billingModal").hidden = true; }
        else if (status === "cancelled") showToast("Оплата отменена");
      });
      return;
    }
    
    if (link) {
      if (tg?.openLink) tg.openLink(link);
      else window.open(link, "_blank");
      if (orderId) pollOrderStatus(orderId);
      $("billingModal").hidden = true;
      return;
    }
    
    if (res.ok || res.success) {
      showToast("Успешно");
      loadMe();
      $("billingModal").hidden = true;
      return;
    }
    throw new Error("Не удалось получить ссылку");
  } catch (err) {
    errEl.textContent = err.message;
    errEl.hidden = false;
  }
}

function pollOrderStatus(orderId) {
  let attempts = 0;
  clearInterval(state.orderPollTimer);
  state.orderPollTimer = setInterval(async () => {
    attempts++;
    if (attempts > 20) { clearInterval(state.orderPollTimer); return; }
    try {
      const data = await apiRequest(`/api/billing/order/${orderId}`);
      const s = String(data.status || "").toLowerCase();
      if (["paid", "success", "active"].includes(s)) {
        clearInterval(state.orderPollTimer);
        showToast("Оплата получена");
        loadMe();
      } else if (["failed", "cancelled", "expired"].includes(s)) {
        clearInterval(state.orderPollTimer);
        showToast("Оплата не прошла");
      }
    } catch { /* ignore */ }
  }, 5000);
}

// Onboarding
function openOnboarding() {
  state.onboardingStep = 0;
  state.onboardingData = {};
  const m = $("onboardingModal");
  if (m) { m.hidden = false; renderOnboardingStep(); }
}

function renderOnboardingStep() {
  const cfg = state.onboardingConfig[state.onboardingStep];
  if (!cfg) return;
  
  $("onboardingTitle").textContent = cfg.title;
  $("onboardingError").hidden = true;
  
  const dots = $("onboardingProgressRow")?.querySelectorAll("span");
  if (dots) dots.forEach((d, i) => d.classList.toggle("active", i <= state.onboardingStep));
  
  const body = $("onboardingBody");
  body.innerHTML = "";
  
  if (cfg.type === "textarea") {
    const ta = document.createElement("textarea");
    ta.className = "profile-textarea";
    ta.rows = 4;
    ta.placeholder = cfg.placeholder;
    ta.value = state.onboardingData[cfg.id] || "";
    ta.oninput = () => state.onboardingData[cfg.id] = ta.value;
    body.appendChild(ta);
  } else {
    cfg.options.forEach(o => {
      const b = document.createElement("button");
      b.className = `onboarding-option ${state.onboardingData[cfg.id] === o.key ? 'active' : ''}`;
      b.textContent = o.label;
      b.onclick = () => { state.onboardingData[cfg.id] = o.key; renderOnboardingStep(); };
      body.appendChild(b);
    });
  }
  
  $("onboardingBackBtn").disabled = state.onboardingStep === 0;
  $("onboardingNextBtn").textContent = state.onboardingStep === state.onboardingConfig.length - 1 ? "Завершить" : "Далее";
}

async function nextOnboarding() {
  const cfg = state.onboardingConfig[state.onboardingStep];
  const val = state.onboardingData[cfg.id];
  
  if (!val || !String(val).trim()) {
    $("onboardingError").textContent = "Пожалуйста, заполните это поле.";
    $("onboardingError").hidden = false;
    return;
  }
  
  if (state.onboardingStep < state.onboardingConfig.length - 1) {
    state.onboardingStep++;
    renderOnboardingStep();
    return;
  }
  
  $("onboardingNextBtn").disabled = true;
  try {
    await apiRequest("/api/onboarding", { method: "POST", body: JSON.stringify(state.onboardingData) });
    $("onboardingModal").hidden = true;
    showToast("Профиль настроен");
    loadMe();
  } catch {
    $("onboardingModal").hidden = true;
    showToast("Профиль можно заполнить позже.");
  } finally {
    $("onboardingNextBtn").disabled = false;
  }
}

// Events
function bindEvents() {
  // Nav
  document.querySelectorAll(".nav-item").forEach(b => {
    b.addEventListener("click", () => switchView(b.dataset.target));
  });
  $("headerProfileBtn")?.addEventListener("click", () => switchView("profile"));
  
  // Chat
  const chatInput = $("homeChatInput");
  const chatBtn = $("homeChatSendBtn");
  if (chatInput && chatBtn) {
    chatInput.addEventListener("input", () => {
      autoResizeTextarea(chatInput);
      updateSendButton();
    });
    chatInput.addEventListener("keydown", e => {
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleChatSend(); }
    });
    chatBtn.addEventListener("click", handleChatSend);
  }
  
  // Quick Actions & Tools
  $("quickStrip")?.addEventListener("click", e => {
    const b = e.target.closest(".quick-action");
    if (b && chatInput) { chatInput.value = b.dataset.prompt; chatInput.focus(); autoResizeTextarea(chatInput); updateSendButton(); }
  });
  $("toolsGrid")?.addEventListener("click", e => {
    const r = e.target.closest(".tool-item-row");
    if (r) { switchView("home"); if(chatInput) { chatInput.value = r.dataset.prompt; chatInput.focus(); autoResizeTextarea(chatInput); updateSendButton(); } }
  });
  
  // History Filters
  $("historyFilters")?.addEventListener("click", e => {
    const b = e.target.closest(".filter-btn");
    if (!b) return;
    $("historyFilters").querySelectorAll(".filter-btn").forEach(n => n.classList.remove("active"));
    b.classList.add("active");
    state.historyFilter = b.dataset.filter;
    renderHistory();
  });
  
  // Profile Forms
  $("saveProfileBtn")?.addEventListener("click", async () => {
    const text = $("profileBusinessDescription")?.value.trim();
    try {
      await apiTry("/api/profile/save", "/api/business-profile", { method: "POST", body: JSON.stringify({ telegram_user_id: getTelegramUserId(), business_profile: text, description: text }) });
      if(state.user) state.user.business_profile = text;
      showToast("Настройки сохранены");
    } catch(err) { showToast(err.message); }
  });
  
  $("submitAppFeedbackBtn")?.addEventListener("click", async () => {
    const text = $("appFeedbackText")?.value.trim();
    if(!text) return;
    try {
      await apiRequest("/api/feedback", { method: "POST", body: JSON.stringify({ telegram_user_id: getTelegramUserId(), message: text, type: "app" }) });
      $("appFeedbackText").value = "";
      showToast("Спасибо за отзыв");
    } catch(err) { showToast(err.message); }
  });
  
  // Modals
  $("openBillingBtn")?.addEventListener("click", openBillingModal);
  $("closeBillingBtn")?.addEventListener("click", () => $("billingModal").hidden = true);
  $("backToPlansBtn")?.addEventListener("click", () => { $("paymentProviderBox").hidden = true; $("billingPlanList").hidden = false; $("billingTitle").textContent = "Тарифные планы";});
  
  $("billingPlanList")?.addEventListener("click", e => {
    const b = e.target.closest(".plan-item-row");
    if (b) selectPlan(b.dataset.plan);
  });
  $("providerList")?.addEventListener("click", e => {
    const b = e.target.closest(".provider-item-row");
    if (b) checkout(b.dataset.provider);
  });
  
  $("onboardingBackBtn")?.addEventListener("click", () => { if(state.onboardingStep > 0) { state.onboardingStep--; renderOnboardingStep(); } });
  $("onboardingNextBtn")?.addEventListener("click", nextOnboarding);
}

// Boot
async function boot() {
  injectIcons();
  if (tg) {
    tg.ready?.();
    tg.expand?.();
    if (tg.setHeaderColor) tg.setHeaderColor("bg_color");
    if (tg.setBackgroundColor) tg.setBackgroundColor("bg_color");
  }
  
  bindEvents();
  
  await Promise.allSettled([
    loadMe(),
    loadTools(),
    loadBillingPlans(),
    loadHistory()
  ]);
}

document.addEventListener("DOMContentLoaded", boot);