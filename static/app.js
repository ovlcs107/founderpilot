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
  chevron: '<polyline points="9 18 15 12 9 6"/>',
  // Премиальная нативная звезда Telegram Stars
  tg_stars: '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
  // Чистый геометрический логотип TON
  ton: '<path d="M12 2L3 9l9 13 9-13L12 2zm0 4.5L17.5 10H6.5L12 6.5zM6.8 12h10.4l-5.2 7.5-5.2-7.5z"/>'
};

const state = {
  user: null,
  tools: [],
  plans: {},
  history: [],
  currentMode: "strategy",
  historyFilter: "all",
  activePlan: null,
  onboardingStep: 0,
  onboardingData: {},
  onboardingConfig: [
    {
      id: "role",
      title: "Кто вы?",
      options: [
        { key: "wb_seller", label: "Селлер Wildberries" },
        { key: "ozon_seller", label: "Селлер Ozon" },
        { key: "multi_seller", label: "Торгую на нескольких маркетплейсах" },
        { key: "beginner", label: "Только выбираю нишу" }
      ]
    },
    {
      id: "turnover",
      title: "Ваш текущий оборот",
      options: [
        { key: "zero", label: "Пока нет продаж" },
        { key: "up_to_100", label: "До 100 000 ₽ / мес" },
        { key: "up_to_1m", label: "До 1 000 000 ₽ / мес" },
        { key: "over_1m", label: "Более 1 000 000 ₽ / мес" }
      ]
    },
    {
      id: "pain",
      title: "Главная бизнес-задача",
      options: [
        { key: "seo", label: "SEO-оптимизация и описание карточек" },
        { key: "margin", label: "Расчет маржинальности и цены" },
        { key: "ads", label: "Эффективная реклама и офферы" },
        { key: "strategy", label: "Стратегия развития и план продаж" }
      ]
    }
  ]
};

function $(id) { return document.getElementById(id); }

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
  tg.ready();
  tg.expand();
  if (tg.HeaderColor) tg.setHeaderColor("secondary_bg_color");
  document.body.classList.add("tg-theme");
}

function showToast(text) {
  const el = $("toast");
  el.textContent = text;
  el.classList.add("visible");
  setTimeout(() => el.classList.remove("visible"), 2800);
}

function switchView(target) {
  document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach((btn) => btn.classList.toggle("active", btn.dataset.target === target));
  
  const targetView = $(`view-${target}`);
  if (targetView) targetView.classList.add("active");

  const titles = { home: "Главная", chat: "AI Чат", tools: "Инструменты", history: "История", profile: "Профиль" };
  $("pageTitle").textContent = titles[target] || "FounderPilot AI";
}

function autoResizeTextarea(textarea) {
  textarea.style.height = "auto";
  textarea.style.height = (textarea.scrollHeight) + "px";
}

function updateChatSendButton(textareaId, buttonId) {
  const txt = $(textareaId), btn = $(buttonId);
  if (txt && btn) btn.disabled = !txt.value.trim();
}

async function request(url, options = {}) {
  const initData = tg?.initData || "";
  options.headers = { ...options.headers, "Content-Type": "application/json" };
  if (initData) options.headers["X-Telegram-Init-Data"] = initData;
  const res = await fetch(url, options);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Системная ошибка сервера" }));
    throw new Error(err.detail || "Внутренний сбой платформы");
  }
  return res.json();
}

function renderChat(scrollId, messages) {
  const scroll = $(scrollId);
  if (!scroll) return;
  if (!messages || !messages.length) {
    scroll.innerHTML = `<div class="chat-empty"><span data-icon="chat"></span><p>История диалога пуста.</p></div>`;
    injectIcons(scroll);
    return;
  }
  scroll.innerHTML = messages.map(m => {
    let cls = "system-msg";
    if (m.role === "user") cls = "user";
    if (m.role === "assistant") cls = "bot";
    return `<div class="msg ${cls}">${m.text}</div>`;
  }).join("");
}

async function handleChatSend(inputId, scrollId, sendBtnId) {
  const input = $(inputId), text = input.value.trim();
  if (!text) return;
  
  input.value = "";
  autoResizeTextarea(input);
  updateChatSendButton(inputId, sendBtnId);

  const scroll = $(scrollId);
  let empty = scroll.querySelector(".chat-empty");
  if (empty) empty.remove();

  scroll.insertAdjacentHTML("beforeend", `<div class="msg user">${text}</div>`);
  const statusId = "status_" + Date.now();
  scroll.insertAdjacentHTML("beforeend", `<div class="msg bot system-msg" id="${statusId}">Выполняется анализ данных...</div>`);
  scroll.scrollTop = scroll.scrollHeight;

  try {
    const res = await request("/api/ask", {
      method: "POST",
      body: JSON.stringify({ mode: state.currentMode, text })
    });
    $(statusId)?.remove();
    scroll.insertAdjacentHTML("beforeend", `<div class="msg bot">${res.answer}</div>`);
    if (state.user) {
      state.user.used_today = res.used_today;
      state.user.used_period = res.used_period;
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
  }
  scroll.scrollTop = scroll.scrollHeight;
}

function updateProfileUI() {
  if (!state.user) return;
  if ($("homeGreeting")) $("homeGreeting").textContent = `Здравствуйте, ${state.user.first_name || "пользователь"}`;
  if ($("profileUserTitle")) $("profileUserTitle").textContent = state.user.username ? `@${state.user.username}` : `ID: ${state.user.telegram_id}`;
  
  const label = $("profilePlanLabel");
  if (label) {
    const p = state.user.plan ? state.user.plan.toUpperCase() : "FREE";
    const rem = state.user.remaining === null ? "Без ограничений" : `Осталось: ${state.user.remaining}`;
    label.innerHTML = `${p} <small style="display:block; font-weight:normal; margin-top:2px;">${rem}</small>`;
  }
  if ($("profileBusinessDescription")) $("profileBusinessDescription").value = state.user.business_profile || "";
  const initial = (state.user.first_name || "F").charAt(0).toUpperCase();
  if ($("userAvatar")) $("userAvatar").textContent = initial;
}

async function loadMe() {
  const data = await request("/api/me");
  state.user = data.user;
  updateProfileUI();
  if (data.onboarding_required) openOnboarding();
}

function openOnboarding() {
  state.onboardingStep = 0;
  state.onboardingData = {};
  $("onboardingModal").hidden = false;
  renderOnboardingStep();
}

function renderOnboardingStep() {
  const cfg = state.onboardingConfig[state.onboardingStep];
  $("onboardingTitle").textContent = cfg.title;
  
  const dots = $("onboardingModal").querySelectorAll(".progress-row span");
  dots.forEach((dot, idx) => dot.classList.toggle("active", idx === state.onboardingStep));
  
  $("onboardingBackBtn").style.visibility = state.onboardingStep === 0 ? "hidden" : "visible";
  $("onboardingNextBtn").textContent = state.onboardingStep === state.onboardingConfig.length - 1 ? "Завершить" : "Далее";
  
  let html = "";
  cfg.options.forEach(opt => {
    const act = state.onboardingData[cfg.id] === opt.key ? "active" : "";
    html += `<button class="onboarding-option ${act}" data-key="${opt.key}" type="button">${opt.label}</button>`;
  });
  $("onboardingBody").innerHTML = html;
  $("onboardingError").hidden = true;
}

async function nextOnboarding() {
  const cfg = state.onboardingConfig[state.onboardingStep];
  if (!state.onboardingData[cfg.id]) {
    const err = $("onboardingError");
    err.textContent = "Пожалуйста, выберите один из вариантов.";
    err.hidden = false;
    return;
  }
  if (state.onboardingStep < state.onboardingConfig.length - 1) {
    state.onboardingStep++;
    renderOnboardingStep();
  } else {
    try {
      const res = await request("/api/onboarding", { method: "POST", body: JSON.stringify(state.onboardingData) });
      state.user = res.user;
      updateProfileUI();
      $("onboardingModal").hidden = true;
      showToast("Профиль успешно настроен");
    } catch (err) {
      const e = $("onboardingError");
      e.textContent = err.message;
      e.hidden = false;
    }
  }
}

function previousOnboarding() {
  if (state.onboardingStep > 0) {
    state.onboardingStep--;
    renderOnboardingStep();
  }
}

async function loadTools() {
  const data = await request("/api/tools");
  state.tools = data.tools || [];
  renderTools(state.tools);
  
  const row = $("historyFilters");
  const uniq = [...new Set(state.tools.map(t => t.mode).filter(Boolean))];
  uniq.forEach(m => {
    row.insertAdjacentHTML("beforeend", `<button data-filter="${m}" type="button">${m.toUpperCase()}</button>`);
  });
}

function renderTools(list) {
  const grid = $("toolsGrid");
  if (!grid) return;
  if (!list.length) {
    grid.innerHTML = `<p class="muted" style="text-align:center; padding:20px;">Модули не найдены</p>`;
    return;
  }
  grid.innerHTML = list.map(t => `
    <button class="tool-card" data-mode="${t.mode}" data-prompt="${t.prompt || ''}" type="button">
      <span class="card-icon" data-icon="tools"></span>
      <div class="tool-meta">
        <h4>${t.title}</h4>
        <p>${t.description}</p>
      </div>
      <span data-icon="chevron" class="chevron"></span>
    </button>
  `).join("");
  injectIcons(grid);
}

async function loadHistory() {
  state.history = await request("/api/history");
  renderHistory();
}

function renderHistory() {
  const list = $("historyList");
  if (!list) return;
  const filtered = state.historyFilter === "all" ? state.history : state.history.filter(h => h.mode === state.historyFilter);
  if (!filtered.length) {
    list.innerHTML = `<p class="muted" style="text-align:center; padding:20px;">Архив пуст</p>`;
    return;
  }
  list.innerHTML = filtered.map(h => `
    <article class="history-card">
      <div class="meta-line">
        <span>${h.mode}</span>
        <span>${h.created_at || ""}</span>
      </div>
      <p><strong>Запрос:</strong> ${h.request_text}</p>
      <p style="margin-top:6px; color:var(--app-hint);">- ${h.response_preview || ""}</p>
    </article>
  `).join("");
}

async function loadBillingPlans() {
  const data = await request("/api/billing/plans");
  state.plans = data.plans || {};
}

function openBillingModal() {
  $("billingModal").hidden = false;
  renderBillingPlans();
}

function closeBillingModal() {
  $("billingModal").hidden = true;
  $("paymentProviderBox").hidden = true;
  $("billingPlanList").hidden = false;
}

function renderBillingPlans() {
  $("paymentProviderBox").hidden = true;
  const container = $("billingPlanList");
  container.hidden = false;
  
  const html = Object.keys(state.plans).map(key => {
    const p = state.plans[key];
    return `
      <button class="plan-card" data-plan-key="${key}" type="button">
        <div class="plan-main">
          <span data-icon="user"></span>
          <div>
            <h4>${p.title}</h4>
            <small>Лимит: ${p.daily_limit} запр./день</small>
          </div>
        </div>
        <span class="plan-price">${p.price_label}</span>
      </button>
    `;
  }).join("");
  container.innerHTML = html;
  injectIcons(container);
}

function selectPlan(key) {
  state.activePlan = state.plans[key];
  if (!state.activePlan) return;
  $("billingPlanList").hidden = true;
  const box = $("paymentProviderBox");
  box.hidden = false;
  
  const list = $("providerList");
  list.innerHTML = state.activePlan.providers.map(prov => {
    // Интеллектуальный роутинг кастомных брендовых логотипов
    let iconName = "chat";
    let customClass = "";
    const pid = prov.id.toLowerCase();
    
    if (pid.includes("stars") || pid.includes("telegram_stars")) {
      iconName = "tg_stars";
      customClass = "provider-icon-stars";
    } else if (pid.includes("ton") || pid.includes("crypto") || pid.includes("wallet")) {
      iconName = "ton";
      customClass = "provider-icon-ton";
    }

    return `
      <button class="provider-card" data-provider="${prov.id}" type="button">
        <div class="provider-main">
          <span class="card-icon ${customClass}" data-icon="${iconName}"></span>
          <div>
            <strong>${prov.title}</strong>
            <small>${prov.description || ""}</small>
          </div>
        </div>
        <span data-icon="chevron" class="chevron"></span>
      </button>
    `;
  }).join("");
  injectIcons(list);
  $("billingError").hidden = true;
}

async function checkout(providerId) {
  if (!state.activePlan) return;
  const errBox = $("billingError");
  errBox.hidden = true;
  try {
    const res = await request("/api/billing/order", {
      method: "POST",
      body: JSON.stringify({ plan: state.activePlan.key, provider: providerId })
    });
    if (providerId === "telegram_stars" && res.invoice_url) {
      if (tg) {
        tg.openInvoice(res.invoice_url, (status) => {
          if (status === "paid") {
            showToast("Оплата успешно верифицирована");
            closeBillingModal();
            loadMe().catch(() => {});
          } else if (status === "failed") {
            showToast("Ошибка при проведении платежа");
          }
        });
      } else {
        window.open(res.invoice_url, "_blank");
      }
    } else if (res.invoice_url) {
      if (tg) {
        tg.openLink(res.invoice_url);
      } else {
        window.open(res.invoice_url, "_blank");
      }
      closeBillingModal();
    } else {
      showToast("Заказ сформирован успешно");
      closeBillingModal();
    }
  } catch (err) {
    errBox.textContent = err.message;
    errBox.hidden = false;
  }
}

async function submitFeedback(toolId, type, view, text) {
  await request("/api/feedback", {
    method: "POST",
    body: JSON.stringify({ tool_id: toolId, type, view, message: text })
  });
  showToast("Сообщение успешно отправлено");
}

function bindEvents() {
  const textareas = ["homeChatInput", "mainChatInput"];
  textareas.forEach(id => {
    const el = $(id);
    if (!el) return;
    el.addEventListener("input", () => {
      autoResizeTextarea(el);
      const btnId = id === "homeChatInput" ? "homeChatSendBtn" : "mainChatSendBtn";
      updateChatSendButton(id, btnId);
    });
  });

  $("appNav").addEventListener("click", (e) => {
    const btn = e.target.closest(".nav-item");
    if (btn) switchView(btn.dataset.target);
  });

  $("homeChatSendBtn").addEventListener("click", () => handleChatSend("homeChatInput", "homeChatScroll", "homeChatSendBtn"));
  $("mainChatSendBtn").addEventListener("click", () => handleChatSend("mainChatInput", "mainChatScroll", "mainChatSendBtn"));

  document.addEventListener("click", (e) => {
    const action = e.target.closest("[data-prompt]");
    if (action) {
      const p = action.dataset.prompt;
      if (action.classList.contains("tool-card")) {
        state.currentMode = action.dataset.mode || "strategy";
        $("chatViewTitle").textContent = action.querySelector("h4").textContent;
        $("chatViewSubtitle").textContent = "Специализированный режим анализа";
        switchView("chat");
        $("mainChatInput").value = p;
        autoResizeTextarea($("mainChatInput"));
        updateChatSendButton("mainChatInput", "mainChatSendBtn");
      } else {
        state.currentMode = "strategy";
        $("chatViewTitle").textContent = "Аналитическая сессия";
        $("chatViewSubtitle").textContent = "Прямой диалог с бизнес-моделью";
        switchView("chat");
        $("mainChatInput").value = p;
        autoResizeTextarea($("mainChatInput"));
        updateChatSendButton("mainChatInput", "mainChatSendBtn");
      }
    }
  });

  $("toolsSearchInput")?.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    const filtered = state.tools.filter(t => t.title.toLowerCase().includes(q) || t.description.toLowerCase().includes(q));
    renderTools(filtered);
  });

  $("onboardingBody").addEventListener("click", (e) => {
    const opt = e.target.closest(".onboarding-option");
    if (!opt) return;
    const cfg = state.onboardingConfig[state.onboardingStep];
    state.onboardingData[cfg.id] = opt.dataset.key;
    $("onboardingBody").querySelectorAll(".onboarding-option").forEach(node => node.classList.toggle("active", node === opt));
  });

  $("profileBusinessForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const desc = $("profileBusinessDescription").value.trim();
    try {
      const res = await request("/api/profile/business", { method: "POST", body: JSON.stringify({ description: desc }) });
      state.user = res.user;
      showToast("Профиль бизнеса обновлен");
    } catch (err) {
      showToast(err.message);
    }
  });

  $("appFeedbackForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = $("appFeedbackText").value.trim();
    if (!message) {
      showToast("Пожалуйста, заполните поле ввода");
      return;
    }
    await submitFeedback(-1, "app", "profile", message);
    $("appFeedbackText").value = "";
  });

  $("openBillingBtn")?.addEventListener("click", openBillingModal);
  $("closeBillingBtn")?.addEventListener("click", closeBillingModal);
  $("backToPlansBtn")?.addEventListener("click", renderBillingPlans);
  
  $("billingModal")?.addEventListener("click", (e) => {
    if (e.target === $("billingModal")) closeBillingModal();
  });

  $("billingPlanList").addEventListener("click", (e) => {
    const card = e.target.closest("[data-plan-key]");
    if (card) selectPlan(card.dataset.planKey);
  });

  $("providerList").addEventListener("click", (e) => {
    const card = e.target.closest("[data-provider]");
    if (card) checkout(card.dataset.provider);
  });

  $("onboardingNextBtn").addEventListener("click", nextOnboarding);
  $("onboardingBackBtn").addEventListener("click", previousOnboarding);

  $("historyFilters").addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-filter]");
    if (!btn) return;
    state.historyFilter = btn.dataset.filter;
    $("historyFilters").querySelectorAll("button").forEach(n => n.classList.toggle("active", n === btn));
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
  
  await Promise.all([loadTools(), loadBillingPlans()]);
  try {
    await loadMe();
  } catch (err) {
    showToast(err.message);
  }
  await loadHistory().catch(() => {});
})();