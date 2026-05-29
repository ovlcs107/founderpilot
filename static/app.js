/**
 * FounderPilot AI - Frontend App
 * Clean iOS/Linear Style
 */

const tg = window.Telegram?.WebApp || null;

const iconPaths = {
  home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline>',
  tools: '<rect x="3" y="3" width="7" height="7" rx="1"></rect><rect x="14" y="3" width="7" height="7" rx="1"></rect><rect x="14" y="14" width="7" height="7" rx="1"></rect><rect x="3" y="14" width="7" height="7" rx="1"></rect>',
  history: '<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>',
  user: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle>',
  send: '<line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>',
  search: '<circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line>',
  close: '<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>',
  edit: '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>',
  chart: '<line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line>',
  wallet: '<path d="M22 12V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2"></path><rect x="18" y="10" width="4" height="4"></rect>',
  stars: '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>',
  target: '<circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle>',
  message: '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>',
  mic: '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line>',
  save: '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline>',
  back: '<line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline>',
  copy: '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>',
  'credit-card': '<rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line>',
  ton: '<polygon points="12 2 3 9 12 22 21 9 12 2"></polygon><polyline points="3 9 12 13 21 9"></polyline><line x1="12" y1="22" x2="12" y2="13"></line>',
  btc: '<path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path><path d="M10 8h2.5a1.5 1.5 0 0 1 0 3H10V8z"></path><path d="M10 13h3a1.5 1.5 0 0 1 0 3h-3v-3z"></path><path d="M12 5v2"></path><path d="M12 17v2"></path>',
  coin: '<circle cx="12" cy="12" r="9"></circle><path d="M8.8 12h6.4"></path><path d="M12 8.8v6.4"></path>',
  plus: '<circle cx="12" cy="12" r="9"></circle><path d="M12 8v8"></path><path d="M8 12h8"></path>',
  bug: '<path d="M8 2l1.8 3h4.4L16 2"></path><rect x="7" y="5" width="10" height="14" rx="5"></rect><path d="M3 13h4"></path><path d="M17 13h4"></path><path d="M4.5 19l3-2"></path><path d="M19.5 19l-3-2"></path>',
  support: '<path d="M4 12a8 8 0 0 1 16 0"></path><path d="M4 12v4a2 2 0 0 0 2 2h1v-6H6a2 2 0 0 0-2 2"></path><path d="M20 12v4a2 2 0 0 1-2 2h-1v-6h1a2 2 0 0 1 2 2"></path><path d="M14 20h-4"></path>',
  receipt: '<path d="M6 2h12v20l-3-2-3 2-3-2-3 2V2z"></path><path d="M9 8h6"></path><path d="M9 12h6"></path><path d="M9 16h4"></path>'
};

const $ = id => document.getElementById(id);

const state = {
  user: null,
  activeView: 'home',
  isSending: false,
  tools: [],
  history: [],
  plans: {},
  providers: [],
  billingCapabilities: { autopay_available: false, yookassa_recurring_available: false },
  creditPacks: [],
  organizations: { active: null, owned: [], memberships: [] },
  supportTickets: [],
  supportMessages: [],
  activeSupportTicketId: null,
  historyFilter: 'all'
};

const TELEGRAM_INIT_DATA_STORAGE_KEY = 'founderpilot.telegramInitData';

function parseLaunchParams() {
  const result = new URLSearchParams(window.location.search || '');
  const hash = String(window.location.hash || '').replace(/^#/, '');
  if (hash) {
    const hashParams = new URLSearchParams(hash);
    hashParams.forEach((value, key) => {
      if (!result.has(key)) result.set(key, value);
    });
  }
  return result;
}

function getTelegramInitData() {
  const direct = tg?.initData || '';
  if (direct) {
    try { sessionStorage.setItem(TELEGRAM_INIT_DATA_STORAGE_KEY, direct); } catch {}
    return direct;
  }

  // Telegram Web sometimes exposes launch data in the URL hash while the SDK is still warming up.
  const launch = parseLaunchParams();
  const fromHash = launch.get('tgWebAppData') || launch.get('initData') || '';
  if (fromHash) {
    try {
      const decoded = decodeURIComponent(fromHash);
      sessionStorage.setItem(TELEGRAM_INIT_DATA_STORAGE_KEY, decoded);
      return decoded;
    } catch {
      return fromHash;
    }
  }

  try { return sessionStorage.getItem(TELEGRAM_INIT_DATA_STORAGE_KEY) || ''; } catch { return ''; }
}

function getTelegramUnsafeUser() {
  const direct = tg?.initDataUnsafe?.user;
  if (direct?.id) return direct;

  const initData = getTelegramInitData();
  if (!initData) return null;
  try {
    const parsed = new URLSearchParams(initData);
    const rawUser = parsed.get('user');
    return rawUser ? JSON.parse(rawUser) : null;
  } catch {
    return null;
  }
}

function buildTelegramFallbackUser() {
  const u = getTelegramUnsafeUser() || {};
  return {
    first_name: u.first_name || state.user?.first_name || 'Пользователь',
    last_name: u.last_name || state.user?.last_name || '',
    username: u.username || state.user?.username || '',
    telegram_id: u.id || state.user?.telegram_id || null,
    telegram_user_id: u.id ? String(u.id) : (state.user?.telegram_user_id || null),
    id: u.id || state.user?.id || null,
    photo_url: u.photo_url || state.user?.photo_url || '',
    avatar_url: u.photo_url || state.user?.avatar_url || '',
    plan: state.user?.plan || 'Free'
  };
}

function initTelegramBridge() {
  if (!tg) return;
  try { tg.ready?.(); } catch {}
  try { tg.expand?.(); } catch {}
  try { tg.setHeaderColor?.('bg_color'); tg.setBackgroundColor?.('bg_color'); } catch {}
  const snapshot = getTelegramUnsafeUser();
  if (snapshot?.id && !state.user) {
    state.user = buildTelegramFallbackUser();
    try { updateProfileUI(); } catch {}
  }
}

// Utils
function escapeHTML(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function escapeAttr(str) {
  return escapeHTML(str).replace(/`/g, "&#096;");
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
  setTimeout(() => el.classList.remove("visible"), 2500);
}

function getTelegramUserId() {
  const unsafe = getTelegramUnsafeUser();
  const raw = unsafe?.id || state.user?.telegram_id || state.user?.telegram_user_id || state.user?.id || null;
  const numeric = Number(raw);
  return Number.isFinite(numeric) && numeric > 0 ? numeric : null;
}

function withTelegramUser(payload = {}) {
  const telegramId = getTelegramUserId();
  return telegramId ? { ...payload, telegram_user_id: telegramId } : { ...payload };
}

const CHAT_STORAGE_KEY = 'founderpilot.activeConversationId';

function saveActiveConversationId(id) {
  if (!id) return;
  state.activeConversationId = String(id);
  try { localStorage.setItem(CHAT_STORAGE_KEY, String(id)); } catch {}
}

function clearActiveConversationId() {
  state.activeConversationId = null;
  try { localStorage.removeItem(CHAT_STORAGE_KEY); } catch {}
}

async function ensureActiveConversation() {
  if (state.activeConversationId) return state.activeConversationId;
  const created = await apiRequest('/api/conversations', { method: 'POST', body: JSON.stringify({}) });
  const id = created.conversation_id || created.id;
  if (id) saveActiveConversationId(id);
  return state.activeConversationId;
}

async function loadConversationIntoHome(conversationId, { silent = false } = {}) {
  if (!conversationId) return false;
  try {
    const data = await apiRequest(`/api/conversations/${encodeURIComponent(conversationId)}`);
    const messages = Array.isArray(data.messages) ? data.messages : [];
    saveActiveConversationId(conversationId);
    const scroll = $('homeChatScroll');
    if (scroll) scroll.innerHTML = '';
    if (messages.length) {
      $('view-home')?.classList.add('chat-active');
      messages.forEach(m => appendMessage(m.role === 'assistant' ? 'bot' : m.role, m.content || ''));
    }
    return true;
  } catch (err) {
    if (!silent) showToast(friendlyError(err, 'Не удалось открыть диалог'));
    return false;
  }
}

async function restoreLastConversation() {
  const saved = (() => { try { return localStorage.getItem(CHAT_STORAGE_KEY); } catch { return null; } })();
  if (saved && await loadConversationIntoHome(saved, { silent: true })) return;
  try {
    const data = await apiRequest('/api/conversations');
    const items = Array.isArray(data.items) ? data.items : [];
    const latest = items.find(item => Number(item.messages_count || 0) > 0) || items[0];
    if (latest?.id) await loadConversationIntoHome(latest.id, { silent: true });
  } catch {}
}

function openExternal(url) {
  if (!url) return;
  if (tg?.openLink) tg.openLink(url);
  else window.open(url, "_blank", "noopener,noreferrer");
}

function openPaymentLink(url, provider) {
  if (!url) return;
  if (provider === "telegram_stars" && tg?.openInvoice) {
    try {
      tg.openInvoice(url, status => {
        if (status === "paid") showToast("Оплата получена");
      });
      return;
    } catch (err) {
      console.warn("Telegram invoice open failed, fallback to link", err);
    }
  }
  openExternal(url);
}

// API
async function apiRequest(url, options = {}) {
  const headers = { "Content-Type": "application/json" };
  const initData = getTelegramInitData();
  if (initData) headers["X-Telegram-Init-Data"] = initData;

  const res = await fetch(url, { ...options, headers: { ...headers, ...options.headers } });
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { detail: text }; }

  if (!res.ok || data?.ok === false) {
    throw new Error(data?.error || data?.detail || "Сервис временно недоступен");
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

// Fallbacks
function getFallbackTools() {
  return [
    { id: "margin", title: "Анализ идеи", description: "Оценка рынка и перспектив", prompt_template: "Проанализируй идею нового продукта и оцени спрос." },
    { id: "plan", title: "Бизнес-план", description: "Пошаговый план и финмодель", prompt_template: "Составь пошаговый бизнес-план." },
    { id: "pitch", title: "Презентация", description: "Создание питч-дека", prompt_template: "Сделай план презентации для инвесторов." },
    { id: "market", title: "Маркетинг", description: "Стратегия продвижения", prompt_template: "Составь маркетинговый план." }
  ];
}

function getFallbackPlans() {
  return [
    { key: "free", title: "Free", description: "Базовые инструменты и лимиты", price_text: "0 ₽", providers: [] },
    { key: "go", title: "Go", description: "Для первых регулярных задач", price_text: "399 ₽ / мес", providers: [] },
    { key: "plus", title: "Plus", description: "Оптимум для активной работы", price_text: "990 ₽ / мес", providers: [] },
    { key: "pro", title: "Pro", description: "Для серьёзного запуска и роста", price_text: "2 490 ₽ / мес", providers: [] },
    { key: "business", title: "Business", description: "Команды, роли и совместная работа", price_text: "7 990 ₽ / мес", providers: [] }
  ];
}

function getFallbackCreditPacks() {
  return [
    { id: "pack1", title: "1 000 кредитов", price_text: "199 ₽" },
    { id: "pack2", title: "5 000 кредитов", price_text: "799 ₽" },
    { id: "pack3", title: "15 000 кредитов", price_text: "1 990 ₽" },
    { id: "pack4", title: "50 000 кредитов", price_text: "5 490 ₽" }
  ];
}

function normalizeProviderId(id) {
  const value = String(id || "").toLowerCase();
  if (value === "stars") return "telegram_stars";
  if (value === "card" || value === "sbp") return "yookassa";
  if (value === "btc") return "btcpay_btc";
  return value;
}

function providerInfo(id) {
  const key = normalizeProviderId(id);
  const map = {
    telegram_stars: { id: "telegram_stars", title: "Telegram Stars", description: "Оплата внутри Telegram", icon: "stars" },
    yookassa: { id: "yookassa", title: "Карта / СБП", description: "Банковская карта или СБП", icon: "credit-card" },
    ton: { id: "ton", title: "TON", description: "Оплата через TON", icon: "ton" },
    btcpay_btc: { id: "btcpay_btc", title: "BTC", description: "Оплата в BTC", icon: "btc" }
  };
  return map[key] || { id: key, title: key, description: "Оплата онлайн", icon: "credit-card" };
}

function enabledProviderIds(plan = null) {
  const source = Array.isArray(plan?.providers) && plan.providers.length ? plan.providers : state.providers;
  return new Set((source || []).map(p => normalizeProviderId(p.id || p.key || p.provider || p)));
}

function friendlyError(err, fallback = "Что-то пошло не так") {
  const raw = String(err?.message || err || fallback);
  if (/recurring|автопродлен|автосписан|save_payment_method|forbidden/i.test(raw)) return "Автопродление временно недоступно. Оплата тарифа работает без него.";
  if (/yookassa|юkassa|shop_id|secret_key|\.env|telegram_stars|openrouter|provider/i.test(raw)) return "Оплата временно недоступна. Попробуйте позже.";
  if (/not\s*found|404/i.test(raw)) return "Функция пока недоступна";
  if (/failed to fetch|network|сервер/i.test(raw)) return "Сервис временно недоступен";
  if (/undefined|null|\[object Object\]/i.test(raw)) return fallback;
  return raw;
}

// Navigation & UI
function switchView(target) {
  if (target !== "profile") closeProfilePane();
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(b => b.classList.toggle("active", b.dataset.target === target));

  const v = $(`view-${target}`);
  if (v) v.classList.add("active");
  state.activeView = target;
}

function switchProfilePane(paneId) {
  if (window.innerWidth < 1100) {
    $("profileShell")?.classList.add("detail-open");
  }
  document.querySelectorAll(".mobile-tab-link").forEach(b => b.classList.toggle("active", b.dataset.pane === paneId));
  document.querySelectorAll(".profile-sub-pane").forEach(p => {
    p.classList.toggle("active", p.id === `pane-${paneId}`);
  });
}

function closeProfilePane() {
  $("profileShell")?.classList.remove("detail-open");
}

function applyAvatar(el, user) {
  if (!el) return;
  const initial = user?.first_name?.charAt(0).toUpperCase() || "U";
  if (user?.photo_url) {
    el.style.backgroundImage = `url("${user.photo_url.replace(/"/g, "%22")}")`;
    el.textContent = "";
  } else {
    el.style.backgroundImage = "";
    el.textContent = initial;
  }
}

function setText(id, value) {
  const el = $(id);
  if (el) el.textContent = value;
}

function updateProfileUI() {
  const fallback = { first_name: "Пользователь", username: "", telegram_id: "—", plan: "Free", photo_url: "" };
  const u = { ...fallback, ...(state.user || {}) };
  const planName = String(u.plan || "Free");
  const planNameUpper = planName.charAt(0).toUpperCase() + planName.slice(1);
  const subtitle = u.username ? `@${u.username}` : `ID: ${u.telegram_id || "—"}`;

  setText("homeGreeting", `Доброе утро, ${u.first_name}! 👋`);

  ["sidebarAvatar", "headerUserAvatar", "desktopTopAvatar", "mobileHeaderAvatar", "profileUserAvatar", "profileUserAvatarLarge"].forEach(id => applyAvatar($(id), u));

  setText("sidebarUserName", u.first_name);
  setText("sidebarUserPlan", planNameUpper);
  setText("profileUserTitle", u.first_name);
  setText("profileUserTitleMirror", u.first_name);
  setText("profileUserTitleMirror2", u.first_name);
  setText("profileUserSubtitle", subtitle);
  setText("profileUserSubtitleMirror", subtitle);
  setText("profileUserSubtitleMirror2", subtitle);
  setText("profilePlanLabel", planNameUpper);
  setText("profilePlanLabelMirror", planNameUpper);

  const planPrice = getPlanPriceText ? getPlanPriceText(planName.toLowerCase()) : "";
  setText("profilePlanPrice", planPrice);
  setText("profilePlanPriceMirror", planPrice);
  setText("subscriptionCurrentPlan", planNameUpper);
  setText("subscriptionCurrentPrice", planPrice || "0 ₽");
  setText("profileSubscriptionPlanTitle", planNameUpper);
  setText("profileSubscriptionPrice", planPrice || "0 ₽");

  const assignValue = (id, value) => {
    const el = $(id);
    if (!el) return;
    if ("value" in el) el.value = value;
    else el.textContent = value;
  };
  assignValue("profileNameValue", u.first_name || "Пользователь");
  assignValue("profileUsernameValue", u.username ? `@${u.username}` : "—");
  assignValue("profileTelegramIdValue", u.telegram_id || "—");
  assignValue("profileCompanyName", u.company_name || "");
  assignValue("profileBusinessDescription", u.business_profile || "");

  const remaining = Number(u.remaining_credits_today ?? u.remaining ?? u.credits ?? 0);
  if ($("desktopTopCreditsValue")) $("desktopTopCreditsValue").textContent = remaining ? remaining.toLocaleString("ru-RU") : "100";

  const isBusiness = planName.toLowerCase() === "business";
  const teamNotice = $("teamBusinessNotice");
  if (teamNotice) teamNotice.style.display = isBusiness ? "none" : "block";
  if ($("teamActiveContent")) $("teamActiveContent").style.display = isBusiness ? "block" : "none";
}

function getPlanPriceText(planKey = "free") {
  const key = String(planKey || "free").toLowerCase();
  // Canonical public prices. Do not trust stale backend/cache values for these keys.
  const canonical = { free: "0 ₽", go: "399 ₽ / мес", plus: "990 ₽ / мес", pro: "2 490 ₽ / мес", business: "7 990 ₽ / мес" };
  if (canonical[key]) return canonical[key];
  const plans = Array.isArray(state.plans) ? state.plans : Object.values(state.plans || {});
  const plan = plans.find(p => String(p.key || p.id || p.slug || p.title || "").toLowerCase() === key);
  if (plan) return plan.price_text || plan.price || "";
  return "0 ₽";
}

// Markdown parser
function formatInlineMarkdown(raw) {
  const chunks = String(raw || "").split(/(`[^`]*`)/g);
  return chunks.map(chunk => {
    if (chunk.startsWith("`") && chunk.endsWith("`") && chunk.length >= 2) {
      return `<code>${escapeHTML(chunk.slice(1, -1))}</code>`;
    }

    let out = escapeHTML(chunk);
    out = out.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+|\/[^\s)]*)\)/g, (_, label, url) => {
      const safeUrl = escapeAttr(url);
      return `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer">${label}</a>`;
    });
    out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    out = out.replace(/__([^_]+)__/g, '<strong>$1</strong>');
    out = out.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>');
    out = out.replace(/(^|[^_])_([^_\n]+)_/g, '$1<em>$2</em>');
    return out;
  }).join("");
}

function splitMarkdownTableRow(line) {
  return String(line || "")
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map(cell => cell.trim());
}

function isMarkdownTableSeparator(line) {
  return /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line || "");
}

function renderMarkdown(text) {
  const source = String(text || "").replace(/\r\n/g, "\n").trim();
  if (!source) return "";

  const lines = source.split("\n");
  const result = [];
  let i = 0;

  while (i < lines.length) {
    const rawLine = lines[i] || "";
    const line = rawLine.trim();

    if (!line) {
      i += 1;
      continue;
    }

    if (line.startsWith("```")) {
      const lang = line.slice(3).trim().replace(/[^a-z0-9_-]/gi, "").toLowerCase();
      const buffer = [];
      i += 1;
      while (i < lines.length && !String(lines[i]).trim().startsWith("```")) {
        buffer.push(lines[i]);
        i += 1;
      }
      if (i < lines.length) i += 1;
      const cls = lang ? ` class="language-${escapeAttr(lang)}"` : "";
      result.push(`<pre><code${cls}>${escapeHTML(buffer.join("\n"))}</code></pre>`);
      continue;
    }

    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      const level = heading[1].length;
      result.push(`<h${level}>${formatInlineMarkdown(heading[2])}</h${level}>`);
      i += 1;
      continue;
    }

    if (line.includes("|") && i + 1 < lines.length && isMarkdownTableSeparator(lines[i + 1])) {
      const headers = splitMarkdownTableRow(line);
      const body = [];
      i += 2;
      while (i < lines.length && String(lines[i]).trim().includes("|")) {
        body.push(splitMarkdownTableRow(lines[i]));
        i += 1;
      }
      result.push(
        `<div class="md-table-wrap"><table><thead><tr>${headers.map(h => `<th>${formatInlineMarkdown(h)}</th>`).join("")}</tr></thead><tbody>${body.map(row => `<tr>${headers.map((_, idx) => `<td>${formatInlineMarkdown(row[idx] || "")}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`
      );
      continue;
    }

    if (/^[-*+]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*[-*+]\s+/.test(lines[i] || "")) {
        items.push(String(lines[i]).replace(/^\s*[-*+]\s+/, ""));
        i += 1;
      }
      result.push(`<ul>${items.map(item => `<li>${formatInlineMarkdown(item)}</li>`).join("")}</ul>`);
      continue;
    }

    if (/^\d+[.)]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*\d+[.)]\s+/.test(lines[i] || "")) {
        items.push(String(lines[i]).replace(/^\s*\d+[.)]\s+/, ""));
        i += 1;
      }
      result.push(`<ol>${items.map(item => `<li>${formatInlineMarkdown(item)}</li>`).join("")}</ol>`);
      continue;
    }

    if (/^>\s+/.test(line)) {
      const quotes = [];
      while (i < lines.length && /^\s*>\s+/.test(lines[i] || "")) {
        quotes.push(String(lines[i]).replace(/^\s*>\s+/, ""));
        i += 1;
      }
      result.push(`<blockquote>${quotes.map(formatInlineMarkdown).join("<br>")}</blockquote>`);
      continue;
    }

    const paragraph = [rawLine.trim()];
    i += 1;
    while (i < lines.length) {
      const next = String(lines[i] || "");
      const t = next.trim();
      if (!t || t.startsWith("```") || /^(#{1,4})\s+/.test(t) || /^\s*[-*+]\s+/.test(next) || /^\s*\d+[.)]\s+/.test(next) || /^\s*>\s+/.test(next)) break;
      if (t.includes("|") && i + 1 < lines.length && isMarkdownTableSeparator(lines[i + 1])) break;
      paragraph.push(t);
      i += 1;
    }
    result.push(`<p>${formatInlineMarkdown(paragraph.join(" "))}</p>`);
  }

  return result.join("");
}

// Chat
function activateHomeChatMode() {
  const view = $("view-home");
  if (!view || view.classList.contains("chat-active")) return;

  const composer = view.querySelector(".chat-composer-zone");
  const firstRect = composer?.getBoundingClientRect();

  view.classList.add("chat-active");

  // FLIP-анимация: поле ввода плавно переезжает из центра вниз, как в ChatGPT.
  if (composer && firstRect && composer.animate) {
    const lastRect = composer.getBoundingClientRect();
    const dx = firstRect.left - lastRect.left;
    const dy = firstRect.top - lastRect.top;
    const scaleX = firstRect.width && lastRect.width ? firstRect.width / lastRect.width : 1;

    composer.animate([
      { transform: `translate(${dx}px, ${dy}px) scaleX(${scaleX})`, transformOrigin: "center bottom" },
      { transform: "translate(0, 0) scaleX(1)", transformOrigin: "center bottom" }
    ], {
      duration: 420,
      easing: "cubic-bezier(.22,.61,.36,1)",
      fill: "both"
    });
  }
}

function appendMessage(role, text, id = null) {
  const scroll = $("homeChatScroll");
  if (!scroll) return;

  activateHomeChatMode();

  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;
  if (id) wrap.id = id;

  const txtDiv = document.createElement("div");
  if (role === "user" || role === "bot") {
    txtDiv.className = "md-content";
    txtDiv.innerHTML = renderMarkdown(text);
  } else {
    txtDiv.textContent = text;
  }
  wrap.appendChild(txtDiv);

  if (role === "bot" && text !== "FounderPilot готовит ответ...") {
    const act = document.createElement("div");
    act.className = "message-actions";

    const copyBtn = document.createElement("button");
    copyBtn.innerHTML = `<span data-icon="copy"></span> Скопировать`;
    copyBtn.onclick = () => {
      navigator.clipboard.writeText(text).then(() => showToast("Скопировано"));
    };

    act.appendChild(copyBtn);
    wrap.appendChild(act);
  }

  scroll.appendChild(wrap);
  scroll.scrollTop = scroll.scrollHeight;
  injectIcons(wrap);
}

function autoResizeTextarea() {
  const el = $("homeChatInput");
  if (!el) return;
  el.style.height = "auto";
  el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
  $("homeChatSendBtn").disabled = !el.value.trim() || state.isSending;
}

async function handleChatSend() {
  const input = $("homeChatInput");
  const text = input?.value.trim();
  if (!text || state.isSending) return;

  state.isSending = true;
  $("homeChatSendBtn").disabled = true;
  input.value = "";
  autoResizeTextarea();

  appendMessage("user", text);
  const sysId = `sys_${Date.now()}`;
  appendMessage("system", "FounderPilot готовит ответ...", sysId);

  try {
    const payload = withTelegramUser({ message: text, text: text, mode: "chat", conversation_id: state.activeConversationId || null });
    const res = await apiTry("/api/chat", "/api/ask", { method: "POST", body: JSON.stringify(payload) });

    $(sysId)?.remove();
    const answer = res.answer || res.response || res.result || res.text || "Аналитический модуль вернул пустой результат.";
    appendMessage("bot", answer);
    if (res.conversation_id) saveActiveConversationId(res.conversation_id);
  } catch (err) {
    const sys = $(sysId);
    if (sys) sys.textContent = "Ошибка: " + err.message;
  } finally {
    state.isSending = false;
    autoResizeTextarea();
  }
}

// Rendering
function renderQuickActions() {
  const container = $("quickStrip");
  if (!container) return;
  const tools = state.tools.slice(0, 4);
  container.innerHTML = tools.map(t => `
    <button class="quick-pill" data-prompt="${escapeHTML(t.prompt_template || '')}">
      <div class="icon-box"><span data-icon="stars"></span></div>
      <div class="text-box"><b>${escapeHTML(t.title)}</b><small>${escapeHTML(t.description)}</small></div>
    </button>
  `).join("");
  injectIcons(container);
}

function renderTools() {
  const container = $("toolsGrid");
  if (!container) return;
  const q = $("toolsSearchInput")?.value.toLowerCase().trim() || "";

  const filtered = state.tools.filter(t => (t.title + " " + t.description).toLowerCase().includes(q));

  if (!filtered.length) {
    container.innerHTML = `
      <div class="empty-panel embedded-empty">
        <span data-icon="search"></span>
        <h3>&#1053;&#1080;&#1095;&#1077;&#1075;&#1086; &#1085;&#1077; &#1085;&#1072;&#1081;&#1076;&#1077;&#1085;&#1086;</h3>
        <p>&#1055;&#1086;&#1087;&#1088;&#1086;&#1073;&#1091;&#1081;&#1090;&#1077; &#1076;&#1088;&#1091;&#1075;&#1086;&#1081; &#1079;&#1072;&#1087;&#1088;&#1086;&#1089; &#1080;&#1083;&#1080; &#1082;&#1072;&#1090;&#1077;&#1075;&#1086;&#1088;&#1080;&#1102;.</p>
      </div>`;
    injectIcons(container);
    return;
  }

  container.innerHTML = filtered.map(t => `
    <button class="list-row tool-card" data-prompt="${escapeHTML(t.prompt_template)}">
      <div class="icon-box"><span data-icon="tools"></span></div>
      <div class="info">
        <h4>${escapeHTML(t.title)}</h4>
        <p>${escapeHTML(t.description)}</p>
      </div>
      <span class="chevron">›</span>
    </button>
  `).join("");
  injectIcons(container);
}

function normalizeHistoryData(data) {
  if (Array.isArray(data)) return data;

  const result = [];
  const pushItems = (items, type, fallbackTitle) => {
    (items || []).forEach(item => {
      if (!item || typeof item !== "object") return;
      const created = item.created_at || item.updated_at || item.date || item.started_at || "";
      result.push({
        ...item,
        type: item.type || type,
        title: item.title || item.tool_title || item.mode_title || item.message || item.prompt || fallbackTitle,
        message: item.message || item.content || item.result || item.prompt || "",
        date: item.date || formatHistoryDate(created),
        created_at: created
      });
    });
  };

  pushItems(data?.items || data?.history, "tools", "Документ");
  pushItems(data?.conversations, "chat", "Диалог");
  pushItems(data?.tool_runs, "tools", "Документ");
  pushItems(data?.saved, "favorites", "Сохранено");

  const seen = new Set();
  return result
    .filter(item => {
      const key = `${item.type}:${item.id || item.conversation_id || item.source_id || item.title}:${item.created_at || item.date}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    })
    .sort((a, b) => Date.parse(b.created_at || b.date || 0) - Date.parse(a.created_at || a.date || 0));
}

function formatHistoryDate(value) {
  if (!value) return "Недавно";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString("ru-RU", { day: "2-digit", month: "short" });
}


function planBenefitLines(plan) {
  const key = String(plan?.key || plan?.id || "free").toLowerCase();
  const f = plan?.features || {};
  const monthly = Number(plan?.monthly_limit || plan?.credits_monthly_limit || 0);
  const daily = Number(plan?.daily_limit || plan?.credits_daily_limit || 0);
  const lines = [];
  if (monthly) lines.push(`${monthly.toLocaleString('ru-RU')} кредитов в месяц`);
  if (daily) lines.push(`${daily.toLocaleString('ru-RU')} кредитов в день`);
  if (f.exports) lines.push('Экспорт документов');
  if (Number(f.projects || 0) > 0) lines.push(`${Number(f.projects).toLocaleString('ru-RU')} проект${Number(f.projects) === 1 ? '' : 'ов'}`);
  if (Number(f.team_members || 0) > 0) lines.push(`Команда до ${f.team_members} участников`);
  if (f.priority_support) lines.push('Приоритетная поддержка');
  if (key === 'free') lines.push('Стартовый доступ без оплаты');
  return lines.slice(0, 5);
}

function renderCurrentPlanBenefits(plan) {
  const list = $("subscriptionBenefitsList");
  if (!list) return;
  const lines = planBenefitLines(plan);
  list.innerHTML = (lines.length ? lines : ['Серверные лимиты и история результатов']).map(line =>
    `<li><span class="bullet-check">✓</span> ${escapeHTML(line)}</li>`
  ).join('');
  const note = $("subscriptionSafetyNote");
  if (note) {
    note.textContent = plan?.profit_guard_enabled === false
      ? 'Лимиты и кредиты обновляются автоматически.'
      : 'Лимиты и кредиты обновляются автоматически.';
  }
}

function renderHistory() {
  const container = $("historyList");
  const empty = $("historyEmptyState");
  if (!container || !empty) return;

  let items = state.history || [];
  const q = ($("historySearchInput")?.value || $("historySearchInputMobile")?.value || "").toLowerCase().trim();

  if (q) {
    items = items.filter(i => (i.title || i.message || "").toLowerCase().includes(q));
  }
  if (state.historyFilter !== 'all') {
    items = items.filter(i => i.type === state.historyFilter || i.mode === state.historyFilter);
  }

  if (items.length === 0) {
    container.innerHTML = "";
    empty.hidden = false;
    empty.style.display = "block";
    return;
  }
  empty.hidden = true;
  empty.style.display = "none";

  container.innerHTML = items.map(h => `
    <div class="list-row">
      <div class="icon-box"><span data-icon="${h.type === 'chat' ? 'message' : 'save'}"></span></div>
      <div class="info">
        <h4>${escapeHTML(h.title || h.message || "Диалог")}</h4>
        <p>${escapeHTML(h.type === 'chat' ? 'Чат с AI' : 'Документ')}</p>
      </div>
      <span class="meta">${escapeHTML(h.date || h.created_at || "Недавно")}</span>
    </div>
  `).join("");
  injectIcons(container);
}

function renderAutopayControl() {
  const toggle = $("subscriptionAutopayToggle");
  const note = $("subscriptionAutopayNote");
  const row = toggle?.closest(".toggle-row");
  const section = row?.closest(".settings-section");
  const available = Boolean(state.billingCapabilities?.autopay_available || state.billingCapabilities?.yookassa_recurring_available);

  // Не показываем пользователю технические статусы платёжного провайдера.
  // Если автопродление недоступно, интерфейс просто остаётся чистым: пользователь видит обычную оплату тарифа.
  if (section) {
    section.hidden = !available;
    section.style.display = available ? "" : "none";
  }

  if (toggle) {
    toggle.disabled = !available;
    if (!available) toggle.checked = false;
  }
  if (row) row.classList.toggle("disabled-row", !available);
  if (note) note.textContent = available ? "Можно включить для следующих списаний" : "";
}

function renderSubscription() {
  const planList = $("subscriptionPlanList");
  if (!planList) return;

  const currentPlan = String(state.user?.plan || "free").toLowerCase();

  const plans = Array.isArray(state.plans) ? state.plans : Object.values(state.plans || {});

  if ($("subscriptionCurrentPlan")) {
    const cp = plans.find(p => String(p.key).toLowerCase() === currentPlan) || plans[0];
    $("subscriptionCurrentPlan").textContent = cp ? (cp.title || cp.name || "Free") : "Free";
    if ($("subscriptionCurrentPrice")) $("subscriptionCurrentPrice").textContent = cp ? getPlanPriceText(cp.key || cp.id || currentPlan) : "0 ₽";
    renderCurrentPlanBenefits(cp);
  }

  planList.innerHTML = plans.map(p => {
    const key = String(p.key || p.id || p.slug || "free").toLowerCase();
    const active = key === currentPlan;
    const benefits = planBenefitLines(p).slice(0, 3).map(item => `<span>${escapeHTML(item)}</span>`).join("");
    return `
      <button class="plan-card subscription-plan-row ${active ? 'active' : ''}" data-plan="${escapeHTML(key)}">
        <div class="plan-row-main"><h4>${escapeHTML(p.title || p.name || key)}</h4><small>${escapeHTML(p.description || p.subtitle || "")}</small><div class="plan-feature-chips">${benefits}</div></div>
        <div class="subscription-price">${escapeHTML(getPlanPriceText(key))}</div>
        <span class="check">✓</span>
      </button>
    `;
  }).join("");
  updateProfileUI();
  renderAutopayControl();
}

function chooseAutoProvider(enabled) {
  const order = tg?.initData ? ["telegram_stars", "yookassa", "ton", "btcpay_btc"] : ["yookassa", "telegram_stars", "ton", "btcpay_btc"];
  return order.find(id => enabled.has(id)) || Array.from(enabled)[0] || "auto";
}

function selectPlan(key) {
  key = String(key || "").toLowerCase();
  if (key === 'free') {
    showToast("Тариф Free доступен по умолчанию");
    if ($("paymentSection")) $("paymentSection").style.display = "none";
    return;
  }

  document.querySelectorAll(".plan-card").forEach(c => c.classList.toggle("active", c.dataset.plan === key));

  const plans = Array.isArray(state.plans) ? state.plans : Object.values(state.plans || {});
  const plan = plans.find(p => String(p.key || p.id || p.slug).toLowerCase() === key) || null;
  renderCurrentPlanBenefits(plan);
  const enabled = enabledProviderIds(plan);
  const preferred = ["telegram_stars", "yookassa", "ton", "btcpay_btc"].map(providerInfo);

  const box = $("subscriptionPaymentProviders");
  if (box) {
    if (!enabled.size) {
      box.innerHTML = `
        <div class="provider-empty-note">
          <b>Способы оплаты не настроены</b>
          <p>Оплата временно недоступна. Мы уже работаем над восстановлением способов оплаты.</p>
        </div>`;
    } else {
      const autoProvider = chooseAutoProvider(enabled);
      const autoCard = `
        <button class="provider-btn provider-primary" data-provider="${escapeHTML(autoProvider)}" data-plan="${escapeHTML(key)}">
          <span class="icon" data-icon="credit-card"></span>
          <div class="info">
            <h5>Оплатить тариф</h5>
            <p>Безопасная оплата выбранного тарифа</p>
          </div>
        </button>`;
      const providerCards = preferred.map(prov => {
        const isEnabled = enabled.has(prov.id);
        const badge = isEnabled ? "" : `<span class="provider-soon">Скоро</span>`;
        return `
          <button class="provider-btn ${isEnabled ? '' : 'disabled'}" ${isEnabled ? '' : 'disabled'} data-provider="${escapeHTML(prov.id)}" data-plan="${escapeHTML(key)}" aria-disabled="${isEnabled ? 'false' : 'true'}">
            <span class="icon" data-icon="${escapeHTML(prov.icon)}"></span>
            <div class="info">
              <h5>${escapeHTML(prov.title)} ${badge}</h5>
              <p>${escapeHTML(isEnabled ? prov.description : 'Будет доступно позже')}</p>
            </div>
          </button>`;
      }).join("");
      box.innerHTML = autoCard + providerCards;
    }
    injectIcons(box);
  }
  if ($("paymentSection")) {
    $("paymentSection").style.display = "block";
    $("paymentSection").scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}


function pollOrderStatus(orderId) {
  if (!orderId) return;
  let tries = 0;
  const timer = setInterval(async () => {
    tries += 1;
    try {
      const data = await apiRequest(`/api/billing/order/${encodeURIComponent(orderId)}`);
      const order = data.order || data;
      const status = String(order.status || data.status || data.payment_status || "").toLowerCase();
      if (["paid", "success", "active", "succeeded"].includes(status)) {
        clearInterval(timer);
        showToast("Оплата получена");
        await loadData();
      } else if (["failed", "cancelled", "canceled", "expired"].includes(status)) {
        clearInterval(timer);
        showToast("Оплата не прошла");
      }
    } catch (err) {
      if (tries >= 20) clearInterval(timer);
    }
    if (tries >= 30) clearInterval(timer);
  }, 3000);
}

async function checkout(planKey, providerId) {
  providerId = normalizeProviderId(providerId);
  if (!providerId || providerId === "undefined") return showToast("Способ оплаты не выбран");
  showToast("Создание заказа...");
  try {
    const payload = withTelegramUser({
      plan: planKey,
      provider: providerId || "auto",
      auto_renew: Boolean($("subscriptionAutopayToggle")?.checked && !$("subscriptionAutopayToggle")?.disabled && state.billingCapabilities?.autopay_available)
    });
    const res = await apiRequest("/api/billing/create-order", {
      method: "POST",
      body: JSON.stringify(payload)
    }).catch(async () => {
      return await apiRequest("/api/billing/checkout", {
        method: "POST",
        body: JSON.stringify(payload)
      });
    });

    const link = res.payment_url || res.invoice_url || res.invoice_link || res.url;
    const orderId = res.order_id || res.id;
    if (link) openPaymentLink(link, res.provider || providerId);
    if (orderId) pollOrderStatus(orderId);
    if (!link && !orderId) showToast("Заказ создан");
  } catch (err) {
    showToast(friendlyError(err, "Не удалось создать оплату"));
  }
}

function pollCreditPackOrder(orderId) {
  if (!orderId) return;
  let tries = 0;
  const timer = setInterval(async () => {
    tries += 1;
    try {
      const data = await apiRequest(`/api/credits/packs/order/${encodeURIComponent(orderId)}`);
      const order = data.order || data;
      const status = String(order.status || data.status || "").toLowerCase();
      if (["paid", "success", "succeeded"].includes(status)) {
        clearInterval(timer);
        showToast("Кредиты начислены");
        await loadData();
      } else if (["failed", "cancelled", "canceled", "expired"].includes(status)) {
        clearInterval(timer);
        showToast("Оплата пакета не прошла");
      }
    } catch (err) {
      if (tries >= 20) clearInterval(timer);
    }
    if (tries >= 30) clearInterval(timer);
  }, 3000);
}

function renderCreditPacks() {
  const container = $("creditPackList");
  if (!container) return;
  container.innerHTML = state.creditPacks.map(p => `
    <div class="credit-pack">
      <div class="info">
        <h5>${escapeHTML(p.title)}</h5>
        <p>${escapeHTML(p.description || "Разовое пополнение")}</p>
      </div>
      <button class="price-btn" data-pack="${escapeHTML(p.id)}">${escapeHTML(p.price_text)}</button>
    </div>
  `).join("");
}


function renderOrganizations() {
  const list = $("organizationList");
  const invites = $("organizationInviteList");
  if (!list) return;
  const org = state.organizations?.active || state.organizations?.current || state.organizations?.owned?.[0] || state.organizations?.memberships?.[0] || null;
  const members = Array.isArray(state.organizationMembers) ? state.organizationMembers : [];

  if (!org) {
    setText("organizationNameLabel", "Организация не создана");
    setText("organizationMetaLabel", "Создайте компанию и пригласите участников");
    list.innerHTML = `
      <div class="settings-row org-create-row">
        <span><b>Создать организацию</b><small>Название можно изменить позже.</small></span>
      </div>
      <div class="settings-row org-create-form">
        <input id="organizationCreateTitle" type="text" placeholder="Название организации" value="Моя организация">
        <button id="createOrganizationBtn" class="plain-btn" type="button">Создать</button>
      </div>`;
    if (invites) { invites.style.display = "none"; invites.innerHTML = ""; }
    return;
  }

  const orgName = org?.name || org?.title || "Организация";
  const orgRole = org?.role || (String(org.owner_telegram_user_id || "") === String(state.user?.telegram_id || state.user?.id || "") ? "owner" : "member");
  setText("organizationNameLabel", orgName);
  setText("organizationMetaLabel", `${orgRole} • ${members.length || 1} участник`);

  if (!members.length) {
    list.innerHTML = `<div class="settings-row"><span><b>Участников пока нет</b><small>Пригласите сотрудника по Telegram username.</small></span></div>`;
  } else {
    list.innerHTML = members.map(m => {
      const name = m.first_name || m.name || m.username || "Участник";
      const username = m.username ? `@${m.username}` : `ID: ${m.telegram_id || m.telegram_user_id || "—"}`;
      const role = m.role || "member";
      return `<div class="settings-row"><span><b>${escapeHTML(name)}</b><small>${escapeHTML(username)}</small></span><em>${escapeHTML(role)}</em></div>`;
    }).join("");
  }

  const pending = state.organizations?.pending_invites || [];
  if (invites) {
    invites.style.display = pending.length ? "block" : "none";
    invites.innerHTML = pending.map(inv => `<div class="settings-row"><span><b>${escapeHTML(inv.username || inv.invited_username || "Приглашение")}</b><small>Ожидает подтверждения</small></span></div>`).join("");
  }
}


async function loadOrganizations() {
  try {
    const data = await apiRequest("/api/organizations");
    state.organizations = { ...state.organizations, ...(data.organizations || data) };
  } catch (err) { }
  try {
    const current = await apiRequest("/api/organizations/current");
    state.organizations.active = current.organization || current.active || current.current || current;
  } catch (err) { }
  try {
    const members = await apiRequest("/api/organizations/members");
    state.organizationMembers = Array.isArray(members) ? members : (members.members || members.items || []);
  } catch (err) { state.organizationMembers = []; }
  try {
    const inv = await apiRequest("/api/organizations/invites/pending");
    state.organizations.pending_invites = Array.isArray(inv) ? inv : (inv.invites || inv.pending_invites || []);
  } catch (err) { }
  renderOrganizations();
}

async function inviteOrganizationMember() {
  const input = $("organizationInviteUsername");
  const username = input?.value.trim().replace(/^@/, "");
  if (!username) return showToast("Введите Telegram username");
  try {
    await apiRequest("/api/organizations/invite", {
      method: "POST",
      body: JSON.stringify(withTelegramUser({ username }))
    });
    input.value = "";
    showToast("Приглашение отправлено");
    await loadOrganizations();
  } catch (err) { showToast(err.message || "Не удалось отправить приглашение"); }
}

async function loadNotificationPrefs() {
  try {
    const data = await apiRequest("/api/notifications/preferences");
    const prefs = data.preferences || data || {};
    const setChecked = (id, value) => { const el = $(id); if (el) el.checked = Boolean(value); };
    setChecked("notifyLimitToggle", prefs.low_credits ?? true);
    setChecked("notifyBillingToggle", prefs.subscription_reminders ?? true);
    setChecked("notifyProductToggle", prefs.product_updates ?? false);
  } catch (err) { }
}

async function saveNotificationPrefs() {
  try {
    await apiRequest("/api/notifications/preferences", {
      method: "POST",
      body: JSON.stringify({
        low_credits: Boolean($("notifyLimitToggle")?.checked),
        subscription_reminders: Boolean($("notifyBillingToggle")?.checked),
        product_updates: Boolean($("notifyProductToggle")?.checked)
      })
    });
    showToast("Уведомления сохранены");
  } catch (err) { showToast(friendlyError(err, "Не удалось сохранить уведомления")); }
}

async function saveAutopaySettings() {
  const toggle = $("subscriptionAutopayToggle");
  const enabled = Boolean(toggle?.checked);
  if (enabled && !state.billingCapabilities?.autopay_available) {
    if (toggle) toggle.checked = false;
    return showToast("Автопродление временно недоступно. Оплата тарифа работает без него.");
  }
  const activePlan = document.querySelector(".plan-card.active")?.dataset.plan || state.user?.plan || "go";
  try {
    await apiRequest("/api/billing/autopay", {
      method: "POST",
      body: JSON.stringify({ enabled, plan: activePlan === "free" ? "go" : activePlan, provider: "yookassa" })
    });
    showToast(enabled ? "Автопродление включено" : "Автопродление выключено");
  } catch (err) { showToast(friendlyError(err, "Не удалось изменить автопродление")); }
}

async function createOrganizationFromUI() {
  const title = ($("organizationCreateTitle")?.value || "Моя организация").trim();
  try {
    await apiRequest("/api/organizations", { method: "POST", body: JSON.stringify({ title }) });
    showToast("Организация создана");
    await loadOrganizations();
  } catch (err) { showToast(friendlyError(err, "Не удалось создать организацию")); }
}


function supportStatusLabel(status) {
  const map = {
    open: "Открыт",
    waiting_support: "Ждёт поддержки",
    answered: "Есть ответ",
    closed: "Закрыт"
  };
  return map[String(status || "open")] || "Открыт";
}

function supportCategoryLabel(category) {
  const map = { bug: "Баг", payment: "Оплата", account: "Аккаунт", idea: "Идея", other: "Другое" };
  return map[String(category || "bug")] || "Другое";
}

function renderSupportTickets() {
  const list = $("supportTicketList");
  if (!list) return;
  const tickets = state.supportTickets || [];
  if (!tickets.length) {
    list.innerHTML = `<div class="settings-row"><span><b>История поддержки пустая</b><small>Создайте обращение, и ответы появятся здесь.</small></span></div>`;
    return;
  }
  list.innerHTML = tickets.map(t => {
    const active = String(t.id) === String(state.activeSupportTicketId);
    const preview = t.last_message || t.subject || "Обращение";
    return `
      <button type="button" class="settings-row support-ticket-row ${active ? 'active' : ''}" data-ticket-id="${escapeHTML(t.id)}">
        <span class="row-icon"><span data-icon="message"></span></span>
        <span><b>${escapeHTML(t.subject || 'Обращение')}</b><small>${escapeHTML(supportStatusLabel(t.status))} • ${escapeHTML(supportCategoryLabel(t.category))} • ${escapeHTML(String(preview).slice(0, 90))}</small></span>
        <span class="chevron">›</span>
      </button>`;
  }).join("");
  injectIcons(list);
}

function renderSupportMessages() {
  const box = $("supportChatMessages");
  if (!box) return;
  const messages = state.supportMessages || [];
  if (!state.activeSupportTicketId) {
    box.innerHTML = `<div class="support-empty"><b>Выберите тикет или создайте новый</b><small>Здесь будет отдельная история чата с поддержкой.</small></div>`;
    return;
  }
  if (!messages.length) {
    box.innerHTML = `<div class="support-empty"><b>Сообщений пока нет</b><small>Мы уже получили обращение. Ответ появится в этом диалоге.</small></div>`;
    return;
  }
  box.innerHTML = messages.map(m => {
    const isUser = String(m.author_type || '') === 'user';
    const author = isUser ? 'Вы' : (m.author_name || 'Поддержка');
    return `
      <div class="support-msg ${isUser ? 'user' : 'support'}">
        <div class="support-msg-author">${escapeHTML(author)}</div>
        <div class="md-content">${renderMarkdown(m.content || '')}</div>
      </div>`;
  }).join("");
  box.scrollTop = box.scrollHeight;
}

async function loadSupport() {
  try {
    const data = await apiRequest("/api/support/tickets");
    state.supportTickets = Array.isArray(data.items) ? data.items : [];
    if (!state.activeSupportTicketId && state.supportTickets.length) state.activeSupportTicketId = state.supportTickets[0].id;
    renderSupportTickets();
    if (state.activeSupportTicketId) await openSupportTicket(state.activeSupportTicketId, { silent: true });
    else renderSupportMessages();
  } catch (err) {
    renderSupportTickets();
    renderSupportMessages();
  }
}

async function openSupportTicket(ticketId, options = {}) {
  if (!ticketId) return;
  state.activeSupportTicketId = ticketId;
  renderSupportTickets();
  try {
    const data = await apiRequest(`/api/support/tickets/${encodeURIComponent(ticketId)}`);
    state.supportMessages = Array.isArray(data.messages) ? data.messages : [];
    renderSupportMessages();
    if (!options.silent) showToast("Тикет открыт");
  } catch (err) {
    if (!options.silent) showToast(friendlyError(err, "Не удалось открыть тикет"));
  }
}

async function submitSupportTicket() {
  const subject = ($("supportSubjectInput")?.value || "").trim();
  const message = ($("supportMessageInput")?.value || "").trim();
  const category = ($("supportCategorySelect")?.value || "bug").trim();
  if (message.length < 3) return showToast("Опишите проблему чуть подробнее");
  try {
    const data = await apiRequest("/api/support/tickets", {
      method: "POST",
      body: JSON.stringify({ subject, message, category })
    });
    $("supportSubjectInput").value = "";
    $("supportMessageInput").value = "";
    state.activeSupportTicketId = data.ticket?.id || null;
    showToast(data.group_sent ? "Обращение отправлено поддержке" : "Обращение сохранено. Мы скоро ответим");
    await loadSupport();
  } catch (err) { showToast(friendlyError(err, "Не удалось отправить обращение")); }
}

async function submitSupportMessage() {
  const input = $("supportReplyInput");
  const message = (input?.value || "").trim();
  if (!state.activeSupportTicketId) return showToast("Сначала выберите тикет");
  if (!message) return showToast("Введите сообщение");
  try {
    await apiRequest(`/api/support/tickets/${encodeURIComponent(state.activeSupportTicketId)}/messages`, {
      method: "POST",
      body: JSON.stringify({ message })
    });
    input.value = "";
    await openSupportTicket(state.activeSupportTicketId, { silent: true });
    showToast("Сообщение отправлено");
  } catch (err) { showToast(friendlyError(err, "Не удалось отправить сообщение")); }
}

async function closeSupportTicket() {
  if (!state.activeSupportTicketId) return showToast("Сначала выберите тикет");
  try {
    await apiRequest(`/api/support/tickets/${encodeURIComponent(state.activeSupportTicketId)}/status`, {
      method: "POST",
      body: JSON.stringify({ status: "closed" })
    });
    showToast("Тикет закрыт");
    await loadSupport();
  } catch (err) { showToast(friendlyError(err, "Не удалось закрыть тикет")); }
}

// Data Loaders
async function loadData() {
  try {
    const userData = await apiRequest("/api/me");
    state.user = userData.user || userData || {};
  } catch (err) { console.warn('Telegram profile load failed', err); state.user = buildTelegramFallbackUser(); }

  updateProfileUI();

  try {
    const tData = await apiRequest("/api/tools");
    state.tools = Array.isArray(tData) ? tData : (tData.tools || getFallbackTools());
  } catch { state.tools = getFallbackTools(); }
  renderQuickActions();
  renderTools();

  try {
    const hData = await apiRequest("/api/history");
    state.history = normalizeHistoryData(hData);
  } catch { state.history = []; }
  renderHistory();

  try {
    const pData = await apiRequest("/api/billing/plans");
    const raw = pData?.plans || pData || [];
    let backendPlans = [];
    if (Array.isArray(raw)) backendPlans = raw;
    else if (raw && typeof raw === "object") backendPlans = Object.entries(raw).map(([key, plan]) => ({ key, ...plan }));
    const globalProviders = Array.isArray(pData?.providers) ? pData.providers : [];
    state.billingCapabilities = pData?.capabilities || {
      autopay_available: globalProviders.some(p => normalizeProviderId(p.id || p.key) === "yookassa" && p.recurring_available),
      yookassa_recurring_available: globalProviders.some(p => normalizeProviderId(p.id || p.key) === "yookassa" && p.recurring_available)
    };
    const fallbackByKey = Object.fromEntries(getFallbackPlans().map(p => [p.key, p]));
    state.providers = globalProviders;
    state.plans = (backendPlans.length ? backendPlans : getFallbackPlans()).map(plan => {
      const key = String(plan.key || plan.id || plan.slug || plan.title || "").toLowerCase();
      const fallback = fallbackByKey[key] || {};
      return {
        ...fallback,
        ...plan,
        key,
        title: plan.title || plan.name || fallback.title || key,
        description: plan.description || plan.subtitle || fallback.description || "",
        price_text: getPlanPriceText(key),
        price: getPlanPriceText(key),
        providers: key === "free" ? [] : (Array.isArray(plan.providers) && plan.providers.length ? plan.providers : globalProviders)
      };
    });
  } catch { state.providers = []; state.billingCapabilities = { autopay_available: false, yookassa_recurring_available: false }; state.plans = getFallbackPlans(); }
  renderSubscription();

  try {
    const cData = await apiRequest("/api/credits/packs");
    state.creditPacks = Array.isArray(cData?.packs) ? cData.packs : getFallbackCreditPacks();
  } catch { state.creditPacks = getFallbackCreditPacks(); }
  renderCreditPacks();

  await loadOrganizations();
  await loadNotificationPrefs();
  await loadSupport();
}

// Event Bindings
function bindEvents() {
  // Navigation
  document.querySelectorAll(".nav-item").forEach(b => {
    b.addEventListener("click", () => switchView(b.dataset.target));
  });

  // Profile Tabs
  document.querySelectorAll(".mobile-tab-link, .rail-link, .profile-hero-card[data-pane]").forEach(link => {
    link.addEventListener("click", () => switchProfilePane(link.dataset.pane));
  });
  $("headerProfileBtn")?.addEventListener("click", () => switchView("profile"));
  document.querySelectorAll("[data-profile-back]").forEach(btn => {
    btn.addEventListener("click", closeProfilePane);
  });

  // Chat
  const chatInput = $("homeChatInput");
  if (chatInput) {
    chatInput.addEventListener("input", autoResizeTextarea);
    chatInput.addEventListener("keydown", e => {
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleChatSend(); }
    });
  }
  $("homeChatSendBtn")?.addEventListener("click", handleChatSend);
  document.querySelectorAll(".composer-left-actions .icon-soft-btn, .voice-btn").forEach(btn => {
    btn.addEventListener("click", () => showToast("Функция скоро появится"));
  });
  document.querySelectorAll(".selector-dropdown-filter-btn").forEach(btn => {
    btn.addEventListener("click", () => showToast("Фильтры скоро появятся"));
  });
  document.querySelectorAll(".change-payment-method-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const plan = String(state.user?.plan || "go").toLowerCase() === "free" ? "go" : String(state.user?.plan || "go").toLowerCase();
      selectPlan(plan);
    });
  });

  // Quick actions to chat
  $("quickStrip")?.addEventListener("click", e => {
    const btn = e.target.closest(".quick-pill");
    if (btn && chatInput) {
      chatInput.value = btn.dataset.prompt;
      chatInput.focus();
      autoResizeTextarea();
    }
  });

  // Tools to chat
  $("toolsGrid")?.addEventListener("click", e => {
    const card = e.target.closest(".tool-card");
    if (card && chatInput) {
      switchView("home");
      chatInput.value = card.dataset.prompt;
      chatInput.focus();
      autoResizeTextarea();
    }
  });

  // Tools Search
  $("toolsSearchInput")?.addEventListener("input", renderTools);

  // History Search & Filters
  $("historySearchInput")?.addEventListener("input", renderHistory);
  $("historySearchInputMobile")?.addEventListener("input", renderHistory);
  $("historyFilters")?.addEventListener("click", e => {
    const chip = e.target.closest(".chip");
    if (chip) {
      document.querySelectorAll("#historyFilters .chip").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      state.historyFilter = chip.dataset.filter;
      renderHistory();
    }
  });

  // Subscription clicks
  $("subscriptionPlanList")?.addEventListener("click", e => {
    const card = e.target.closest(".plan-card");
    if (card) selectPlan(card.dataset.plan);
  });
  $("subscriptionPaymentProviders")?.addEventListener("click", e => {
    const btn = e.target.closest(".provider-btn");
    if (!btn) return;
    if (btn.disabled || btn.classList.contains("disabled")) return showToast("Этот способ оплаты скоро появится");
    checkout(btn.dataset.plan, btn.dataset.provider);
  });
  $("creditPackList")?.addEventListener("click", e => {
    const btn = e.target.closest(".price-btn");
    if (btn) {
      showToast("Создание оплаты...");
      apiRequest("/api/credits/packs/order", {
        method: "POST",
        body: JSON.stringify(withTelegramUser({ pack_id: btn.dataset.pack, provider: "yookassa" }))
      })
        .then(res => {
          const link = res.payment_url || res.invoice_url || res.invoice_link || res.url;
          const orderId = res.order_id || res.id || res.order?.id;
          if (link) openExternal(link);
          if (orderId) pollCreditPackOrder(orderId);
          if (!link && !orderId) showToast("Заказ создан");
        })
        .catch(err => showToast(friendlyError(err, "Не удалось создать оплату")));
    }
  });

  $("inviteOrganizationBtn")?.addEventListener("click", inviteOrganizationMember);

  // Profile actions
  $("copyTgIdBtn")?.addEventListener("click", () => {
    navigator.clipboard.writeText(state.user?.telegram_id || "").then(() => showToast("ID скопирован"));
  });

  $("saveProfileBtn")?.addEventListener("click", async () => {
    const profileText = $("profileBusinessDescription")?.value.trim();
    const company = $("profileCompanyName")?.value.trim();
    try {
      await apiRequest("/api/profile", {
        method: "POST",
        body: JSON.stringify(withTelegramUser({ business_profile: profileText, company_name: company }))
      });
      showToast("Контекст сохранён");
    } catch { showToast("Сохранено локально"); }
  });

  $("submitAppFeedbackBtn")?.addEventListener("click", async () => {
    const val = $("appFeedbackText")?.value.trim();
    if (!val) return showToast("Введите текст отзыва");
    try {
      await apiRequest("/api/feedback", { method: "POST", body: JSON.stringify({ source_type: "mini_app", source_id: "profile_about", rating: 0, message: val }) });
      $("appFeedbackText").value = "";
      showToast("Спасибо за отзыв!");
    } catch (err) { showToast(friendlyError(err, "Не удалось отправить отзыв")); }
  });


  $("supportTicketList")?.addEventListener("click", e => {
    const row = e.target.closest(".support-ticket-row");
    if (row) openSupportTicket(row.dataset.ticketId);
  });
  $("sendSupportTicketBtn")?.addEventListener("click", submitSupportTicket);
  $("sendSupportReplyBtn")?.addEventListener("click", submitSupportMessage);
  $("closeSupportTicketBtn")?.addEventListener("click", closeSupportTicket);
  $("supportReplyInput")?.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submitSupportMessage(); }
  });

  $("saveNotificationsBtn")?.addEventListener("click", saveNotificationPrefs);
  $("subscriptionAutopayToggle")?.addEventListener("change", saveAutopaySettings);
  $("exportHistoryBtn")?.addEventListener("click", () => openExternal("/api/export/history.txt"));
  document.querySelector("[data-copy-inn]")?.addEventListener("click", () => {
    navigator.clipboard.writeText("713304603876").then(() => showToast("ИНН скопирован"));
  });
  document.addEventListener("click", e => {
    const btn = e.target.closest("#createOrganizationBtn");
    if (btn) createOrganizationFromUI();
  });
}

function revealApp() {
  const app = $("appContainer");
  const loader = $("appPreloader");
  if (app) app.classList.add("loaded");
  if (loader) loader.classList.add("loaded");
}

async function boot() {
  try {
    injectIcons();
    initTelegramBridge();

    if (tg) {
      tg.ready?.();
      tg.expand?.();
      try {
        if (tg.setHeaderColor) tg.setHeaderColor("bg_color");
        if (tg.setBackgroundColor) tg.setBackgroundColor("bg_color");
      } catch (e) { }
    }

    bindEvents();
    await loadData();

    const params = new URLSearchParams(window.location.search || "");
    const returnedOrderId = params.get("order_id");
    const returnedCreditPackOrderId = params.get("credit_pack_order_id");
    if (params.get("credit_pack_return") && returnedCreditPackOrderId) {
      showToast("Проверяем оплату пакета...");
      pollCreditPackOrder(returnedCreditPackOrderId);
    } else if (params.get("payment_return") && returnedOrderId) {
      showToast("Проверяем оплату...");
      pollOrderStatus(returnedOrderId);
    }
  } catch (err) {
    console.error("FounderPilot boot error", err);
    state.user = state.user || { first_name: "Пользователь", telegram_id: null, plan: "Free" };
    state.tools = state.tools.length ? state.tools : getFallbackTools();
    state.plans = Array.isArray(state.plans) && state.plans.length ? state.plans : getFallbackPlans();
    state.creditPacks = state.creditPacks.length ? state.creditPacks : getFallbackCreditPacks();
    try { updateProfileUI(); renderQuickActions(); renderTools(); renderHistory(); renderSubscription(); renderCreditPacks(); } catch (e) { console.error("Fallback render error", e); }
    showToast("Интерфейс загружен в резервном режиме");
  } finally {
    revealApp();
  }
}


/* === Final functional polish layer === */
Object.assign(state, {
  activeConversationId: null,
  notifications: [],
  unreadNotifications: 0,
  subscriptionTab: 'plans',
  supportTab: 'new',
  appMeta: {}
});

Object.assign(iconPaths, {
  home: '<path d="M4 10.5 12 4l8 6.5V20a1 1 0 0 1-1 1h-4v-6H9v6H5a1 1 0 0 1-1-1v-9.5Z"></path>',
  tools: '<path d="M4 5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V5Z"></path><path d="M14 5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1V5Z"></path><path d="M4 15a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-4Z"></path><path d="M14 15a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-4a1 1 0 0 1-1-1v-4Z"></path>',
  history: '<path d="M12 8v5l3 2"></path><path d="M21 12a9 9 0 1 1-2.64-6.36"></path><path d="M21 4v5h-5"></path>',
  user: '<circle cx="12" cy="8" r="4"></circle><path d="M5 21a7 7 0 0 1 14 0"></path>',
  message: '<path d="M5 6.5A3.5 3.5 0 0 1 8.5 3h7A3.5 3.5 0 0 1 19 6.5v5A3.5 3.5 0 0 1 15.5 15H11l-5 4v-4.2A3.5 3.5 0 0 1 5 12.3V6.5Z"></path>',
  bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 8-3 8h18s-3-1-3-8"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path>',
  calendar: '<path d="M7 3v4"></path><path d="M17 3v4"></path><rect x="4" y="5" width="16" height="16" rx="2"></rect><path d="M4 10h16"></path>',
  coin: '<circle cx="12" cy="12" r="9"></circle><path d="M8 12h8"></path><path d="M12 8v8"></path>',
  bug: '<path d="M8 2l1.5 3"></path><path d="M16 2l-1.5 3"></path><rect x="7" y="7" width="10" height="12" rx="5"></rect><path d="M3 13h4"></path><path d="M17 13h4"></path><path d="M4 19l3-2"></path><path d="M20 19l-3-2"></path>',
  support: '<path d="M4 12a8 8 0 0 1 16 0v3a3 3 0 0 1-3 3h-2"></path><path d="M8 15h8"></path><path d="M15 18h-3a2 2 0 0 1-2-2"></path>',
  receipt: '<path d="M6 3h12v18l-3-2-3 2-3-2-3 2V3Z"></path><path d="M9 8h6"></path><path d="M9 12h6"></path><path d="M9 16h4"></path>'
});

function formatDateRu(value) {
  if (!value) return '—';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' });
}

function updateProfileUI() {
  const fallback = { first_name: 'Пользователь', username: '', telegram_id: '—', plan: 'Free', photo_url: '' };
  const rawUser = state.user || {};
  const u = { ...fallback, ...rawUser, telegram_id: rawUser.telegram_id || rawUser.id || rawUser.telegram_user_id || '—' };
  const planName = String(u.plan || 'Free').toLowerCase();
  const planNameUpper = planName.charAt(0).toUpperCase() + planName.slice(1);
  const subtitle = u.username ? `@${u.username}` : `Telegram ID: ${u.telegram_id || '—'}`;

  setText('homeGreeting', `Доброе утро, ${u.first_name || 'друг'}! 👋`);
  ['sidebarAvatar', 'headerUserAvatar', 'desktopTopAvatar', 'mobileHeaderAvatar', 'profileUserAvatar', 'profileUserAvatarLarge'].forEach(id => applyAvatar($(id), u));
  setText('sidebarUserName', u.first_name || 'Пользователь');
  setText('sidebarUserPlan', planNameUpper);
  setText('profileUserTitle', u.first_name || 'Пользователь');
  setText('profileUserTitleMirror', u.first_name || 'Пользователь');
  setText('profileUserTitleMirror2', u.first_name || 'Пользователь');
  setText('profileUserSubtitle', subtitle);
  setText('profileUserSubtitleMirror', subtitle);
  setText('profileUserSubtitleMirror2', subtitle);
  setText('profilePlanLabel', planNameUpper);
  setText('profilePlanLabelMirror', planNameUpper);

  const planPrice = getPlanPriceText(planName);
  setText('profilePlanPrice', planPrice);
  setText('profilePlanPriceMirror', planPrice);
  setText('subscriptionCurrentPlan', planNameUpper);
  setText('subscriptionCurrentPrice', planPrice || '0 ₽');
  setText('profileSubscriptionPlanTitle', planNameUpper);
  setText('profileSubscriptionPrice', planPrice || '0 ₽');

  const assignValue = (id, value) => { const el = $(id); if (!el) return; if ('value' in el) el.value = value; else el.textContent = value; };
  assignValue('profileNameValue', u.first_name || 'Пользователь');
  assignValue('profileUsernameValue', u.username ? `@${u.username}` : '—');
  assignValue('profileTelegramIdValue', u.telegram_id || '—');
  assignValue('profileRegistrationDateValue', formatDateRu(u.created_at || u.registration_date));
  assignValue('profileCompanyName', u.company_name || '');
  assignValue('profileBusinessDescription', u.business_profile || '');

  const remaining = Number(u.remaining_credits_today ?? u.remaining ?? u.credits ?? 0);
  if ($('desktopTopCreditsValue')) $('desktopTopCreditsValue').textContent = remaining ? remaining.toLocaleString('ru-RU') : '20';

  const isBusiness = planName === 'business';
  const teamNotice = $('teamBusinessNotice');
  if (teamNotice) teamNotice.style.display = isBusiness ? 'none' : 'block';
  if ($('teamActiveContent')) $('teamActiveContent').style.display = isBusiness ? 'block' : 'none';
}

function renderTools() {
  const container = $('toolsGrid');
  if (!container) return;
  const q = $('toolsSearchInput')?.value.toLowerCase().trim() || '';
  const source = (state.tools && state.tools.length ? state.tools : getFallbackTools());
  const filtered = source.filter(t => `${t.title || ''} ${t.description || ''}`.toLowerCase().includes(q));
  if (!filtered.length) {
    container.innerHTML = `<div class="empty-panel embedded-empty"><span data-icon="search"></span><h3>Ничего не найдено</h3><p>Лучше напишите задачу прямо в чат — он тоже умеет выбирать режим.</p></div>`;
    injectIcons(container); return;
  }
  container.innerHTML = filtered.map((t, idx) => `
    <button class="tool-card-modern tool-card" data-prompt="${escapeAttr(t.prompt_template || t.placeholder || t.description || '')}" style="--i:${idx}">
      <span class="tool-mini-icon"><span data-icon="${idx % 3 === 0 ? 'stars' : idx % 3 === 1 ? 'chart' : 'message'}"></span></span>
      <span class="tool-card-text"><b>${escapeHTML(t.title || 'Инструмент')}</b><small>${escapeHTML(t.description || 'Открыть в AI-чате')}</small></span>
      <span class="tool-open-label">В чат</span>
    </button>
  `).join('');
  injectIcons(container);
}

function normalizeHistoryData(data) {
  if (Array.isArray(data)) return data;
  const result = [];
  const pushItems = (items, type, fallbackTitle) => {
    (items || []).forEach(item => {
      if (!item || typeof item !== 'object') return;
      const created = item.updated_at || item.created_at || item.date || item.started_at || '';
      const title = item.title || item.tool_title || item.mode_title || item.subject || fallbackTitle;
      const message = item.preview || item.last_message || item.user_text || item.content || item.result_text || item.ai_answer || '';
      result.push({ ...item, type: item.type || type, title, message, date: item.date || formatHistoryDate(created), created_at: created });
    });
  };
  pushItems(data?.conversations, 'chat', 'Диалог');
  pushItems(data?.tool_runs, 'tools', 'Документ');
  pushItems(data?.saved, 'favorites', 'Сохранено');
  pushItems(data?.items || data?.history, 'tools', 'Запрос');
  const seen = new Set();
  return result.filter(item => {
    const key = `${item.type}:${item.id || item.conversation_id || item.source_id || item.title}:${item.created_at || item.date}`;
    if (seen.has(key)) return false;
    seen.add(key); return true;
  }).sort((a, b) => Date.parse(b.created_at || b.date || 0) - Date.parse(a.created_at || a.date || 0));
}

function renderHistory() {
  const container = $('historyList');
  const empty = $('historyEmptyState');
  if (!container || !empty) return;
  let items = state.history || [];
  const q = ($('historySearchInput')?.value || $('historySearchInputMobile')?.value || '').toLowerCase().trim();
  if (q) items = items.filter(i => `${i.title || ''} ${i.message || ''}`.toLowerCase().includes(q));
  if (state.historyFilter !== 'all') items = items.filter(i => i.type === state.historyFilter || i.mode === state.historyFilter);
  if (!items.length) { container.innerHTML = ''; empty.hidden = false; empty.style.display = 'block'; return; }
  empty.hidden = true; empty.style.display = 'none';
  container.innerHTML = items.map((h, idx) => {
    const isChat = h.type === 'chat';
    const isTool = h.type === 'tools';
    const id = h.id || h.conversation_id || '';
    const icon = isChat ? 'message' : isTool ? 'receipt' : 'save';
    const label = isChat ? 'AI-чат' : isTool ? 'Документ' : 'Сохранено';
    return `<button type="button" class="history-row-clean list-row" data-history-type="${escapeAttr(h.type)}" data-history-id="${escapeAttr(id)}" style="--i:${idx}">
      <span class="icon-box"><span data-icon="${icon}"></span></span>
      <span class="info"><h4>${escapeHTML(h.title || 'Диалог')}</h4><p>${escapeHTML(String(h.message || label).slice(0, 110))}</p></span>
      <span class="meta">${escapeHTML(h.date || h.created_at || 'Недавно')}</span>
    </button>`;
  }).join('');
  injectIcons(container);
}

async function openHistoryItem(type, id) {
  if (type !== 'chat' || !id) return showToast('Документ сохранён в истории');
  switchView('home');
  await loadConversationIntoHome(id, { silent: false });
}

function setSubscriptionTab(tab) {
  state.subscriptionTab = tab === 'credits' ? 'credits' : 'plans';
  document.querySelectorAll('[data-subscription-tab]').forEach(btn => btn.classList.toggle('active', btn.dataset.subscriptionTab === state.subscriptionTab));
  const page = document.querySelector('.subscription-page');
  if (page) page.classList.toggle('tab-credits', state.subscriptionTab === 'credits');
}

function renderSubscription() {
  const planList = $('subscriptionPlanList');
  if (!planList) return;
  const currentPlan = String(state.user?.plan || 'free').toLowerCase();
  const plans = Array.isArray(state.plans) ? state.plans : Object.values(state.plans || {});
  if ($('subscriptionCurrentPlan')) {
    const cp = plans.find(p => String(p.key).toLowerCase() === currentPlan) || plans[0];
    $('subscriptionCurrentPlan').textContent = cp ? (cp.title || cp.name || 'Free') : 'Free';
    if ($('subscriptionCurrentPrice')) $('subscriptionCurrentPrice').textContent = cp ? getPlanPriceText(cp.key || cp.id || currentPlan) : '0 ₽';
    renderCurrentPlanBenefits(cp);
  }
  planList.innerHTML = plans.map(p => {
    const key = String(p.key || p.id || p.slug || 'free').toLowerCase();
    const active = key === currentPlan;
    const benefits = planBenefitLines(p).slice(0, 2).map(item => `<span>${escapeHTML(item)}</span>`).join('');
    return `<button class="plan-card subscription-plan-row ${active ? 'active' : ''}" data-plan="${escapeHTML(key)}">
      <div class="plan-row-main"><h4>${escapeHTML(p.title || p.name || key)}</h4><small>${escapeHTML(p.description || p.subtitle || '')}</small><div class="plan-feature-chips">${benefits}</div></div>
      <div class="subscription-price">${escapeHTML(getPlanPriceText(key))}</div>
      <span class="check">✓</span>
    </button>`;
  }).join('');
  updateProfileUI(); renderAutopayControl(); setSubscriptionTab(state.subscriptionTab || 'plans');
}

function renderCreditPacks() {
  const container = $('creditPackList');
  if (!container) return;
  const packs = state.creditPacks && state.creditPacks.length ? state.creditPacks : getFallbackCreditPacks();
  container.innerHTML = packs.map((p, idx) => `<article class="credit-pack polished-pack" style="--i:${idx}">
    <div class="pack-head">
      <span class="tool-mini-icon"><span data-icon="coin"></span></span>
      <div class="pack-title"><h5>${escapeHTML(p.title)}</h5><p>${escapeHTML(p.description || 'Разовое пополнение баланса')}</p></div>
    </div>
    <button class="price-btn" data-pack="${escapeHTML(p.id)}">${escapeHTML(p.price_text)}</button>
  </article>`).join('');
  injectIcons(container);
}

function setSupportTab(tab) {
  state.supportTab = ['new', 'history', 'chat'].includes(tab) ? tab : 'new';
  document.querySelectorAll('[data-support-tab]').forEach(btn => btn.classList.toggle('active', btn.dataset.supportTab === state.supportTab));
  document.querySelectorAll('[data-support-panel]').forEach(panel => panel.classList.toggle('active', panel.dataset.supportPanel === state.supportTab));
}

function renderSupportTickets() {
  const list = $('supportTicketList');
  if (!list) return;
  const tickets = state.supportTickets || [];
  if (!tickets.length) {
    list.innerHTML = `<div class="support-empty clean"><b>История пустая</b><small>Создайте первое обращение — оно сохранится здесь.</small></div>`;
    return;
  }
  list.innerHTML = tickets.map((t, idx) => {
    const active = String(t.id) === String(state.activeSupportTicketId);
    const preview = t.last_message || t.subject || 'Обращение';
    return `<button type="button" class="support-ticket-card ${active ? 'active' : ''}" data-ticket-id="${escapeAttr(t.id)}" style="--i:${idx}">
      <span class="support-ticket-icon"><span data-icon="${t.category === 'payment' ? 'credit-card' : t.category === 'bug' ? 'bug' : 'support'}"></span></span>
      <span class="support-ticket-main"><b>${escapeHTML(t.subject || 'Обращение')}</b><small>${escapeHTML(supportStatusLabel(t.status))} • ${escapeHTML(supportCategoryLabel(t.category))}</small><em>${escapeHTML(String(preview).slice(0, 95))}</em></span>
    </button>`;
  }).join(''); injectIcons(list);
}

function renderSupportMessages() {
  const box = $('supportChatMessages');
  if (!box) return;
  const messages = state.supportMessages || [];
  if (!state.activeSupportTicketId) { box.innerHTML = `<div class="support-empty clean"><b>Выберите обращение</b><small>Откройте обращение из истории, чтобы продолжить диалог.</small></div>`; return; }
  if (!messages.length) { box.innerHTML = `<div class="support-empty clean"><b>Сообщений пока нет</b><small>Мы уже получили обращение. Ответ появится в этом диалоге.</small></div>`; return; }
  box.innerHTML = messages.map(m => {
    const isUser = String(m.author_type || '') === 'user';
    const author = isUser ? 'Вы' : (m.author_name || 'Поддержка');
    return `<div class="support-msg ${isUser ? 'user' : 'support'}"><div class="support-msg-author">${escapeHTML(author)}</div><div class="md-content">${renderMarkdown(m.content || '')}</div></div>`;
  }).join('');
  box.scrollTop = box.scrollHeight;
}

async function openSupportTicket(ticketId, options = {}) {
  if (!ticketId) return;
  state.activeSupportTicketId = ticketId;
  renderSupportTickets();
  try {
    const data = await apiRequest(`/api/support/tickets/${encodeURIComponent(ticketId)}`);
    state.supportMessages = Array.isArray(data.messages) ? data.messages : [];
    renderSupportMessages();
    if (!options.silent) setSupportTab('chat');
  } catch (err) { if (!options.silent) showToast(friendlyError(err, 'Не удалось открыть тикет')); }
}

async function loadNotifications() {
  try {
    const data = await apiRequest('/api/notifications');
    state.notifications = Array.isArray(data.items) ? data.items : [];
    state.unreadNotifications = Number(data.unread_count || 0);
  } catch (err) { state.notifications = []; state.unreadNotifications = 0; }
  renderNotifications();
}

function renderNotifications() {
  const box = $('notificationFeed');
  if (!box) return;
  const items = state.notifications || [];
  if (!items.length) { box.innerHTML = `<div class="support-empty clean"><b>Пока тихо</b><small>Платежи, ответы поддержки и важные события появятся здесь.</small></div>`; return; }
  box.innerHTML = items.map((n, idx) => `<div class="notification-item ${n.read_at ? '' : 'unread'}" style="--i:${idx}">
    <span class="notification-dot"></span>
    <span><b>${escapeHTML(n.title || 'Уведомление')}</b><small>${escapeHTML(n.body || '')}</small><em>${escapeHTML(formatHistoryDate(n.created_at))}</em></span>
  </div>`).join('');
}

async function markNotificationsRead() {
  try { await apiRequest('/api/notifications/read', { method: 'POST', body: JSON.stringify({}) }); await loadNotifications(); showToast('Уведомления прочитаны'); }
  catch (err) { showToast(friendlyError(err, 'Не удалось обновить уведомления')); }
}

async function loadAppMeta() {
  try {
    const data = await apiRequest('/api/app/meta');
    state.appMeta = data || {};
    setText('appVersionValue', data.version || '1.3.0');
    setText('appUpdatedAtValue', formatDateRu(data.updated_at));
    setText('appSupportValue', data.support || 'FounderPilot Support');
  } catch (err) {
    setText('appVersionValue', '1.3.0');
    setText('appUpdatedAtValue', '29 мая 2026');
  }
}

async function loadData() {
  try { const userData = await apiRequest('/api/me'); state.user = userData.user || userData || {}; }
  catch (err) { console.warn('Telegram profile load failed', err); state.user = buildTelegramFallbackUser(); }
  updateProfileUI();
  try { const tData = await apiRequest('/api/tools'); state.tools = Array.isArray(tData) ? tData : (tData.tools || getFallbackTools()); }
  catch { state.tools = getFallbackTools(); }
  renderTools();
  try { const hData = await apiRequest('/api/history'); state.history = normalizeHistoryData(hData); }
  catch { state.history = []; }
  renderHistory();
  try {
    const bData = await apiRequest('/api/billing/plans');
    const backendPlans = Array.isArray(bData.plans) ? bData.plans : Object.values(bData.plans || {});
    const globalProviders = Array.isArray(bData.providers) ? bData.providers : [];
    state.billingCapabilities = bData.capabilities || { autopay_available: false, yookassa_recurring_available: false };
    const fallbackByKey = Object.fromEntries(getFallbackPlans().map(p => [p.key, p]));
    state.providers = globalProviders;
    state.plans = (backendPlans.length ? backendPlans : getFallbackPlans()).map(plan => {
      const key = String(plan.key || plan.id || plan.slug || plan.title || '').toLowerCase();
      const fallback = fallbackByKey[key] || {};
      return { ...fallback, ...plan, key, title: plan.title || plan.name || fallback.title || key, description: plan.description || plan.subtitle || fallback.description || '', price_text: getPlanPriceText(key), price: getPlanPriceText(key), providers: key === 'free' ? [] : (Array.isArray(plan.providers) && plan.providers.length ? plan.providers : globalProviders) };
    });
  } catch { state.providers = []; state.billingCapabilities = { autopay_available: false, yookassa_recurring_available: false }; state.plans = getFallbackPlans(); }
  renderSubscription();
  try { const cData = await apiRequest('/api/credits/packs'); state.creditPacks = Array.isArray(cData?.packs) ? cData.packs : getFallbackCreditPacks(); }
  catch { state.creditPacks = getFallbackCreditPacks(); }
  renderCreditPacks();
  await loadOrganizations(); await loadNotificationPrefs(); await loadNotifications(); await loadSupport(); await loadAppMeta();
  await restoreLastConversation();
}

async function handleChatSend() {
  const input = $('homeChatInput'); const text = input?.value.trim();
  if (!text || state.isSending) return;
  state.isSending = true; $('homeChatSendBtn').disabled = true; input.value = ''; autoResizeTextarea();
  appendMessage('user', text); const sysId = `sys_${Date.now()}`; appendMessage('system', 'FounderPilot готовит ответ...', sysId);
  try {
    // Create the conversation before the AI request. If the user closes the Mini App
    // while the model is answering, the dialogue id is already known and can be restored.
    await ensureActiveConversation();
    const payload = withTelegramUser({ message: text, text, mode: 'chat', conversation_id: state.activeConversationId || null });
    const res = await apiTry('/api/chat', '/api/ask', { method: 'POST', body: JSON.stringify(payload) });
    $(sysId)?.remove(); const answer = res.answer || res.response || res.result || res.text || 'Аналитический модуль вернул пустой результат.';
    if (res.conversation_id) saveActiveConversationId(res.conversation_id);
    appendMessage('bot', answer);
    try { const hData = await apiRequest('/api/history'); state.history = normalizeHistoryData(hData); renderHistory(); } catch {}
  } catch (err) { const sys = $(sysId); if (sys) sys.textContent = 'Ошибка: ' + err.message; }
  finally { state.isSending = false; autoResizeTextarea(); }
}

function bindPolishEvents() {
  if (window.__fpPolishBound) {
    setSubscriptionTab(state.subscriptionTab || 'plans');
    setSupportTab(state.supportTab || 'new');
    return;
  }
  window.__fpPolishBound = true;
  $('subscriptionTabs')?.addEventListener('click', e => { const btn = e.target.closest('[data-subscription-tab]'); if (btn) setSubscriptionTab(btn.dataset.subscriptionTab); });
  $('supportTabs')?.addEventListener('click', e => { const btn = e.target.closest('[data-support-tab]'); if (btn) setSupportTab(btn.dataset.supportTab); });
  $('historyList')?.addEventListener('click', e => { const row = e.target.closest('[data-history-type]'); if (row) openHistoryItem(row.dataset.historyType, row.dataset.historyId); });
  $('markNotificationsReadBtn')?.addEventListener('click', markNotificationsRead);
  document.querySelectorAll('.top-bell-btn').forEach(btn => btn.addEventListener('click', e => { e.preventDefault(); switchView('profile'); switchProfilePane('settings'); loadNotifications(); }));
  setSubscriptionTab(state.subscriptionTab || 'plans'); setSupportTab(state.supportTab || 'new');
}

const __originalBoot = boot;
boot = async function polishedBoot() {
  try { bindPolishEvents(); } catch (e) { console.warn('polish bind failed', e); }
  await __originalBoot();
  try { bindPolishEvents(); setSubscriptionTab(state.subscriptionTab || 'plans'); setSupportTab(state.supportTab || 'new'); } catch (e) {}
};

// Safety timeout for loading state.
window.setTimeout(revealApp, 4500);
document.addEventListener("DOMContentLoaded", boot);
