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
  tg_stars: '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
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
  
  const savedKey = state.onboardingData[cfg.id];
  const html = cfg.options.map(o => `
    <button class="onboarding-option ${savedKey === o.key ? 'active' : ''}" data-key="${o.key}" type="button">
      ${o.label}
    </button>
  `).join("");
  
  $("onboardingBody").innerHTML = html;
  $("onboardingError").hidden = true;
  $("onboardingBackBtn").disabled = (state.onboardingStep === 0);
  
  const isLast = (state.onboardingStep === state.onboardingConfig.length - 1);
  $("onboardingNextBtn").textContent = isLast ? "Готово" : "Далее";
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
      $("onboardingNextBtn").disabled = true;
      const res = await request("/api/onboarding", {
        method: "POST",
        body: JSON.stringify(state.onboardingData)
      });
      state.user = res.user;
      updateProfileUI();
      $("onboardingModal").hidden = true;
      showToast("Онбординг успешно завершён!");
    } catch (e) {
      const err = $("onboardingError");
      err.textContent = e.message;
      err.hidden = false;
      $("onboardingNextBtn").disabled = false;
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
  const grid = $("toolsGrid");
  if (!grid) return;
  
  if (!state.tools.length) {
    grid.innerHTML = `<p class="muted" style="grid-column: 1/-1; text-align: center; padding: 40px 0;">Инструменты временно недоступны.</p>`;
    return;
  }
  
  grid.innerHTML = state.tools.map(t => `
    <div class="tool-card" data-prompt="${t.prompt_template}">
      <div class="tool-icon-wrapper"><span data-icon="tools"></span></div>
      <h4>${t.title}</h4>
      <p class="muted">${t.description}</p>
    </div>
  `).join("");
  injectIcons(grid);
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
}

function renderBillingPlans() {
  $("paymentProviderBox").hidden = true;
  const planList = $("billingPlanList");
  planList.hidden = false;
  $("billingTitle").textContent = "Доступные тарифы";

  const keys = Object.keys(state.plans);
  if (!keys.length) {
    planList.innerHTML = `<p class="muted" style="text-align:center; padding:20px;">Нет доступных тарифов.</p>`;
    return;
  }

  planList.innerHTML = keys.map(k => {
    const p = state.plans[k];
    const isCurrent = state.user && state.user.plan === k;
    return `
      <button class="plan-card ${isCurrent ? 'muted-plan' : ''}" data-plan-key="${k}" type="button">
        <div class="plan-main">
          <div>
            <h4>${p.title}</h4>
            <small>${p.description}</small>
          </div>
        </div>
        <div class="plan-price">${p.price_monthly} ₽</div>
      </button>
    `;
  }).join("");
}

function selectPlan(planKey) {
  state.activePlan = state.plans[planKey];
  if (!state.activePlan) return;

  $("billingPlanList").hidden = true;
  $("billingTitle").textContent = `Оплата: ${state.activePlan.title}`;
  $("billingError").hidden = true;
  
  const box = $("paymentProviderBox");
  box.hidden = false;

  const provList = $("providerList");
  provList.innerHTML = state.activePlan.providers.map(p => {
    let iconName = "credit-card";
    let extraCls = "";
    if (p.id === "telegram_stars") { iconName = "tg_stars"; extraCls = "provider-card-stars"; }
    if (p.id === "ton") { iconName = "ton"; extraCls = "provider-card-ton"; }
    
    return `
      <button class="provider-card ${extraCls}" data-provider="${p.id}" type="button">
        <span class="provider-icon" data-icon="${iconName}"></span>
        <div class="provider-info">
          <strong>${p.title}</strong>
          <small>${p.description}</small>
        </div>
        <div class="provider-price-tag">${p.price_formatted}</div>
      </button>
    `;
  }).join("");
  injectIcons(provList);
}

async function checkout(providerId) {
  const pBox = $("paymentProviderBox");
  const errEl = $("billingError");
  errEl.hidden = true;
  
  try {
    pBox.classList.add("loading-state");
    const planKey = Object.keys(state.plans).find(k => state.plans[k].title === state.activePlan.title);
    
    const res = await request("/api/billing/checkout", {
      method: "POST",
      body: JSON.stringify({ plan: planKey, provider: providerId })
    });

    if (providerId === "telegram_stars" && res.invoice_link) {
      if (window.Telegram?.WebApp?.openInvoice) {
        window.Telegram.WebApp.openInvoice(res.invoice_link, (status) => {
          if (status === "paid") {
            showToast("Оплата успешно проведена!");
            closeBillingModal();
            loadMe().catch(() => {});
          } else {
            showToast("Оплата не завершена");
          }
        });
      } else {
        showToast("Прямая оплата поддерживается только внутри Telegram App");
      }
      return;
    }

    if (res.invoice_url) {
      if (window.Telegram?.WebApp?.openLink) {
        window.Telegram.WebApp.openLink(res.invoice_url);
      } else {
        window.open(res.invoice_url, "_blank");
      }
      showToast("Ссылка на оплату открыта.");
      closeBillingModal();
      return;
    }

    if (res.success) {
      showToast("Подписка успешно активирована!");
      closeBillingModal();
      await loadMe();
    }
  } catch (err) {
    errEl.textContent = err.message;
    errEl.hidden = false;
  } finally {
    pBox.classList.remove("loading-state");
  }
}

async function loadHistory() {
  const data = await request("/api/history");
  state.history = data.history || [];
  renderHistory();
}

function renderHistory() {
  const list = $("historyList");
  if (!list) return;

  let filtered = state.history;
  if (state.historyFilter !== "all") {
    filtered = state.history.filter(h => h.mode === state.historyFilter);
  }

  if (!filtered.length) {
    list.innerHTML = `<div class="chat-empty"><span data-icon="history"></span><p>Записей не найдено.</p></div>`;
    injectIcons(list);
    return;
  }

  list.innerHTML = filtered.map(h => `
    <article class="history-card">
      <div class="history-card-header">
        <span class="badge badge-${h.mode}">${h.mode.toUpperCase()}</span>
        <time class="muted small">${new Date(h.timestamp * 1000).toLocaleDateString()}</time>
      </div>
      <p class="history-prompt"><strong>Запрос:</strong> ${h.text}</p>
      <div class="history-answer"><strong>Ответ ИИ:</strong> ${h.answer}</div>
    </article>
  `).join("");
}

function bindEvents() {
  document.querySelectorAll(".nav-item").forEach(btn => {
    btn.addEventListener("click", () => switchView(btn.dataset.target));
  });

  document.querySelectorAll("[data-open-view]").forEach(btn => {
    btn.addEventListener("click", () => switchView(btn.dataset.openView));
  });

  const txtHome = $("homeChatInput"), btnHome = $("homeChatSendBtn");
  if (txtHome && btnHome) {
    txtHome.addEventListener("input", () => {
      autoResizeTextarea(txtHome);
      updateChatSendButton("homeChatInput", "homeChatSendBtn");
    });
    btnHome.addEventListener("click", () => handleChatSend("homeChatInput", "homeChatScroll", "homeChatSendBtn"));
  }

  const txtMain = $("mainChatInput"), btnMain = $("mainChatSendBtn");
  if (txtMain && btnMain) {
    txtMain.addEventListener("input", () => {
      autoResizeTextarea(txtMain);
      updateChatSendButton("mainChatInput", "mainChatSendBtn");
    });
    btnMain.addEventListener("click", () => handleChatSend("mainChatInput", "mainChatScroll", "mainChatSendBtn"));
  }

  document.querySelectorAll(".chat-mode-selector .mode-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".chat-mode-selector .mode-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      state.currentMode = tab.dataset.mode;
    });
  });

  $("quickStrip")?.addEventListener("click", (e) => {
    const act = e.target.closest(".quick-action");
    if (!act) return;
    switchView("chat");
    const mainIn = $("mainChatInput");
    if (mainIn) {
      mainIn.value = act.dataset.prompt || "";
      autoResizeTextarea(mainIn);
      updateChatSendButton("mainChatInput", "mainChatSendBtn");
      mainIn.focus();
    }
  });

  $("toolsGrid")?.addEventListener("click", (e) => {
    const card = e.target.closest(".tool-card");
    if (!card) return;
    switchView("chat");
    const mainIn = $("mainChatInput");
    if (mainIn) {
      mainIn.value = card.dataset.prompt || "";
      autoResizeTextarea(mainIn);
      updateChatSendButton("mainChatInput", "mainChatSendBtn");
      mainIn.focus();
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
    const profileText = $("profileBusinessDescription").value.trim();
    try {
      const res = await request("/api/profile/save", {
        method: "POST",
        body: JSON.stringify({ business_profile: profileText })
      });
      state.user = res.user;
      updateProfileUI();
      showToast("Профиль успешно сохранён!");
    } catch (err) {
      showToast(err.message);
    }
  });

  $("submitAppFeedbackBtn")?.addEventListener("click", async () => {
    const msg = $("appFeedbackText").value.trim();
    if (!msg) {
      showToast("Напишите, что улучшить");
      return;
    }
    try {
      await request("/api/feedback", {
        method: "POST",
        body: JSON.stringify({ message: msg, type: "app" })
      });
      $("appFeedbackText").value = "";
      showToast("Спасибо за ваш отзыв!");
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
  } catch (error) {
    showToast(error.message);
  }
  await loadHistory().catch(() => {});
})();