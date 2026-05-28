const tg = window.Telegram?.WebApp || null;

const iconPaths = {
  home: '<path d="m3 10.5 9-7 9 7"/><path d="M5 10v10h5v-6h4v6h5V10"/>',
  chat: '<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7A8.4 8.4 0 0 1 4 11.5a8.5 8.5 0 0 1 17 0Z"/>',
  tools: '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
  history: '<path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/><path d="M12 7v5l3 2"/>',
  user: '<path d="M20 21a8 8 0 0 0-16 0"/><circle cx="12" cy="7" r="4"/>',
  send: '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
  copy: '<rect x="9" y="9" width="13" height="13" rx="2"/><rect x="2" y="2" width="13" height="13" rx="2"/>',
  save: '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2Z"/><path d="M17 21v-8H7v8"/><path d="M7 3v5h8"/>',
  trash: '<path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v5"/><path d="M14 11v5"/>',
  edit: '<path d="M12 20h9"/><path d="m16.5 3.5 4 4L8 20H4v-4Z"/>',
  plus: '<path d="M12 5v14"/><path d="M5 12h14"/>',
  back: '<path d="m15 18-6-6 6-6"/><path d="M21 12H9"/>',
  check: '<path d="m20 6-11 11-5-5"/>',
  close: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  warning: '<path d="m12 3 10 18H2Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
  thumbsUp: '<path d="M7 10v11"/><path d="M15 5.5 14 10h5.4a2 2 0 0 1 2 2.3l-1.2 7A2 2 0 0 1 18.3 21H7a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h2.8L12 5.5A2 2 0 0 1 15 5.5Z"/>',
  thumbsDown: '<path d="M7 14V3"/><path d="M15 18.5 14 14h5.4a2 2 0 0 0 2-2.3l-1.2-7A2 2 0 0 0 18.3 3H7a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h2.8l2.2 4.5a2 2 0 0 0 3 0Z"/>',
  link: '<path d="M10 13a5 5 0 0 0 7.1 0l2-2a5 5 0 0 0-7.1-7.1l-1.1 1.1"/><path d="M14 11a5 5 0 0 0-7.1 0l-2 2A5 5 0 0 0 12 20.1l1.1-1.1"/>',
  chart: '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-7"/>',
  product: '<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M7 8h10"/><path d="M7 12h6"/><path d="M7 16h4"/>',
  card: '<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M7 8h10"/><path d="M7 12h6"/><path d="M7 16h4"/>',
  calculator: '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M8 6h8"/><path d="M8 10h.01"/><path d="M12 10h.01"/><path d="M16 10h.01"/><path d="M8 14h.01"/><path d="M12 14h.01"/><path d="M16 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/><path d="M16 18h.01"/>',
  target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
  content: '<path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/>',
  list: '<path d="M8 6h13"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M3 6h.01"/><path d="M3 12h.01"/><path d="M3 18h.01"/>',
  trending: '<path d="m22 7-8.5 8.5-5-5L2 17"/><path d="M16 7h6v6"/>',
  settings: '<path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6V22a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1A2 2 0 1 1 4.2 18l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.6-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1A2 2 0 1 1 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3h.1a1.7 1.7 0 0 0 .9-1.6V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1A2 2 0 1 1 19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9v.1a1.7 1.7 0 0 0 1.6.9h.1a2 2 0 1 1 0 4H21a1.7 1.7 0 0 0-1.6 1Z"/>',
};

function icon(name) {
  const path = iconPaths[name] || iconPaths.tools;
  return `<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${path}</svg>`;
}

function injectIcons(root = document) {
  root.querySelectorAll("[data-icon]").forEach((node) => {
    node.innerHTML = icon(node.dataset.icon);
  });
}

const fallbackTools = [
  {
    id: "wb_ozon_card",
    title: "WB/Ozon карточка товара",
    description: "SEO-название, описание, буллеты, ключи, фото и инфографика.",
    icon: "product",
    fields: [
      { key: "product", label: "Товар", placeholder: "Например: органайзер для кухни", required: "true" },
      { key: "price", label: "Цена", placeholder: "Например: 1290 руб.", required: "true", inputmode: "decimal" },
      { key: "target_audience", label: "Целевая аудитория", placeholder: "Кто покупает и зачем", type: "textarea", required: "true" },
      { key: "advantages", label: "Преимущества", placeholder: "Что у товара сильного", type: "textarea", required: "true" },
      { key: "disadvantages", label: "Недостатки", placeholder: "Что может мешать продаже", type: "textarea", required: "false" },
      { key: "competitors", label: "Конкуренты", placeholder: "Названия, ссылки или описание", type: "textarea", required: "false" },
    ],
  },
  {
    id: "margin_calc",
    title: "Расчет маржи",
    description: "Прибыль, маржа, ROI, безубыточность и рекомендации по цене.",
    icon: "calculator",
    fields: [
      { key: "purchase_price", label: "Закупочная цена", placeholder: "Например: 430", type: "number", required: "true", inputmode: "decimal" },
      { key: "sale_price", label: "Цена продажи", placeholder: "Например: 990", type: "number", required: "true", inputmode: "decimal" },
      { key: "commission", label: "Комиссия", placeholder: "Например: 18% или 180", required: "true", inputmode: "decimal" },
      { key: "logistics", label: "Логистика", placeholder: "Например: 95", type: "number", required: "true", inputmode: "decimal" },
      { key: "packaging", label: "Упаковка", placeholder: "Например: 25", type: "number", required: "false", inputmode: "decimal" },
      { key: "ads", label: "Реклама", placeholder: "Например: 120", type: "number", required: "false", inputmode: "decimal" },
      { key: "taxes_other", label: "Налоги/прочее", placeholder: "Например: 6% или 50", required: "false", inputmode: "decimal" },
    ],
  },
  { id: "product_idea", title: "Идея товара", description: "5 идей товаров с рисками, конкуренцией и оффером.", icon: "target", fields: [] },
  { id: "product_description", title: "Описание товара", description: "Продающее описание, преимущества, SEO-ключи и заголовки.", icon: "content", fields: [] },
  { id: "ad_offer", title: "Реклама и оффер", description: "Оффер, заголовки, объявления, боли ЦА и триггеры.", icon: "chart", fields: [] },
  { id: "review_reply", title: "Ответ на отзыв", description: "Ответы на отзывы покупателей и выводы по товару.", icon: "chat", fields: [] },
  { id: "competitor_analysis", title: "Анализ конкурента", description: "Сильные и слабые стороны, отстройка и идеи карточки.", icon: "search", fields: [] },
  { id: "swot", title: "SWOT-анализ", description: "Сильные стороны, слабости, возможности и угрозы.", icon: "check", fields: [] },
  { id: "content_plan", title: "Контент-план", description: "7 постов, Reels/Shorts, CTA и темы для прогрева.", icon: "list", fields: [] },
  { id: "sales_plan", title: "План продаж", description: "14 дней действий, метрики и гипотезы роста.", icon: "trending", fields: [] },
  { id: "business_idea", title: "Проверка бизнес-идеи", description: "Плюсы, минусы, монетизация и проверка за 7 дней.", icon: "settings", fields: [] },
];

const quickActions = [
  { toolId: "margin_calc", label: "Посчитать маржу", icon: "calculator" },
  { toolId: "wb_ozon_card", label: "Улучшить карточку товара", icon: "product" },
  { toolId: "ad_offer", label: "Сделать оффер", icon: "chart" },
  { toolId: "competitor_analysis", label: "Разобрать конкурента", icon: "search" },
];

const promptSuggestions = [
  "Посчитай маржу",
  "Улучши карточку",
  "Сделай оффер",
  "Разбери конкурента",
  "Почему нет продаж?",
];

const improveActions = [
  "Сделай короче",
  "Сделай подробнее",
  "Добавь примеры",
  "Сделай продающе",
];

const state = {
  tools: fallbackTools,
  currentView: "home",
  previousView: "home",
  currentTool: null,
  currentToolRunId: null,
  currentResult: "",
  chatConversationId: null,
  chatMessages: [],
  chatLoading: false,
  me: null,
  profile: null,
  usage: null,
  saved: [],
  history: { conversations: [], tool_runs: [], saved: [], items: [] },
  historyFilter: "all",
  onboarding: { step: 0, user_type: "", main_goal: "", description: "" },
};

const $ = (id) => document.getElementById(id);

const els = {
  pageTitle: $("pageTitle"),
  userAvatar: $("userAvatar"),
  profileAvatar: $("profileAvatar"),
  profileTitle: $("profileTitle"),
  profileUsername: $("profileUsername"),
  homeGreeting: $("homeGreeting"),
  quickActions: $("quickActions"),
  homeHistory: $("homeHistory"),
  toolsGrid: $("toolsGrid"),
  toolForm: $("toolForm"),
  toolIcon: $("toolIcon"),
  toolTitle: $("toolTitle"),
  toolDescription: $("toolDescription"),
  toolFields: $("toolFields"),
  toolInput: $("toolInput"),
  toolError: $("toolError"),
  generateBtn: $("generateBtn"),
  toolResultCard: $("toolResultCard"),
  toolResultStatus: $("toolResultStatus"),
  toolResultContent: $("toolResultContent"),
  toolResultActions: $("toolResultActions"),
  toolFeedbackBox: $("toolFeedbackBox"),
  chatSubtitle: $("chatSubtitle"),
  chatEmpty: $("chatEmpty"),
  chatMessages: $("chatMessages"),
  chatInput: $("chatInput"),
  sendChatBtn: $("sendChatBtn"),
  chatError: $("chatError"),
  promptRow: $("promptRow"),
  historyList: $("historyList"),
  savedList: $("savedList"),
  detailModal: $("detailModal"),
  detailTitle: $("detailTitle"),
  detailContent: $("detailContent"),
  detailActions: $("detailActions"),
  onboardingModal: $("onboardingModal"),
  onboardingTitle: $("onboardingTitle"),
  onboardingBody: $("onboardingBody"),
  onboardingError: $("onboardingError"),
  onboardingBackBtn: $("onboardingBackBtn"),
  onboardingNextBtn: $("onboardingNextBtn"),
  toast: $("toast"),
};

function applyTelegramTheme() {
  if (!tg?.themeParams) return;
  const map = {
    bg_color: "--tg-theme-bg-color",
    text_color: "--tg-theme-text-color",
    hint_color: "--tg-theme-hint-color",
    link_color: "--tg-theme-link-color",
    button_color: "--tg-theme-button-color",
    button_text_color: "--tg-theme-button-text-color",
    secondary_bg_color: "--tg-theme-secondary-bg-color",
  };
  Object.entries(map).forEach(([key, cssVar]) => {
    if (tg.themeParams[key]) document.documentElement.style.setProperty(cssVar, tg.themeParams[key]);
  });
}

function initTelegram() {
  if (!tg) return;
  applyTelegramTheme();
  tg.ready();
  tg.expand();
  tg.onEvent?.("themeChanged", applyTelegramTheme);
  tg.BackButton?.onClick(() => {
    if (!els.detailModal.hidden) {
      closeDetail();
      return;
    }
    if (state.currentView === "tool") setView("tools");
    else setView("home");
  });
  tg.MainButton?.hide();
}

function haptic(kind = "selection") {
  if (!tg?.HapticFeedback) return;
  if (kind === "success" || kind === "error") tg.HapticFeedback.notificationOccurred(kind);
  else tg.HapticFeedback.selectionChanged();
}

function telegramUser() {
  return tg?.initDataUnsafe?.user || null;
}

function initData() {
  return tg?.initData || "";
}

function startParam() {
  return tg?.initDataUnsafe?.start_param || new URLSearchParams(window.location.search).get("start") || "";
}

function userDisplayName() {
  const user = telegramUser();
  const me = state.me?.user;
  const first = user?.first_name || me?.first_name || "";
  const last = user?.last_name || me?.last_name || "";
  const username = user?.username || me?.username || "";
  return [first, last].filter(Boolean).join(" ") || username || "предприниматель";
}

function initials(name) {
  return String(name || "FP")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase() || "FP";
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Telegram-Init-Data": initData(),
      ...(options.headers || {}),
    },
  });
  let data = null;
  try {
    data = await response.json();
  } catch (_) {
    data = null;
  }
  if (!response.ok) {
    throw new Error(data?.error || data?.detail || `HTTP ${response.status}`);
  }
  if (data?.ok === false) {
    throw new Error(data.error || "Запрос не выполнен");
  }
  return data;
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function inlineMarkdown(text) {
  return escapeHtml(text)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`(.+?)`/g, "<code>$1</code>");
}

function markdownToHtml(text) {
  const lines = String(text || "").split(/\r?\n/);
  const html = [];
  let listType = null;

  const closeList = () => {
    if (listType) {
      html.push(`</${listType}>`);
      listType = null;
    }
  };

  lines.forEach((line) => {
    const trimmed = line.trim();
    if (!trimmed) {
      closeList();
      return;
    }
    if (trimmed.startsWith("### ")) {
      closeList();
      html.push(`<h4>${inlineMarkdown(trimmed.slice(4))}</h4>`);
      return;
    }
    if (trimmed.startsWith("## ")) {
      closeList();
      html.push(`<h3>${inlineMarkdown(trimmed.slice(3))}</h3>`);
      return;
    }
    if (trimmed.startsWith("# ")) {
      closeList();
      html.push(`<h2>${inlineMarkdown(trimmed.slice(2))}</h2>`);
      return;
    }
    if (/^[-*]\s+/.test(trimmed)) {
      if (listType !== "ul") {
        closeList();
        listType = "ul";
        html.push("<ul>");
      }
      html.push(`<li>${inlineMarkdown(trimmed.replace(/^[-*]\s+/, ""))}</li>`);
      return;
    }
    if (/^\d+\.\s+/.test(trimmed)) {
      if (listType !== "ol") {
        closeList();
        listType = "ol";
        html.push("<ol>");
      }
      html.push(`<li>${inlineMarkdown(trimmed.replace(/^\d+\.\s+/, ""))}</li>`);
      return;
    }
    closeList();
    html.push(`<p>${inlineMarkdown(trimmed)}</p>`);
  });

  closeList();
  return html.join("");
}

function compact(text, max = 132) {
  const clean = String(text || "").replace(/\s+/g, " ").trim();
  return clean.length > max ? `${clean.slice(0, max)}...` : clean;
}

function formatDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString("ru-RU", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.hidden = false;
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    els.toast.hidden = true;
  }, 2800);
}

function setPageTitle(view) {
  const titles = {
    home: "Главная",
    tools: "Инструменты",
    tool: "Инструмент",
    history: "История",
    profile: "Профиль",
  };
  els.pageTitle.textContent = titles[view] || "FounderPilot AI";
}

function setView(view) {
  if (view === "chat") view = "home";
  state.previousView = state.currentView;
  state.currentView = view;
  document.querySelectorAll(".view").forEach((node) => node.classList.toggle("active", node.id === `view-${view}`));
  document.querySelectorAll(".nav-btn").forEach((button) => {
    const active = button.dataset.view === view || (view === "tool" && button.dataset.view === "tools");
    button.classList.toggle("active", active);
  });
  setPageTitle(view);
  if (tg?.BackButton) {
    if (view === "tool") tg.BackButton.show();
    else tg.BackButton.hide();
  }
  if (view === "home") setTimeout(scrollChatToBottom, 40);
  else window.scrollTo({ top: 0, behavior: "smooth" });
}

function makeActionButton(iconName, label, className = "chip-btn") {
  const button = document.createElement("button");
  button.type = "button";
  button.className = className;
  button.innerHTML = `${icon(iconName)}<span>${escapeHtml(label)}</span>`;
  return button;
}

function renderEmpty(target, text, iconName = "warning") {
  target.innerHTML = `
    <div class="empty-state">
      <span class="empty-icon">${icon(iconName)}</span>
      <p>${escapeHtml(text)}</p>
    </div>
  `;
}

async function copyText(text) {
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
  } catch (_) {
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    document.execCommand("copy");
    area.remove();
  }
  haptic("success");
  showToast("Скопировано");
}

function toolById(toolId) {
  return state.tools.find((tool) => tool.id === toolId) || fallbackTools.find((tool) => tool.id === toolId);
}

function toolTitle(toolId) {
  return toolById(toolId)?.title || toolId || "Инструмент";
}

function setupProfileHeader() {
  const name = userDisplayName();
  const user = telegramUser() || state.me?.user || {};
  els.userAvatar.textContent = initials(name);
  els.profileAvatar.textContent = initials(name);
  els.profileTitle.textContent = name === "предприниматель" ? "Пользователь" : name;
  els.profileUsername.textContent = user.username ? `@${user.username}` : "Telegram Mini App";
  els.homeGreeting.textContent = `Здравствуйте, ${name}`;
}

function renderUsage() {
  const usage = state.usage || {};
  const limit = usage.daily_limit ?? usage.free_limit ?? 20;
  $("statToday").textContent = usage.daily_used ?? usage.used_today ?? 0;
  $("statLimit").textContent = usage.unlimited ? "Без лимита" : limit;
  $("statRemaining").textContent = usage.unlimited ? "Без лимита" : usage.remaining ?? limit;
  $("statPlan").textContent = usage.status_label || usage.plan || "Free";
}

function fillBusinessProfile(profile) {
  const data = profile || {};
  const form = $("businessProfileForm");
  [...form.elements].forEach((field) => {
    if (!field.name) return;
    field.value = data[field.name] || "";
  });
}

async function loadMe() {
  const param = startParam();
  const url = param ? `/api/me?start_param=${encodeURIComponent(param)}` : "/api/me";
  const data = await api(url);
  state.me = data;
  state.profile = data.profile || null;
  state.usage = data.usage || null;
  setupProfileHeader();
  renderUsage();
  fillBusinessProfile(state.profile);
  const shouldOnboard = !data.user?.onboarding_completed || !data.profile;
  if (shouldOnboard) showOnboarding();
}

async function loadTools() {
  try {
    const data = await api("/api/tools");
    if (Array.isArray(data.tools) && data.tools.length) {
      state.tools = data.tools;
    }
  } catch (_) {
    state.tools = fallbackTools;
  }
  renderTools();
  renderQuickActions();
}

function renderQuickActions() {
  els.quickActions.innerHTML = "";
  quickActions.forEach((action) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "quick-action";
    button.innerHTML = `<span class="card-icon">${icon(action.icon)}</span><strong>${escapeHtml(action.label)}</strong>`;
    button.addEventListener("click", () => openTool(action.toolId));
    els.quickActions.appendChild(button);
  });
}

function renderTools() {
  els.toolsGrid.innerHTML = "";
  state.tools.forEach((tool) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "tool-tile";
    button.innerHTML = `
      <span class="card-icon">${icon(tool.icon || "tools")}</span>
      <h3>${escapeHtml(tool.title)}</h3>
      <p>${escapeHtml(tool.description)}</p>
      <span class="text-btn">Открыть</span>
    `;
    button.addEventListener("click", () => openTool(tool.id));
    els.toolsGrid.appendChild(button);
  });
}

function openTool(toolId) {
  const tool = toolById(toolId);
  if (!tool) return;
  state.currentTool = tool;
  state.currentToolRunId = null;
  state.currentResult = "";
  els.toolIcon.innerHTML = icon(tool.icon || "tools");
  els.toolTitle.textContent = tool.title;
  els.toolDescription.textContent = tool.description;
  els.toolInput.value = "";
  els.toolInput.placeholder = tool.placeholder || "Добавьте вводные, если нужно";
  els.toolResultCard.hidden = true;
  els.toolResultContent.innerHTML = "";
  els.toolResultActions.innerHTML = "";
  els.toolFeedbackBox.hidden = true;
  els.toolError.hidden = true;
  renderToolFields(tool);
  setView("tool");
}

function renderToolFields(tool) {
  els.toolFields.innerHTML = "";
  const fields = Array.isArray(tool.fields) ? tool.fields : [];
  if (!fields.length) {
    const wrapper = document.createElement("div");
    wrapper.innerHTML = `
      <label class="field-label" for="field-task">Вводные</label>
      <textarea id="field-task" data-field="task" data-required="true" placeholder="${escapeHtml(tool.placeholder || "Опишите задачу")}"></textarea>
    `;
    els.toolFields.appendChild(wrapper);
    return;
  }
  fields.forEach((field) => {
    const id = `field-${field.key}`;
    const required = String(field.required ?? "true") === "true";
    const wrapper = document.createElement("div");
    const common = `id="${escapeHtml(id)}" data-field="${escapeHtml(field.key)}" data-label="${escapeHtml(field.label)}" data-required="${required ? "true" : "false"}" placeholder="${escapeHtml(field.placeholder || "")}"`;
    if (field.type === "textarea") {
      wrapper.innerHTML = `
        <label class="field-label" for="${escapeHtml(id)}">${escapeHtml(field.label)}${required ? "" : " (необязательно)"}</label>
        <textarea ${common}></textarea>
      `;
    } else {
      wrapper.innerHTML = `
        <label class="field-label" for="${escapeHtml(id)}">${escapeHtml(field.label)}${required ? "" : " (необязательно)"}</label>
        <input ${common} inputmode="${escapeHtml(field.inputmode || "text")}" />
      `;
    }
    els.toolFields.appendChild(wrapper);
  });
}

function readToolInput() {
  const input = {};
  const missing = [];
  els.toolFields.querySelectorAll("[data-field]").forEach((field) => {
    const value = field.value.trim();
    input[field.dataset.field] = value;
    if (field.dataset.required === "true" && !value) {
      missing.push(field.dataset.label || "Поле");
    }
  });
  const notes = els.toolInput.value.trim();
  if (notes) input.additional_context = notes;
  return { input, missing };
}

function setToolError(message) {
  els.toolError.textContent = message;
  els.toolError.hidden = !message;
}

async function runTool(event) {
  event.preventDefault();
  if (!state.currentTool) return;
  const { input, missing } = readToolInput();
  if (missing.length) {
    setToolError(`Заполните поля: ${missing.join(", ")}`);
    haptic("error");
    return;
  }
  if (!Object.values(input).some((value) => String(value || "").trim())) {
    setToolError("Добавьте вводные для инструмента.");
    return;
  }

  setToolError("");
  els.generateBtn.disabled = true;
  els.generateBtn.innerHTML = `${icon("check")}<span>Готовлю результат...</span>`;
  els.toolResultCard.hidden = false;
  els.toolResultStatus.textContent = "В работе";
  els.toolResultStatus.classList.remove("error");
  els.toolResultContent.innerHTML = "<p>Готовлю структурированный результат. Обычно это занимает несколько секунд.</p>";
  els.toolResultActions.innerHTML = "";
  els.toolFeedbackBox.hidden = true;

  try {
    const data = await api("/api/tools/run", {
      method: "POST",
      body: JSON.stringify({
        telegram_user_id: telegramUser()?.id || null,
        tool_id: state.currentTool.id,
        input,
      }),
    });
    state.currentToolRunId = data.tool_run_id;
    state.currentResult = data.result || "";
    state.usage = data.usage || state.usage;
    els.toolResultStatus.textContent = "Готово";
    els.toolResultContent.innerHTML = markdownToHtml(state.currentResult);
    renderResultActions(els.toolResultActions, {
      title: state.currentTool.title,
      content: state.currentResult,
      sourceType: "tool_run",
      sourceId: state.currentToolRunId || state.currentTool.id,
      feedbackBox: els.toolFeedbackBox,
    });
    renderUsage();
    await Promise.all([loadHistory(), loadSaved()]);
    haptic("success");
    showToast("Результат готов");
  } catch (error) {
    els.toolResultStatus.textContent = "Ошибка";
    els.toolResultStatus.classList.add("error");
    els.toolResultContent.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
    await logInterfaceError("tool", error.message);
    haptic("error");
  } finally {
    els.generateBtn.disabled = false;
    els.generateBtn.innerHTML = `${icon("check")}<span>Получить результат</span>`;
  }
}

function updateChatSendButton() {
  els.sendChatBtn.disabled = state.chatLoading || els.chatInput.value.trim().length < 2;
}

function autoSizeChatInput() {
  els.chatInput.style.height = "auto";
  els.chatInput.style.height = `${Math.min(els.chatInput.scrollHeight, 132)}px`;
}

function scrollChatToBottom() {
  const last = els.chatMessages.lastElementChild;
  if (last) last.scrollIntoView({ behavior: "smooth", block: "end" });
}

function renderChat() {
  els.chatMessages.innerHTML = "";
  els.chatEmpty.hidden = state.chatMessages.length > 0 || state.chatLoading;
  state.chatMessages.forEach((message) => renderChatMessage(message));
}

function renderChatMessage(message, options = {}) {
  const wrapper = document.createElement("div");
  wrapper.className = `chat-message ${message.role === "user" ? "user" : "assistant"}`;
  if (options.loading) wrapper.dataset.loading = "true";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  if (message.role === "assistant" && !options.loading) {
    bubble.innerHTML = markdownToHtml(message.content);
  } else {
    bubble.textContent = message.content;
  }
  wrapper.appendChild(bubble);

  if (message.role === "assistant" && !options.loading) {
    const actions = document.createElement("div");
    actions.className = "message-actions";

    const copyBtn = makeActionButton("copy", "Скопировать");
    copyBtn.addEventListener("click", () => copyText(message.content));
    actions.appendChild(copyBtn);

    const saveBtn = makeActionButton("save", "Сохранить");
    saveBtn.addEventListener("click", () => saveResult({
      sourceType: "chat",
      sourceId: state.chatConversationId || "current",
      title: "Ответ AI Chat",
      content: message.content,
    }));
    actions.appendChild(saveBtn);

    improveActions.forEach((label) => {
      const button = makeActionButton("edit", label);
      button.addEventListener("click", () => improveAnswer(label, message.content));
      actions.appendChild(button);
    });

    const up = makeActionButton("thumbsUp", "Хорошо", "chip-btn icon-only");
    up.title = "Хороший ответ";
    up.addEventListener("click", () => submitFeedback(1, "chat", state.chatConversationId || "current"));
    actions.appendChild(up);

    const down = makeActionButton("thumbsDown", "Плохо", "chip-btn icon-only");
    down.title = "Нужно улучшить";
    down.addEventListener("click", () => showInlineFeedback(actions, "chat", state.chatConversationId || "current"));
    actions.appendChild(down);

    wrapper.appendChild(actions);
  }

  els.chatMessages.appendChild(wrapper);
  els.chatEmpty.hidden = true;
  setTimeout(scrollChatToBottom, 20);
}

async function sendChatMessage(text = null, options = {}) {
  const actualText = String(text ?? els.chatInput.value).trim();
  if (state.chatLoading || actualText.length < 2) return;

  state.chatLoading = true;
  updateChatSendButton();
  els.chatError.hidden = true;
  els.chatInput.value = "";
  autoSizeChatInput();

  const displayText = options.displayText || actualText;
  const userMessage = { role: "user", content: displayText };
  state.chatMessages.push(userMessage);
  renderChatMessage(userMessage);
  renderChatMessage({ role: "assistant", content: "AI думает..." }, { loading: true });

  try {
    const data = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        telegram_user_id: telegramUser()?.id || null,
        conversation_id: state.chatConversationId,
        message: actualText,
      }),
    });
    state.chatConversationId = data.conversation_id || state.chatConversationId;
    state.usage = data.usage || state.usage;
    const loading = els.chatMessages.querySelector("[data-loading='true']");
    if (loading) loading.remove();
    const answer = { role: "assistant", content: data.answer || "" };
    state.chatMessages.push(answer);
    renderChatMessage(answer);
    els.chatSubtitle.textContent = state.chatConversationId ? "Диалог сохранен" : "Текущий диалог";
    renderUsage();
    await Promise.all([loadHistory(), loadSaved()]);
    haptic("success");
  } catch (error) {
    const loading = els.chatMessages.querySelector("[data-loading='true']");
    if (loading) loading.remove();
    els.chatError.textContent = error.message;
    els.chatError.hidden = false;
    renderChatMessage({ role: "assistant", content: `Ошибка: ${error.message}` });
    await logInterfaceError("chat", error.message);
    haptic("error");
  } finally {
    state.chatLoading = false;
    updateChatSendButton();
  }
}

function improveAnswer(label, previousAnswer) {
  const prompt = `${label}. Используй прошлый ответ как контекст и не повторяй лишнее.\n\nПрошлый ответ:\n${previousAnswer}`;
  sendChatMessage(prompt, { displayText: label });
}

async function newChat() {
  try {
    const data = await api("/api/conversations", { method: "POST", body: JSON.stringify({}) });
    state.chatConversationId = data.conversation_id || null;
  } catch (_) {
    state.chatConversationId = null;
  }
  state.chatMessages = [];
  els.chatSubtitle.textContent = "Новый диалог";
  renderChat();
  setView("home");
  els.chatInput?.focus();
  haptic();
}

async function loadConversation(conversationId) {
  try {
    const data = await api(`/api/conversations/${encodeURIComponent(conversationId)}`);
    state.chatConversationId = String(data.conversation.id);
    state.chatMessages = (data.messages || []).filter((message) => ["user", "assistant"].includes(message.role));
    els.chatSubtitle.textContent = data.conversation.title || "Диалог";
    renderChat();
    setView("home");
  } catch (error) {
    showToast(error.message);
  }
}

function renderPromptSuggestions() {
  els.promptRow.innerHTML = "";
  promptSuggestions.forEach((text) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = text;
    button.addEventListener("click", () => {
      els.chatInput.value = text;
      autoSizeChatInput();
      updateChatSendButton();
      els.chatInput.focus();
      haptic();
    });
    els.promptRow.appendChild(button);
  });
}

async function saveResult({ sourceType, sourceId, title, content }) {
  if (!content) return;
  try {
    const data = await api("/api/saved", {
      method: "POST",
      body: JSON.stringify({
        source_type: sourceType,
        source_id: String(sourceId || "current"),
        title: title || "Сохраненный результат",
        content,
      }),
    });
    await Promise.all([loadSaved(), loadHistory()]);
    haptic("success");
    showToast("Сохранено");
    return data.id;
  } catch (error) {
    showToast(error.message);
    haptic("error");
  }
}

async function deleteSaved(savedId) {
  try {
    await api(`/api/saved/${savedId}`, { method: "DELETE" });
    await Promise.all([loadSaved(), loadHistory()]);
    closeDetail();
    haptic("success");
    showToast("Удалено из сохраненного");
  } catch (error) {
    showToast(error.message);
  }
}

async function submitFeedback(rating, sourceType, sourceId, message = "") {
  try {
    await api("/api/feedback", {
      method: "POST",
      body: JSON.stringify({
        source_type: sourceType,
        source_id: String(sourceId || "current"),
        rating,
        message,
      }),
    });
    haptic("success");
    showToast("Спасибо, отзыв сохранен");
  } catch (error) {
    showToast(error.message);
  }
}

function showInlineFeedback(target, sourceType, sourceId) {
  let box = target.querySelector(".feedback-box");
  if (!box) {
    box = document.createElement("div");
    box.className = "feedback-box";
    box.innerHTML = `
      <label class="field-label">Что улучшить?</label>
      <textarea placeholder="Коротко опишите проблему"></textarea>
      <button class="secondary full" type="button">${icon("check")}<span>Отправить отзыв</span></button>
    `;
    target.appendChild(box);
    box.querySelector("button").addEventListener("click", async () => {
      const message = box.querySelector("textarea").value.trim();
      await submitFeedback(-1, sourceType, sourceId, message);
      box.remove();
    });
  }
}

function renderResultActions(target, { title, content, sourceType, sourceId, feedbackBox, savedId = null }) {
  target.innerHTML = "";
  const copyBtn = makeActionButton("copy", "Скопировать");
  copyBtn.addEventListener("click", () => copyText(content));
  target.appendChild(copyBtn);

  if (!savedId) {
    const saveBtn = makeActionButton("save", "Сохранить");
    saveBtn.addEventListener("click", () => saveResult({ sourceType, sourceId, title, content }));
    target.appendChild(saveBtn);
  } else {
    const deleteBtn = makeActionButton("trash", "Удалить");
    deleteBtn.addEventListener("click", () => deleteSaved(savedId));
    target.appendChild(deleteBtn);
  }

  const up = makeActionButton("thumbsUp", "Хорошо", "chip-btn icon-only");
  up.title = "Хороший результат";
  up.addEventListener("click", () => submitFeedback(1, sourceType, sourceId));
  target.appendChild(up);

  const down = makeActionButton("thumbsDown", "Плохо", "chip-btn icon-only");
  down.title = "Нужно улучшить";
  down.addEventListener("click", () => {
    if (feedbackBox) {
      feedbackBox.hidden = false;
      feedbackBox.innerHTML = `
        <label class="field-label">Что улучшить?</label>
        <textarea placeholder="Коротко опишите проблему"></textarea>
        <button class="secondary full" type="button">${icon("check")}<span>Отправить отзыв</span></button>
      `;
      feedbackBox.querySelector("button").addEventListener("click", async () => {
        const message = feedbackBox.querySelector("textarea").value.trim();
        await submitFeedback(-1, sourceType, sourceId, message);
        feedbackBox.hidden = true;
      });
    } else {
      showInlineFeedback(target, sourceType, sourceId);
    }
  });
  target.appendChild(down);
}

async function loadHistory() {
  try {
    const data = await api("/api/history");
    state.history = {
      conversations: data.conversations || [],
      tool_runs: data.tool_runs || [],
      saved: data.saved || [],
      items: data.items || [],
    };
    renderHomeHistory();
    renderHistory();
  } catch (error) {
    renderEmpty(els.homeHistory, `История недоступна: ${error.message}`);
    renderEmpty(els.historyList, `История недоступна: ${error.message}`);
  }
}

async function loadSaved() {
  try {
    const data = await api("/api/saved");
    state.saved = data.items || [];
    renderSaved();
  } catch (error) {
    renderEmpty(els.savedList, `Сохраненное недоступно: ${error.message}`);
  }
}

function parseInputPreview(inputJson) {
  try {
    const data = JSON.parse(inputJson || "{}");
    return Object.entries(data)
      .filter(([, value]) => String(value || "").trim())
      .slice(0, 3)
      .map(([key, value]) => `${key}: ${value}`)
      .join("; ");
  } catch (_) {
    return "";
  }
}

function historyItems() {
  const conversations = state.history.conversations.map((item) => ({
    kind: "chats",
    typeLabel: "AI Chat",
    iconName: "chat",
    title: item.title || "AI Chat",
    preview: item.preview || "Диалог FounderPilot AI",
    date: item.updated_at,
    open: () => loadConversation(item.id),
  }));
  const tools = state.history.tool_runs.map((item) => ({
    kind: "tools",
    typeLabel: "Инструмент",
    iconName: toolById(item.tool_id)?.icon || "tools",
    title: toolTitle(item.tool_id),
    preview: item.result_text || parseInputPreview(item.input_json),
    date: item.created_at,
    open: () => openDetail({
      title: toolTitle(item.tool_id),
      content: item.result_text || "Результат пока недоступен.",
      sourceType: "tool_run",
      sourceId: item.id,
    }),
  }));
  const saved = state.history.saved.map((item) => ({
    kind: "saved",
    typeLabel: "Сохраненное",
    iconName: "save",
    title: item.title || "Сохраненный результат",
    preview: item.content,
    date: item.created_at,
    open: () => openDetail({
      title: item.title || "Сохраненный результат",
      content: item.content,
      sourceType: item.source_type,
      sourceId: item.source_id,
      savedId: item.id,
    }),
  }));
  return [...conversations, ...tools, ...saved].sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0));
}

function renderHistoryCard(item) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "history-card";
  button.innerHTML = `
    <span class="card-icon">${icon(item.iconName)}</span>
    <span class="history-body">
      <small>${escapeHtml(item.typeLabel)} · ${escapeHtml(formatDate(item.date))}</small>
      <strong>${escapeHtml(item.title)}</strong>
      <p>${escapeHtml(compact(item.preview))}</p>
    </span>
  `;
  button.addEventListener("click", item.open);
  return button;
}

function renderHomeHistory() {
  const items = historyItems().slice(0, 3);
  els.homeHistory.innerHTML = "";
  if (!items.length) {
    renderEmpty(els.homeHistory, "Здесь появятся последние результаты.", "history");
    return;
  }
  items.forEach((item) => els.homeHistory.appendChild(renderHistoryCard(item)));
}

function renderHistory() {
  const filter = state.historyFilter;
  const items = historyItems().filter((item) => filter === "all" || item.kind === filter);
  els.historyList.innerHTML = "";
  if (!items.length) {
    renderEmpty(els.historyList, "Истории пока нет.", "history");
    return;
  }
  items.forEach((item) => els.historyList.appendChild(renderHistoryCard(item)));
}

function renderSaved() {
  els.savedList.innerHTML = "";
  if (!state.saved.length) {
    renderEmpty(els.savedList, "Здесь будут сохраненные ответы.", "save");
    return;
  }
  state.saved.forEach((item) => {
    els.savedList.appendChild(renderHistoryCard({
      typeLabel: "Сохраненное",
      iconName: "save",
      title: item.title || "Сохраненный результат",
      preview: item.content,
      date: item.created_at,
      open: () => openDetail({
        title: item.title || "Сохраненный результат",
        content: item.content,
        sourceType: item.source_type,
        sourceId: item.source_id,
        savedId: item.id,
      }),
    }));
  });
}

function openDetail({ title, content, sourceType, sourceId, savedId = null }) {
  els.detailTitle.textContent = title;
  els.detailContent.innerHTML = markdownToHtml(content);
  renderResultActions(els.detailActions, { title, content, sourceType, sourceId, savedId });
  els.detailModal.hidden = false;
  tg?.BackButton?.show();
}

function closeDetail() {
  els.detailModal.hidden = true;
  if (state.currentView !== "tool") tg?.BackButton?.hide();
}

async function loadReferral() {
  try {
    const data = await api("/api/referral");
    $("referralLink").value = data.referral_link || data.referral_code || "";
    $("refInvited").textContent = data.invited_count ?? 0;
    $("refBonus").textContent = data.bonus_requests ?? 0;
  } catch (error) {
    $("referralLink").value = "Реферальные данные недоступны";
  }
}

async function saveBusinessProfile(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const payload = {};
  [...form.elements].forEach((field) => {
    if (field.name) payload[field.name] = field.value.trim();
  });
  const error = $("businessProfileError");
  error.hidden = true;
  try {
    const data = await api("/api/business-profile", { method: "POST", body: JSON.stringify(payload) });
    state.profile = data.profile;
    showToast("Профиль бизнеса сохранен");
    haptic("success");
  } catch (err) {
    error.textContent = err.message;
    error.hidden = false;
  }
}

async function clearBusinessProfile() {
  try {
    await api("/api/business-profile", { method: "DELETE" });
    state.profile = null;
    fillBusinessProfile(null);
    showToast("Профиль очищен");
  } catch (error) {
    showToast(error.message);
  }
}

function showOnboarding() {
  state.onboarding.step = 0;
  els.onboardingModal.hidden = false;
  renderOnboarding();
}

function renderOnboarding() {
  const step = state.onboarding.step;
  els.onboardingError.hidden = true;
  els.onboardingBackBtn.hidden = step === 0;
  els.onboardingNextBtn.textContent = step === 2 ? "Завершить" : "Далее";
  document.querySelectorAll(".progress-row span").forEach((node, index) => node.classList.toggle("active", index <= step));

  if (step === 0) {
    els.onboardingTitle.textContent = "Чем вы занимаетесь?";
    renderOnboardingOptions("user_type", ["Селлер WB/Ozon", "Предприниматель", "Маркетолог", "Новичок", "Другое"]);
  } else if (step === 1) {
    els.onboardingTitle.textContent = "Что хотите улучшить?";
    renderOnboardingOptions("main_goal", ["Продажи", "Карточки товара", "Рекламу", "Идеи товара", "Стратегию", "Расчеты"]);
  } else {
    els.onboardingTitle.textContent = "Коротко опишите бизнес";
    els.onboardingBody.innerHTML = `
      <label class="field-label" for="onboardingDescription">Описание</label>
      <textarea id="onboardingDescription" placeholder="Например: продаю товары для дома на WB, хочу увеличить продажи и улучшить карточки">${escapeHtml(state.onboarding.description)}</textarea>
    `;
  }
}

function renderOnboardingOptions(key, options) {
  els.onboardingBody.innerHTML = `<div class="option-grid"></div>`;
  const grid = els.onboardingBody.querySelector(".option-grid");
  options.forEach((option) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `option-card ${state.onboarding[key] === option ? "active" : ""}`;
    button.textContent = option;
    button.addEventListener("click", () => {
      state.onboarding[key] = option;
      renderOnboarding();
      haptic();
    });
    grid.appendChild(button);
  });
}

async function nextOnboarding() {
  const step = state.onboarding.step;
  if (step === 0 && !state.onboarding.user_type) {
    els.onboardingError.textContent = "Выберите вариант.";
    els.onboardingError.hidden = false;
    return;
  }
  if (step === 1 && !state.onboarding.main_goal) {
    els.onboardingError.textContent = "Выберите цель.";
    els.onboardingError.hidden = false;
    return;
  }
  if (step === 2) {
    state.onboarding.description = $("onboardingDescription").value.trim();
    if (!state.onboarding.description) {
      els.onboardingError.textContent = "Коротко опишите бизнес.";
      els.onboardingError.hidden = false;
      return;
    }
    try {
      const data = await api("/api/onboarding", {
        method: "POST",
        body: JSON.stringify({
          user_type: state.onboarding.user_type,
          main_goal: state.onboarding.main_goal,
          description: state.onboarding.description,
        }),
      });
      state.profile = data.profile;
      els.onboardingModal.hidden = true;
      await loadMe();
      setView("home");
      haptic("success");
    } catch (error) {
      els.onboardingError.textContent = error.message;
      els.onboardingError.hidden = false;
    }
    return;
  }
  state.onboarding.step += 1;
  renderOnboarding();
}

function previousOnboarding() {
  if (state.onboarding.step > 0) {
    state.onboarding.step -= 1;
    renderOnboarding();
  }
}

async function logInterfaceError(source, message) {
  try {
    await api("/api/feedback", {
      method: "POST",
      body: JSON.stringify({
        source_type: source,
        source_id: "frontend",
        rating: -1,
        message,
      }),
    });
  } catch (_) {
    // Feedback logging should never block the interface.
  }
}

function bindEvents() {
  document.querySelectorAll(".nav-btn").forEach((button) => {
    button.addEventListener("click", () => setView(button.dataset.view));
  });
  document.querySelectorAll("[data-open-view]").forEach((button) => {
    button.addEventListener("click", () => setView(button.dataset.openView));
  });
  document.querySelectorAll("[data-scroll-target]").forEach((button) => {
    button.addEventListener("click", () => {
      const target = $(button.dataset.scrollTarget);
      if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  $("headerProfileBtn").addEventListener("click", () => setView("profile"));
  $("openChatBtn").addEventListener("click", () => newChat());
  $("newChatBtn").addEventListener("click", newChat);
  $("backToToolsBtn").addEventListener("click", () => setView("tools"));
  $("closeDetailBtn").addEventListener("click", closeDetail);
  els.detailModal.addEventListener("click", (event) => {
    if (event.target === els.detailModal) closeDetail();
  });
  els.toolForm.addEventListener("submit", runTool);
  els.chatInput.addEventListener("input", () => {
    autoSizeChatInput();
    updateChatSendButton();
  });
  els.chatInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendChatMessage();
    }
  });
  els.sendChatBtn.addEventListener("click", () => sendChatMessage());
  $("businessProfileForm").addEventListener("submit", saveBusinessProfile);
  $("clearBusinessProfileBtn").addEventListener("click", clearBusinessProfile);
  $("refreshSavedBtn").addEventListener("click", loadSaved);
  $("copyReferralBtn").addEventListener("click", () => copyText($("referralLink").value));
  $("appFeedbackForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = $("appFeedbackText").value.trim();
    if (!message) {
      showToast("Напишите, что улучшить");
      return;
    }
    await submitFeedback(-1, "app", "profile", message);
    $("appFeedbackText").value = "";
  });
  els.onboardingNextBtn.addEventListener("click", nextOnboarding);
  els.onboardingBackBtn.addEventListener("click", previousOnboarding);
  $("historyFilters").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-filter]");
    if (!button) return;
    state.historyFilter = button.dataset.filter;
    $("historyFilters").querySelectorAll("button").forEach((node) => node.classList.toggle("active", node === button));
    renderHistory();
  });
}

(async function boot() {
  injectIcons();
  initTelegram();
  bindEvents();
  renderPromptSuggestions();
  setupProfileHeader();
  updateChatSendButton();
  await loadTools();
  try {
    await loadMe();
  } catch (error) {
    showToast(error.message);
  }
  await Promise.all([loadHistory(), loadSaved(), loadReferral()]);
  setView("home");
})();
