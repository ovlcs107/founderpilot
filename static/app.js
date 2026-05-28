/**
 * FounderPilot AI - Frontend App (Vanilla JS)
 * Premium Minimal SaaS Edition - V2 (Stable Production)
 */

const tg = window.Telegram?.WebApp || null;
const OWNER_INN = "713304603876";
const OWNER_DISPLAY_NAME = "FounderPilot";

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
  btc: '<path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path><path d="M10 8h2.5a1.5 1.5 0 0 1 0 3H10V8z"></path><path d="M10 13h3a1.5 1.5 0 0 1 0 3h-3v-3z"></path><path d="M12 5v2"></path><path d="M12 17v2"></path>'
};

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
    {
      id: "role", title: "Чем вы занимаетесь?", type: "choices", options: [
        { key: "wb_seller", label: "Селлер WB/Ozon" },
        { key: "entrepreneur", label: "Предприниматель" },
        { key: "marketer", label: "Маркетолог" },
        { key: "beginner", label: "Новичок" },
        { key: "other", label: "Другое" }
      ]
    },
    {
      id: "pain", title: "Что хотите улучшить?", type: "choices", options: [
        { key: "sales", label: "Продажи" },
        { key: "cards", label: "Карточки товара" },
        { key: "ads", label: "Рекламу" },
        { key: "ideas", label: "Идеи товара" },
        { key: "strategy", label: "Стратегию" },
        { key: "unit", label: "Расчёты" }
      ]
    },
    { id: "desc", title: "Коротко опишите бизнес", type: "textarea", placeholder: "Например: продаю автотовары на WB, хочу поднять маржу" }
  ]
};

Object.assign(state, {
  projects: [],
  activeProject: null,
  memory: [],
  templates: [],
  creditPacks: [],
  notificationPrefs: {},
  analytics: null,
  toolSearch: "",
  historySearch: ""
});

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
      el.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${iconPaths[name]}</svg>`;
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
    inn: root.inn || OWNER_INN,
    company_name: root.company_name || root.company || OWNER_DISPLAY_NAME,
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
    { id: "margin", title: "Анализ идеи", description: "Оценка идеи по рынку, трендам и потенциалу.", prompt_template: "Проверь коммерческий потенциал следующей бизнес-идеи: ", icon: "calculator" },
    { id: "market", title: "Проверка рынка", description: "Исследование спроса, конкурентов и аудитории.", prompt_template: "Проведи экспресс-анализ спроса и целевой аудитории для: ", icon: "search" },
    { id: "competitors", title: "Анализ конкурентов", description: "Глубокий анализ стратегий и сильных сторон.", prompt_template: "Выяви сильные и уязвимые стороны ключевых конкурентов в нише: ", icon: "target" },
    { id: "mvp", title: "Генератор MVP", description: "Формирование концепции и плана MVP.", prompt_template: "Составь пошаговый план реализации минимально жизнеспособного продукта (MVP) для: ", icon: "edit" },
    { id: "finance", title: "Финмодель", description: "Финансовая модель и сценарии роста.", prompt_template: "Помоги составить базовую структуру финансовой модели для проекта: ", icon: "chart" },
    { id: "marketing", title: "Маркетинговая стратегия", description: "Стратегия выхода на рынок и каналы роста.", prompt_template: "Разработай go-to-market стратегию привлечения трафика для: ", icon: "message" }
  ];
}

function getPlanProviders(plan) {
  if (Array.isArray(plan?.providers) && plan.providers.length) return plan.providers;
  if (Array.isArray(state.providers) && state.providers.length) return state.providers;
  return [
    { id: "telegram_stars", title: "Telegram Stars", description: "Мгновенное списание средств" },
    { id: "yookassa", title: "Банковская карта / СБП", description: "Официальный эквайринг РФ" },
    { id: "ton", title: "TON Network", description: "Криптовалютный протокол" }
  ];
}

function updateSendButton() {
  const input = $("homeChatInput");
  const btn = $("homeChatSendBtn");
  if (input && btn) btn.disabled = !input.value.trim() || state.isSending;
}

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
    if (!limit) return "Безлимитно";
    const remain = Math.max(0, limit - used);
    return `${remain} / ${limit}`;
  };

  const calcPct = (used, limit) => limit ? Math.min(100, (used / limit) * 100) : 0;

  const tTxt = format(u.daily_used, u.daily_limit);
  const tPct = calcPct(u.daily_used, u.daily_limit);
  const mTxt = format(u.monthly_used, u.monthly_limit);
  const mPct = calcPct(u.monthly_used, u.monthly_limit);

  if ($("creditsTodayText")) $("creditsTodayText").textContent = `${tTxt}`;
  if ($("creditsTodayFill")) $("creditsTodayFill").style.width = `${tPct}%`;

  if ($("creditsMonthText")) $("creditsMonthText").textContent = `Лимит на месяц: ${mTxt}`;
  if ($("creditsMonthFill")) $("creditsMonthFill").style.width = `${mPct}%`;

  if ($("profileCreditsTodayText")) $("profileCreditsTodayText").textContent = tTxt;
  if ($("profileCreditsTodayFill")) $("profileCreditsTodayFill").style.width = `${tPct}%`;

  if ($("profileCreditsMonthText")) $("profileCreditsMonthText").textContent = mTxt;
  if ($("profileCreditsMonthFill")) $("profileCreditsMonthFill").style.width = `${mPct}%`;
  
  if ($("desktopTopCreditsValue")) {
    const remaining = Math.max(0, u.daily_limit - u.daily_used);
    $("desktopTopCreditsValue").textContent = remaining.toLocaleString();
  }
}

function updateProfileUI() {
  if (!state.user) return;
  const u = state.user;
  const initial = u.first_name.charAt(0).toUpperCase() || "F";

  if ($("homeGreeting")) $("homeGreeting").textContent = `Добро пожаловать, ${u.first_name} 👋`;
  if ($("headerUserAvatar")) $("headerUserAvatar").textContent = initial;
  if ($("mobileHeaderAvatar")) $("mobileHeaderAvatar").textContent = initial;
  if ($("profileUserAvatar")) $("profileUserAvatar").textContent = initial;
  if ($("profileUserTitle")) $("profileUserTitle").textContent = u.first_name;
  if ($("profileUserSubtitle")) $("profileUserSubtitle").textContent = u.username ? `@${u.username}` : `ID: ${u.telegram_id}`;
  if ($("profilePlanLabel")) $("profilePlanLabel").textContent = String(u.plan).toUpperCase();
  if ($("profileBusinessDescription")) $("profileBusinessDescription").value = u.business_profile;
  if ($("profileInn")) $("profileInn").value = u.inn || OWNER_INN;
  if ($("profileCompanyName")) $("profileCompanyName").value = u.company_name || OWNER_DISPLAY_NAME;
  syncLegalBadges();

  updateCreditsUI();
}

function getLegalInn() {
  return state.user?.inn || OWNER_INN;
}

function syncLegalBadges() {
  const inn = getLegalInn();
  document.querySelectorAll("[data-legal-inn]").forEach(el => {
    el.textContent = `ИНН ${inn}`;
  });
  document.querySelectorAll("[data-owner-name]").forEach(el => {
    el.textContent = state.user?.company_name || OWNER_DISPLAY_NAME;
  });
  if ($("profileInn") && !$('profileInn').value) $('profileInn').value = inn;
  if ($("profileCompanyName") && !$('profileCompanyName').value) $('profileCompanyName').value = state.user?.company_name || OWNER_DISPLAY_NAME;
}

function normalizeArrayPayload(data, keys = []) {
  if (Array.isArray(data)) return data;
  for (const key of keys) {
    if (Array.isArray(data?.[key])) return data[key];
  }
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

function normalizeObjectPayload(data, key) {
  if (data?.[key] && typeof data[key] === "object") return data[key];
  if (data && typeof data === "object") return data;
  return {};
}

function openExternal(url) {
  if (!url) return;
  if (tg?.openLink) tg.openLink(url);
  else window.open(url, "_blank", "noopener,noreferrer");
}

function copyText(text, msg = "Скопировано") {
  const value = String(text || "");
  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(value).then(() => showToast(msg)).catch(() => showToast("Не удалось скопировать"));
    return;
  }
  const ta = document.createElement("textarea");
  ta.value = value;
  ta.style.position = "fixed";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.select();
  try { document.execCommand("copy"); showToast(msg); }
  catch { showToast("Не удалось скопировать"); }
  finally { ta.remove(); }
}

function getFallbackProjects() {
  return [
    { id: "main", title: "Основной бизнес", niche: "Маркетплейсы / услуги", goal: "Рост продаж и контроль маржи" }
  ];
}

function getFallbackTemplates() {
  return [
    { id: "unit", title: "Юнит-экономика", prompt: "Посчитай маржу, чистую прибыль, ROI и точку безубыточности. Данные: " },
    { id: "offer", title: "Оффер", prompt: "Сделай 5 сильных офферов для продукта с разными болями ЦА. Продукт: " }
  ];
}

function getFallbackCreditPacks() {
  return [
    { id: "starter", title: "1 000 кредитов", description: "Для разовых задач", price_text: "149 ₽" },
    { id: "growth", title: "5 000 кредитов", description: "Для активной работы", price_text: "499 ₽" },
    { id: "scale", title: "20 000 кредитов", description: "Для плотного использования", price_text: "1 490 ₽" }
  ];
}

function renderProjects() {
  const list = $("projectList");
  if (!list) return;
  const projects = state.projects.length ? state.projects : getFallbackProjects();
  const activeId = state.activeProject?.id || projects[0]?.id;
  list.innerHTML = projects.map(p => `
    <button type="button" class="workspace-row ${String(p.id) === String(activeId) ? 'active' : ''}" data-project-id="${escapeHTML(p.id || p.key || '')}">
      <span class="row-dot"></span>
      <span class="workspace-row-main">
        <strong>${escapeHTML(p.title || p.name || 'Проект')}</strong>
        <small>${escapeHTML(p.niche || p.description || p.goal || 'Контекст для AI')}</small>
      </span>
    </button>
  `).join("");
}

function renderMemory() {
  const list = $("memoryList");
  if (!list) return;
  if (!state.memory.length) {
    list.innerHTML = `<div class="subtle-empty">Память пока пустая. Добавьте факт о бизнесе — AI будет учитывать его в ответах.</div>`;
    return;
  }
  list.innerHTML = state.memory.map(item => {
    const text = item.text || item.content || item.memory || item.value || "";
    return `<div class="memory-chip"><span>${escapeHTML(text)}</span></div>`;
  }).join("");
}

function renderTemplates() {
  const list = $("templateList");
  if (!list) return;
  const templates = state.templates.length ? state.templates : getFallbackTemplates();
  list.innerHTML = templates.map(t => `
    <button type="button" class="template-row" data-template-prompt="${escapeHTML(t.prompt || t.content || t.text || '')}">
      <span data-icon="edit"></span>
      <span><strong>${escapeHTML(t.title || t.name || 'Шаблон')}</strong><small>${escapeHTML((t.prompt || t.content || t.text || '').slice(0, 74))}</small></span>
    </button>
  `).join("");
  injectIcons(list);
}

function renderCreditPacks() {
  const list = $("creditPackList");
  if (!list) return;
  const packs = state.creditPacks.length ? state.creditPacks : getFallbackCreditPacks();
  list.innerHTML = packs.map(p => `
    <button type="button" class="pack-row" data-pack-id="${escapeHTML(p.id || p.key || '')}">
      <span><strong>${escapeHTML(p.title || p.name || 'Пакет кредитов')}</strong><small>${escapeHTML(p.description || '')}</small></span>
      <b>${escapeHTML(p.price_text || p.price_formatted || p.price || '')}</b>
    </button>
  `).join("");
}

function renderNotifications() {
  const prefs = state.notificationPrefs || {};
  const set = (id, val) => { const el = $(id); if (el) el.checked = Boolean(val); };
  set("notifyLimitToggle", prefs.limit_alerts ?? true);
  set("notifyBillingToggle", prefs.billing_alerts ?? true);
  set("notifyProductToggle", prefs.product_news ?? false);
}

function renderAnalytics() {
  const box = $("analyticsMini");
  if (!box) return;
  const a = state.analytics || {};
  const users = a.users_total ?? a.total_users ?? "—";
  const paid = a.paid_users ?? a.subscribers ?? "—";
  const requests = a.requests_today ?? a.today_requests ?? "—";
  box.innerHTML = `
    <div><span>Пользователи</span><strong>${escapeHTML(users)}</strong></div>
    <div><span>Оплатившие</span><strong>${escapeHTML(paid)}</strong></div>
    <div><span>Запросы сегодня</span><strong>${escapeHTML(requests)}</strong></div>
  `;
}

function renderTools() {
  const grid = $("toolsGrid");
  if (!grid) return;
  const q = String(state.toolSearch || "").trim().toLowerCase();
  const items = (state.tools.length ? state.tools : getFallbackTools()).filter(t => {
    if (!q) return true;
    return [t.title, t.name, t.description, t.subtitle].filter(Boolean).join(" ").toLowerCase().includes(q);
  });
  if (!items.length) {
    grid.innerHTML = `<div class="loading-state">Ничего не найдено. Попробуйте другой запрос.</div>`;
    return;
  }
  grid.innerHTML = items.map(t => {
    return `
      <div class="tool-card" data-prompt="${escapeHTML(t.prompt_template || t.prompt || '')}">
        <div class="tool-info">
          <h4>${escapeHTML(t.title || t.name || 'Ассистент')}</h4>
          <p>${escapeHTML(t.description || t.subtitle || '')}</p>
        </div>
        <div class="tool-fit-text-cell">
          <span>Развитие продукта</span>
        </div>
      </div>
    `;
  }).join("");
  injectIcons(grid);
}

async function loadProjects() {
  try {
    const data = await apiRequest("/api/projects");
    state.projects = normalizeArrayPayload(data, ["projects"]);
    state.activeProject = data?.active_project || data?.current_project || state.projects[0] || null;
  } catch {
    state.projects = getFallbackProjects();
    state.activeProject = state.projects[0];
  }
  renderProjects();
}

async function loadMemory() {
  try {
    const data = await apiRequest("/api/memory");
    state.memory = normalizeArrayPayload(data, ["memory", "items"]);
  } catch {
    state.memory = [];
  }
  renderMemory();
}

async function loadTemplates() {
  try {
    const data = await apiRequest("/api/templates");
    state.templates = normalizeArrayPayload(data, ["templates"]);
  } catch {
    state.templates = getFallbackTemplates();
  }
  renderTemplates();
}

async function loadCreditPacks() {
  try {
    const data = await apiRequest("/api/credits/packs");
    state.creditPacks = normalizeArrayPayload(data, ["packs", "credit_packs"]);
  } catch {
    state.creditPacks = getFallbackCreditPacks();
  }
  renderCreditPacks();
}

async function loadNotificationPrefs() {
  try {
    const data = await apiRequest("/api/notifications/preferences");
    state.notificationPrefs = normalizeObjectPayload(data, "preferences");
  } catch {
    state.notificationPrefs = { limit_alerts: true, billing_alerts: true, product_news: false };
  }
  renderNotifications();
}

async function loadAnalyticsSummary() {
  try {
    const data = await apiRequest("/api/analytics/summary");
    state.analytics = data?.summary || data;
  } catch {
    state.analytics = null;
  }
  renderAnalytics();
}

async function saveWorkspaceProject() {
  const title = $("projectTitleInput")?.value.trim() || "Основной бизнес";
  const niche = $("projectNicheInput")?.value.trim() || "";
  const goal = $("projectGoalInput")?.value.trim() || "";
  try {
    const payload = { title, name: title, niche, goal, telegram_user_id: getTelegramUserId() };
    const data = await apiRequest("/api/projects", { method: "POST", body: JSON.stringify(payload) });
    const project = data?.project || data;
    state.activeProject = project;
    await loadProjects();
    showToast("Проект сохранён");
  } catch {
    const project = { id: `local_${Date.now()}`, title, niche, goal };
    state.projects.unshift(project);
    state.activeProject = project;
    renderProjects();
    showToast("Проект сохранён локально");
  }
}

async function addMemoryItem() {
  const input = $("memoryInput");
  const text = input?.value.trim();
  if (!text) return;
  try {
    const payload = { text, content: text, telegram_user_id: getTelegramUserId(), project_id: state.activeProject?.id };
    const data = await apiRequest("/api/memory", { method: "POST", body: JSON.stringify(payload) });
    state.memory.unshift(data?.item || data?.memory || { text });
    input.value = "";
    renderMemory();
    showToast("Факт добавлен в память");
  } catch {
    state.memory.unshift({ text });
    input.value = "";
    renderMemory();
    showToast("Факт добавлен локально");
  }
}

async function saveTemplateItem() {
  const title = $("templateTitleInput")?.value.trim();
  const prompt = $("templatePromptInput")?.value.trim();
  if (!title || !prompt) { showToast("Заполните название и текст шаблона"); return; }
  try {
    const data = await apiRequest("/api/templates", { method: "POST", body: JSON.stringify({ title, prompt, content: prompt, telegram_user_id: getTelegramUserId() }) });
    state.templates.unshift(data?.template || { title, prompt });
    $("templateTitleInput").value = "";
    $("templatePromptInput").value = "";
    renderTemplates();
    showToast("Шаблон сохранён");
  } catch {
    state.templates.unshift({ id: `local_${Date.now()}`, title, prompt });
    $("templateTitleInput").value = "";
    $("templatePromptInput").value = "";
    renderTemplates();
    showToast("Шаблон сохранён локально");
  }
}

async function buyCreditPack(packId) {
  if (!packId) return;
  showToast("Создание заказа...");
  try {
    const res = await apiRequest("/api/credits/packs/order", { method: "POST", body: JSON.stringify({ pack_id: packId, telegram_user_id: getTelegramUserId() }) });
    const link = res.payment_url || res.invoice_url || res.invoice_link || res.url;
    const orderId = res.order_id || res.id;
    if (link) {
      openExternal(link);
      if (orderId) pollOrderStatus(orderId);
      return;
    }
    if (res.ok || res.success) { showToast("Кредиты начислены"); loadMe(); }
  } catch (err) {
    showToast(err.message || "Не удалось создать заказ");
  }
}

async function saveNotificationPrefs() {
  const prefs = {
    limit_alerts: Boolean($("notifyLimitToggle")?.checked),
    billing_alerts: Boolean($("notifyBillingToggle")?.checked),
    product_news: Boolean($("notifyProductToggle")?.checked)
  };
  try {
    await apiRequest("/api/notifications/preferences", { method: "POST", body: JSON.stringify(prefs) });
    state.notificationPrefs = prefs;
    showToast("Уведомления обновлены");
  } catch {
    state.notificationPrefs = prefs;
    showToast("Настройки сохранены локально");
  }
}

function exportHistory() {
  openExternal("/api/export/history.txt");
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
  renderTools();
}

async function loadHistory() {
  const list = $("historyList");
  try {
    const data = await apiRequest("/api/history");
    const arr = normalizeHistoryResponse(data);
    state.history = arr;
    renderHistory();
  } catch {
    if (list) list.innerHTML = `<div class="loading-state">Не удалось загрузить историю.</div>`;
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

  const hq = String(state.historySearch || "").trim().toLowerCase();
  if (hq) {
    filtered = filtered.filter(h => [h.title, h.prompt, h.text, h.answer, h.content, h.result].filter(Boolean).join(" ").toLowerCase().includes(hq));
  }

  if (!filtered.length) {
    list.innerHTML = `
      <div class="loading-state" style="border:none;">
        <h3>Архив пуст</h3>
        <p class="muted">Записи сессий отсутствуют в данном фильтре.</p>
      </div>`;
    return;
  }

  list.innerHTML = filtered.map(h => {
    const type = String(h.mode || h.type || "chat").toUpperCase();
    const title = h.title || h.prompt || h.text || "Запрос";
    const dateStr = h.created_at || "24.05.2024";
    const project = h.project_name || "Основной";
    return `
      <div class="history-item">
        <h4>${escapeHTML(title)}</h4>
        <div>${escapeHTML(type)}</div>
        <div>${escapeHTML(project)}</div>
        <div>${escapeHTML(dateStr)}</div>
        <div class="item-meta">
          <span class="badge">Завершён</span>
        </div>
      </div>
    `;
  }).join("");
}

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
  m.classList.add("active");

  const list = $("billingPlanList");
  const pBox = $("paymentProviderBox");
  list.hidden = false;
  pBox.hidden = true;
  $("billingTitle").textContent = "Выбор тарифа";

  const keys = Object.keys(state.plans || {});
  if (!keys.length) {
    list.innerHTML = `<div class="loading-state">Тарифы временно недоступны.</div>`;
    return;
  }

  list.innerHTML = keys.map(k => {
    const p = state.plans[k];
    const isCurrent = state.user && String(state.user.plan).toLowerCase() === k.toLowerCase();
    const price = p.price_text || (p.price_monthly ? `${p.price_monthly} ₽` : "Бесплатно");
    return `
      <button class="plan-card ${isCurrent ? 'active' : ''}" data-plan="${escapeHTML(k)}" type="button">
        <div class="plan-info">
          <h4>${escapeHTML(p.title || k)}</h4>
          <small>${escapeHTML(p.description || '')}</small>
        </div>
        <div class="plan-cost">${escapeHTML(price)}</div>
      </button>
    `;
  }).join("");
}

function selectPlan(key) {
  if (key === "free") {
    showToast("Тариф Free активен по умолчанию");
    return;
  }

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
      <button class="provider-btn" data-provider="${escapeHTML(id)}" type="button">
        <span class="provider-icon" data-icon="${icon}"></span>
        <div class="provider-desc">
          <strong>${escapeHTML(pr.title || pr.name || id)}</strong>
          <small>${escapeHTML(pr.description || '')}</small>
        </div>
        ${pr.price_formatted ? `<div class="plan-cost">${escapeHTML(pr.price_formatted)}</div>` : ""}
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
        if (status === "paid") { showToast("Оплата прошла"); loadMe(); $("billingModal").classList.remove("active"); }
        else if (status === "cancelled") showToast("Оплата отменена");
      });
      return;
    }

    if (link) {
      if (tg?.openLink) tg.openLink(link);
      else window.open(link, "_blank");
      if (orderId) pollOrderStatus(orderId);
      $("billingModal").classList.remove("active");
      return;
    }

    if (res.ok || res.success) {
      showToast("Успешно");
      loadMe();
      $("billingModal").classList.remove("active");
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

// ONBOARDING ENGINE
function openOnboarding() {
  state.onboardingStep = 0;
  state.onboardingData = {};
  const m = $("onboardingModal");
  if (m) {
    m.classList.add("active");
    renderOnboardingStep();
  }
}

function renderOnboardingStep() {
  const cfg = state.onboardingConfig[state.onboardingStep];
  if (!cfg) return;

  $("onboardingTitle").textContent = cfg.title;
  $("onboardingError").hidden = true;
  $("onboardingError").style.display = "none";

  const dots = $("onboardingProgressRow")?.querySelectorAll(".dot");
  if (dots) {
    dots.forEach((d, i) => d.classList.toggle("active", i <= state.onboardingStep));
  }

  const body = $("onboardingBody");
  if (!body) return;
  body.innerHTML = "";

  if (cfg.type === "textarea") {
    const ta = document.createElement("textarea");
    ta.className = "ref-form-textarea";
    ta.rows = 4;
    ta.placeholder = cfg.placeholder || "";
    ta.value = state.onboardingData[cfg.id] || "";
    ta.oninput = () => { state.onboardingData[cfg.id] = ta.value; };
    body.appendChild(ta);
  } else {
    if (Array.isArray(cfg.options)) {
      cfg.options.forEach(o => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = `choice-btn ${state.onboardingData[cfg.id] === o.key ? 'active' : ''}`;
        b.textContent = o.label;
        b.onclick = () => {
          state.onboardingData[cfg.id] = o.key;
          renderOnboardingStep();
        };
        body.appendChild(b);
      });
    }
  }

  if ($("onboardingBackBtn")) {
    $("onboardingBackBtn").disabled = state.onboardingStep === 0;
  }
  if ($("onboardingNextBtn")) {
    $("onboardingNextBtn").textContent = state.onboardingStep === state.onboardingConfig.length - 1 ? "Завершить" : "Продолжить";
  }
}

async function nextOnboarding() {
  const cfg = state.onboardingConfig[state.onboardingStep];
  const val = state.onboardingData[cfg.id];

  if (!val || !String(val).trim()) {
    $("onboardingError").textContent = "Пожалуйста, заполните это поле.";
    $("onboardingError").hidden = false;
    $("onboardingError").style.display = "block";
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
    $("onboardingModal").classList.remove("active");
    showToast("Профиль настроен");
    loadMe();
  } catch {
    $("onboardingModal").classList.remove("active");
    showToast("Профиль зафиксирован локально.");
  } finally {
    $("onboardingNextBtn").disabled = false;
  }
}

function bindEvents() {
  document.querySelectorAll(".nav-item").forEach(b => {
    b.addEventListener("click", () => switchView(b.dataset.target));
  });
  $("headerProfileBtn")?.addEventListener("click", () => switchView("profile"));

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

  $("quickStrip")?.addEventListener("click", e => {
    const b = e.target.closest(".quick-pill");
    if (b && chatInput) { chatInput.value = b.dataset.prompt; chatInput.focus(); autoResizeTextarea(chatInput); updateSendButton(); }
  });

  document.querySelectorAll(".sidebar-link-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      switchView("home");
      if (chatInput) { chatInput.value = btn.dataset.prompt; chatInput.focus(); autoResizeTextarea(chatInput); updateSendButton(); }
    });
  });

  $("toolsGrid")?.addEventListener("click", e => {
    const r = e.target.closest(".tool-card");
    if (r) { switchView("home"); if (chatInput) { chatInput.value = r.dataset.prompt; chatInput.focus(); autoResizeTextarea(chatInput); updateSendButton(); } }
  });

  $("historyFilters")?.addEventListener("click", e => {
    const b = e.target.closest(".chip");
    if (!b) return;
    $("historyFilters").querySelectorAll(".chip").forEach(n => n.classList.remove("active"));
    b.classList.add("active");
    state.historyFilter = b.dataset.filter;
    renderHistory();
  });

  $("saveProfileBtn")?.addEventListener("click", async () => {
    const text = $("profileBusinessDescription")?.value.trim();
    const inn = $("profileInn")?.value.trim();
    const companyName = $("profileCompanyName")?.value.trim();
    try {
      await apiTry("/api/profile/save", "/api/business-profile", { 
        method: "POST", 
        body: JSON.stringify({ 
          telegram_user_id: getTelegramUserId(), 
          business_profile: text, 
          description: text,
          inn: inn,
          company_name: companyName
        }) 
      });
      if (state.user) {
        state.user.business_profile = text;
        state.user.inn = inn;
        state.user.company_name = companyName;
      }
      showToast("Контекст и реквизиты сохранены");
    } catch (err) { showToast(err.message); }
  });

  $("submitAppFeedbackBtn")?.addEventListener("click", async () => {
    const text = $("appFeedbackText")?.value.trim();
    if (!text) return;
    try {
      apiRequest("/api/feedback", { method: "POST", body: JSON.stringify({ telegram_user_id: getTelegramUserId(), message: text, type: "app" }) });
      $("appFeedbackText").value = "";
      showToast("Спасибо за отзыв");
    } catch (err) { showToast(err.message); }
  });

  $("openBillingBtn")?.addEventListener("click", openBillingModal);
  $("closeBillingBtn")?.addEventListener("click", () => $("billingModal").classList.remove("active"));
  $("backToPlansBtn")?.addEventListener("click", () => { $("paymentProviderBox").hidden = true; $("billingPlanList").hidden = false; $("billingTitle").textContent = "Выбор тарифа"; });

  $("billingPlanList")?.addEventListener("click", e => {
    const b = e.target.closest(".plan-card");
    if (b) selectPlan(b.dataset.plan);
  });
  $("providerList")?.addEventListener("click", e => {
    const b = e.target.closest(".provider-btn");
    if (b) checkout(b.dataset.provider);
  });

  $("toolsSearchInput")?.addEventListener("input", e => {
    state.toolSearch = e.target.value || "";
    renderTools();
  });

  $("historySearchInput")?.addEventListener("input", e => {
    state.historySearch = e.target.value || "";
    renderHistory();
  });
  $("exportHistoryBtn")?.addEventListener("click", exportHistory);

  document.querySelectorAll("[data-copy-inn]").forEach(btn => {
    btn.addEventListener("click", () => copyText(getLegalInn(), "ИНН скопирован"));
  });

  $("saveWorkspaceBtn")?.addEventListener("click", saveWorkspaceProject);
  $("projectList")?.addEventListener("click", e => {
    const row = e.target.closest(".workspace-row");
    if (!row) return;
    state.activeProject = state.projects.find(p => String(p.id) === String(row.dataset.projectId)) || state.activeProject;
    renderProjects();
    showToast("Активный проект выбран");
  });
  $("addMemoryBtn")?.addEventListener("click", addMemoryItem);
  $("memoryInput")?.addEventListener("keydown", e => {
    if (e.key === "Enter") { e.preventDefault(); addMemoryItem(); }
  });
  $("saveTemplateBtn")?.addEventListener("click", saveTemplateItem);
  $("templateList")?.addEventListener("click", e => {
    const row = e.target.closest(".template-row");
    if (!row || !chatInput) return;
    switchView("home");
    chatInput.value = row.dataset.templatePrompt || "";
    chatInput.focus();
    autoResizeTextarea(chatInput);
    updateSendButton();
  });
  $("creditPackList")?.addEventListener("click", e => {
    const row = e.target.closest(".pack-row");
    if (row) buyCreditPack(row.dataset.packId);
  });
  $("saveNotificationsBtn")?.addEventListener("click", saveNotificationPrefs);

  $("onboardingBackBtn")?.addEventListener("click", () => { if (state.onboardingStep > 0) { state.onboardingStep--; renderOnboardingStep(); } });
  $("onboardingNextBtn")?.addEventListener("click", nextOnboarding);
}

async function boot() {
  injectIcons();
  if (tg) {
    tg.ready?.();
    tg.expand?.();
    if (tg.setHeaderColor) tg.setHeaderColor("bg_color");
    if (tg.setBackgroundColor) tg.setBackgroundColor("bg_color");
  }

  bindEvents();
  syncLegalBadges();

  await Promise.allSettled([
    loadMe(),
    loadTools(),
    loadBillingPlans(),
    loadHistory(),
    loadProjects(),
    loadMemory(),
    loadTemplates(),
    loadCreditPacks(),
    loadNotificationPrefs(),
    loadAnalyticsSummary()
  ]);
}

document.addEventListener("DOMContentLoaded", boot);