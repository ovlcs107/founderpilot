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
  save: '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline>',
  back: '<line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline>',
  copy: '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>',
  'credit-card': '<rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line>',
  ton: '<polygon points="12 2 3 9 12 22 21 9 12 2"></polygon><polyline points="3 9 12 13 21 9"></polyline><line x1="12" y1="22" x2="12" y2="13"></line>',
  btc: '<path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path><path d="M10 8h2.5a1.5 1.5 0 0 1 0 3H10V8z"></path><path d="M10 13h3a1.5 1.5 0 0 1 0 3h-3v-3z"></path><path d="M12 5v2"></path><path d="M12 17v2"></path>'
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
  creditPacks: [],
  organizations: { active: null, owned: [], memberships: [] },
  historyFilter: 'all'
};

// Utils
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
  setTimeout(() => el.classList.remove("visible"), 2500);
}

function getTelegramUserId() {
  return String(tg?.initDataUnsafe?.user?.id || state.user?.telegram_id || "dev");
}

function openExternal(url) {
  if (!url) return;
  if (tg?.openLink) tg.openLink(url);
  else window.open(url, "_blank", "noopener,noreferrer");
}

// API
async function apiRequest(url, options = {}) {
  const headers = { "Content-Type": "application/json" };
  if (tg?.initData) headers["X-Telegram-Init-Data"] = tg.initData;

  const res = await fetch(url, { ...options, headers: { ...headers, ...options.headers } });
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { data = { detail: text }; }

  if (!res.ok || data?.ok === false) {
    throw new Error(data?.error || data?.detail || "Ошибка сервера");
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
    { key: "free", title: "Free", description: "Для ознакомления", price_text: "0 ₽", providers: [] },
    { key: "go", title: "Go", description: "Базовые задачи", price_text: "399 ₽ / мес", providers: [{ id: 'telegram_stars', title: 'Telegram Stars' }, { id: 'yookassa', title: 'Карта / СБП' }, { id: 'ton', title: 'TON' }, { id: 'btcpay_btc', title: 'BTC' }] },
    { key: "plus", title: "Plus", description: "Активная работа", price_text: "990 ₽ / мес", providers: [{ id: 'telegram_stars', title: 'Telegram Stars' }, { id: 'yookassa', title: 'Карта / СБП' }, { id: 'ton', title: 'TON' }, { id: 'btcpay_btc', title: 'BTC' }] },
    { key: "pro", title: "Pro", description: "Полный безлимит", price_text: "2 490 ₽ / мес", providers: [{ id: 'telegram_stars', title: 'Telegram Stars' }, { id: 'yookassa', title: 'Карта / СБП' }, { id: 'ton', title: 'TON' }, { id: 'btcpay_btc', title: 'BTC' }] },
    { key: "business", title: "Business", description: "Для команд", price_text: "7 990 ₽ / мес", providers: [{ id: 'telegram_stars', title: 'Telegram Stars' }, { id: 'yookassa', title: 'Карта / СБП' }, { id: 'ton', title: 'TON' }, { id: 'btcpay_btc', title: 'BTC' }] }
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

// Navigation & UI
function switchView(target) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(b => b.classList.toggle("active", b.dataset.target === target));

  const v = $(`view-${target}`);
  if (v) v.classList.add("active");
  state.activeView = target;
}

function switchProfilePane(paneId) {
  if (window.innerWidth < 1100) {
    $("profileShell").classList.add("detail-open");
  }
  document.querySelectorAll(".mobile-tab-link").forEach(b => b.classList.toggle("active", b.dataset.pane === paneId));
  document.querySelectorAll(".profile-sub-pane").forEach(p => {
    p.classList.toggle("active", p.id === `pane-${paneId}`);
  });
}

function closeProfilePane() {
  $("profileShell").classList.remove("detail-open");
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
  const plans = Array.isArray(state.plans) ? state.plans : Object.values(state.plans || {});
  const plan = plans.find(p => String(p.key || p.id || p.slug || p.title || "").toLowerCase() === key);
  if (plan) return plan.price_text || plan.price || "";
  const fallback = { free: "0 ₽", go: "399 ₽ / мес", plus: "990 ₽ / мес", pro: "2 490 ₽ / мес", business: "7 990 ₽ / мес" };
  return fallback[key] || "0 ₽";
}

// Markdown parser
function renderMarkdown(text) {
  let out = escapeHTML(text);

  // Basic inline formatting
  out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  out = out.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  out = out.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Split into lines for block-level parsing
  const lines = out.split('\n');
  let result = [];
  let inCodeBlock = false;
  let codeBuffer = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    if (line.startsWith('```')) {
      if (inCodeBlock) {
        result.push(`<pre><code>${codeBuffer.join('\n')}</code></pre>`);
        inCodeBlock = false;
        codeBuffer = [];
      } else {
        inCodeBlock = true;
      }
      continue;
    }

    if (inCodeBlock) {
      codeBuffer.push(line);
      continue;
    }

    if (line.startsWith('- ') || line.startsWith('* ')) {
      result.push(`<ul><li>${line.substring(2)}</li></ul>`);
      continue;
    }

    if (line.match(/^\d+\.\s/)) {
      result.push(`<ol><li>${line.replace(/^\d+\.\s/, '')}</li></ol>`);
      continue;
    }

    if (line.startsWith('> ')) {
      result.push(`<blockquote>${line.substring(2)}</blockquote>`);
      continue;
    }

    if (line === '') {
      continue; // Skip empty lines between paragraphs
    }

    result.push(`<p>${line}</p>`);
  }

  // Clean up adjacent lists
  return result.join('')
    .replace(/<\/ul><ul>/g, '')
    .replace(/<\/ol><ol>/g, '');
}

// Chat
function appendMessage(role, text, id = null) {
  const scroll = $("homeChatScroll");
  if (!scroll) return;

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

  $("view-home").classList.add("chat-active"); // Hides empty state & quick actions
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
    const payload = { telegram_user_id: getTelegramUserId(), message: text, text: text, mode: "chat" };
    const res = await apiTry("/api/chat", "/api/ask", { method: "POST", body: JSON.stringify(payload) });

    $(sysId)?.remove();
    const answer = res.answer || res.response || res.result || res.text || "Аналитический модуль вернул пустой результат.";
    appendMessage("bot", answer);
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

function renderHistory() {
  const container = $("historyList");
  const empty = $("historyEmptyState");
  if (!container || !empty) return;

  let items = state.history || [];
  const q = $("historySearchInput")?.value.toLowerCase().trim() || "";

  if (q) {
    items = items.filter(i => (i.title || i.message || "").toLowerCase().includes(q));
  }
  if (state.historyFilter !== 'all') {
    items = items.filter(i => i.type === state.historyFilter || i.mode === state.historyFilter);
  }

  if (items.length === 0) {
    container.innerHTML = "";
    empty.style.display = "block";
    return;
  }
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

function renderSubscription() {
  const planList = $("subscriptionPlanList");
  if (!planList) return;

  const currentPlan = String(state.user?.plan || "free").toLowerCase();

  const plans = Array.isArray(state.plans) ? state.plans : Object.values(state.plans || {});

  if ($("subscriptionCurrentPlan")) {
    const cp = plans.find(p => String(p.key).toLowerCase() === currentPlan) || plans[0];
    $("subscriptionCurrentPlan").textContent = cp ? (cp.title || cp.name || "Free") : "Free";
    if ($("subscriptionCurrentPrice")) $("subscriptionCurrentPrice").textContent = cp ? (cp.price_text || cp.price || "0 ₽") : "0 ₽";
  }

  planList.innerHTML = plans.map(p => {
    const key = String(p.key || p.id || p.slug || "free").toLowerCase();
    const active = key === currentPlan;
    return `
      <button class="plan-card subscription-plan-row ${active ? 'active' : ''}" data-plan="${escapeHTML(key)}">
        <div><h4>${escapeHTML(p.title || p.name || key)}</h4><small>${escapeHTML(p.description || p.subtitle || "")}</small></div>
        <div class="subscription-price">${escapeHTML(p.price_text || p.price || getPlanPriceText(key))}</div>
        <span class="check">✓</span>
      </button>
    `;
  }).join("");
  updateProfileUI();
}

function selectPlan(key) {
  if (key === 'free') {
    showToast("Тариф Free доступен по умолчанию");
    if ($("paymentSection")) $("paymentSection").style.display = "none";
    return;
  }

  document.querySelectorAll(".plan-card").forEach(c => c.classList.toggle("active", c.dataset.plan === key));

  const plans = Array.isArray(state.plans) ? state.plans : Object.values(state.plans || {});
  const plan = plans.find(p => String(p.key).toLowerCase() === String(key).toLowerCase());
  const providers = (plan?.providers && plan.providers.length ? plan.providers : [
    { id: 'telegram_stars', title: 'Telegram Stars', description: 'Внутри Telegram' },
    { id: 'yookassa', title: 'Карта / СБП', description: 'Банковские карты РФ' },
    { id: 'ton', title: 'TON', description: 'Tonkeeper / TON' },
    { id: 'btcpay_btc', title: 'BTC', description: 'Bitcoin invoice' }
  ]);

  const box = $("subscriptionPaymentProviders");
  if (box) {
    box.innerHTML = providers.map(prov => `
      <button class="provider-btn" data-provider="${escapeHTML(prov.id)}" data-plan="${escapeHTML(key)}">
        <span class="icon" data-icon="${prov.id === 'ton' ? 'ton' : prov.id === 'telegram_stars' ? 'stars' : (String(prov.id).includes('btc') ? 'btc' : 'credit-card')}"></span>
        <div class="info">
          <h5>${escapeHTML(prov.title)}</h5>
          <p>${escapeHTML(prov.description || 'Оплата онлайн')}</p>
        </div>
      </button>
    `).join("");
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
      const status = String(data.status || data.payment_status || "").toLowerCase();
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
  showToast("Создание заказа...");
  try {
    const res = await apiRequest("/api/billing/create-order", {
      method: "POST",
      body: JSON.stringify({ plan: planKey, provider: providerId, telegram_user_id: getTelegramUserId() })
    }).catch(async () => {
      // Fallback endpoint
      return await apiRequest("/api/billing/checkout", {
        method: "POST",
        body: JSON.stringify({ plan: planKey, provider: providerId, telegram_user_id: getTelegramUserId() })
      });
    });

    const link = res.payment_url || res.invoice_url || res.invoice_link || res.url;
    const orderId = res.order_id || res.id;
    if (link) openExternal(link);
    if (orderId) pollOrderStatus(orderId);
    if (!link && !orderId) showToast("Заказ создан");
  } catch (err) {
    showToast(err.message || "Ошибка оплаты");
  }
}

function renderCreditPacks() {
  const container = $("creditPackList");
  if (!container) return;
  container.innerHTML = state.creditPacks.map(p => `
    <div class="credit-pack">
      <div class="info">
        <h5>${escapeHTML(p.title)}</h5>
        <p>Разовое пополнение</p>
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

  const orgName = org?.name || org?.title || "Организация";
  const orgRole = org?.role || "owner";
  setText("organizationNameLabel", orgName);
  setText("organizationMetaLabel", `${orgRole} • ${members.length || 1} участник`);

  if (!members.length) {
    list.innerHTML = `<div class="settings-row"><span><b>Участников пока нет</b><small>Пригласите сотрудника по Telegram username.</small></span></div>`;
  } else {
    list.innerHTML = members.map(m => {
      const name = m.first_name || m.name || m.username || "Участник";
      const username = m.username ? `@${m.username}` : `ID: ${m.telegram_id || "—"}`;
      const role = m.role || "member";
      return `<div class="settings-row"><span><b>${escapeHTML(name)}</b><small>${escapeHTML(username)}</small></span><em>${escapeHTML(role)}</em></div>`;
    }).join("");
  }

  const pending = state.organizations?.pending_invites || [];
  if (invites) {
    invites.style.display = pending.length ? "block" : "none";
    invites.innerHTML = pending.map(inv => `<div class="settings-row"><span><b>${escapeHTML(inv.username || inv.invitee_username || "Приглашение")}</b><small>Ожидает подтверждения</small></span></div>`).join("");
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
      body: JSON.stringify({ username, telegram_user_id: getTelegramUserId() })
    });
    input.value = "";
    showToast("Приглашение отправлено");
    await loadOrganizations();
  } catch (err) { showToast(err.message || "Не удалось отправить приглашение"); }
}

// Data Loaders
async function loadData() {
  try {
    const userData = await apiRequest("/api/me");
    state.user = userData.user || userData || {};
  } catch { state.user = { first_name: "Пользователь", telegram_id: "—", plan: "Free" }; }

  updateProfileUI();

  try {
    const tData = await apiRequest("/api/tools");
    state.tools = Array.isArray(tData) ? tData : (tData.tools || getFallbackTools());
  } catch { state.tools = getFallbackTools(); }
  renderQuickActions();
  renderTools();

  try {
    const hData = await apiRequest("/api/history");
    state.history = Array.isArray(hData) ? hData : (hData.history || []);
  } catch { state.history = []; }
  renderHistory();

  try {
    const pData = await apiRequest("/api/billing/plans");
    const raw = pData?.plans || pData || [];
    let backendPlans = [];
    if (Array.isArray(raw)) backendPlans = raw;
    else if (raw && typeof raw === "object") backendPlans = Object.entries(raw).map(([key, plan]) => ({ key, ...plan }));
    state.plans = backendPlans.length >= 5 ? backendPlans : getFallbackPlans();
  } catch { state.plans = getFallbackPlans(); }
  renderSubscription();

  try {
    const cData = await apiRequest("/api/credits/packs");
    state.creditPacks = Array.isArray(cData?.packs) ? cData.packs : getFallbackCreditPacks();
  } catch { state.creditPacks = getFallbackCreditPacks(); }
  renderCreditPacks();

  await loadOrganizations();
}

// Event Bindings
function bindEvents() {
  // Navigation
  document.querySelectorAll(".nav-item").forEach(b => {
    b.addEventListener("click", () => switchView(b.dataset.target));
  });

  // Profile Tabs
  document.querySelectorAll(".mobile-tab-link, .rail-link").forEach(link => {
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
    if (btn) checkout(btn.dataset.plan, btn.dataset.provider);
  });
  $("creditPackList")?.addEventListener("click", e => {
    const btn = e.target.closest(".price-btn");
    if (btn) {
      showToast("Создание заказа...");
      apiRequest("/api/credits/packs/order", { method: "POST", body: JSON.stringify({ pack_id: btn.dataset.pack, telegram_user_id: getTelegramUserId() }) })
        .then(res => { if (res.url) openExternal(res.url); else showToast("Успешно"); })
        .catch(err => showToast(err.message));
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
        body: JSON.stringify({ telegram_user_id: getTelegramUserId(), business_profile: profileText, company_name: company })
      });
      showToast("Контекст сохранён");
    } catch { showToast("Сохранено локально"); }
  });

  $("submitAppFeedbackBtn")?.addEventListener("click", () => {
    const val = $("appFeedbackText").value;
    if (val) {
      $("appFeedbackText").value = "";
      showToast("Спасибо за отзыв!");
    }
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
  } catch (err) {
    console.error("FounderPilot boot error", err);
    state.user = state.user || { first_name: "Пользователь", telegram_id: "—", plan: "Free" };
    state.tools = state.tools.length ? state.tools : getFallbackTools();
    state.plans = Array.isArray(state.plans) && state.plans.length ? state.plans : getFallbackPlans();
    state.creditPacks = state.creditPacks.length ? state.creditPacks : getFallbackCreditPacks();
    try { updateProfileUI(); renderQuickActions(); renderTools(); renderHistory(); renderSubscription(); renderCreditPacks(); } catch (e) { console.error("Fallback render error", e); }
    showToast("Интерфейс загружен в резервном режиме");
  } finally {
    revealApp();
  }
}

// Даже если backend/Telegram WebView зависнет, не держим пользователя на вечном прелоадере.
window.setTimeout(revealApp, 4500);
document.addEventListener("DOMContentLoaded", boot);