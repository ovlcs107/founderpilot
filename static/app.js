const tg = window.Telegram?.WebApp || null;

const iconPaths = {
  home: '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
  chat: '<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7A8.4 8.4 0 0 1 4 11.5a8.5 8.5 0 0 1 17 0Z"/>',
  tools: '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/>',
  history: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
  user: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
  profile: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
  copy: '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
  save: '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/>',
  trash: '<polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
  edit: '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>',
  plus: '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
  close: '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
  check: '<polyline points="20 6 9 17 4 12"/>',
  warning: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
  back: '<line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>',
  send: '<line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>',
  wallet: '<path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4"/><path d="M4 6v12a2 2 0 0 0 2 2h14v-4"/><path d="M18 12a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h4v-6z"/>'
};

const toolIcons = {
  1: "edit", 2: "wallet", 3: "tools", 4: "edit",
  5: "history", 6: "check", 7: "home", 8: "tools",
  9: "history", 10: "wallet", 11: "check"
};

const state = {
  user: null,
  tools: [],
  plans: [],
  history: [],
  currentView: "home",
  activeTool: null,
  historyFilter: "all",
  activePromptId: null,
  onboardingIndex: 0,
  onboardingData: {},
  billingSelectedPlan: null
};

const onboardingSteps = [
  {
    title: "Кто вы?",
    field: "role",
    type: "select",
    options: [
      { value: "wb_seller", label: "Селлер Wildberries" },
      { value: "ozon_seller", label: "Селлер Ozon" },
      { value: "multichannel_seller", label: "Селлер WB + Ozon" },
      { value: "small_business", label: "Владелец малого бизнеса" },
      { value: "beginner", label: "Планирую запуск бизнеса" }
    ]
  },
  {
    title: "Какая у вас ниша?",
    field: "niche",
    type: "input",
    placeholder: "Например: Одежда, Электроника, Косметика",
    help: "Это поможет ИИ лучше адаптировать тексты и расчёты под ваш товар."
  },
  {
    title: "Текущий оборот в месяц",
    field: "revenue",
    type: "select",
    options: [
      { value: "0", label: "Только начинаю (0 руб)" },
      { value: "under_100k", label: "До 100 000 руб" },
      { value: "100k_500k", label: "100 000 – 500 000 руб" },
      { value: "500k_2m", label: "500 000 – 2 000 000 руб" },
      { value: "above_2m", label: "Более 2 000 000 руб" }
    ]
  }
];

const els = {
  pageTitle: $("pageTitle"),
  homeGreeting: $("homeGreeting"),
  homeSuggestions: $("homeSuggestions"),
  homeChatScroll: $("homeChatScroll"),
  homeChatEmpty: $("homeChatEmpty"),
  homeChatMessages: $("homeChatMessages"),
  homeChatInput: $("homeChatInput"),
  homeChatForm: $("homeChatForm"),
  homeChatSendBtn: $("homeChatSendBtn"),
  homeActivePromptRow: $("homeActivePromptRow"),
  homeActivePromptText: $("homeActivePromptText"),
  homeCancelPromptBtn: $("homeCancelPromptBtn"),
  toolsGrid: $("toolsGrid"),
  toolRunnerBox: $("toolRunnerBox"),
  toolRunnerTitle: $("toolRunnerTitle"),
  toolRunnerDesc: $("toolRunnerDesc"),
  toolForm: $("toolForm"),
  toolResultCard: $("toolResultCard"),
  toolResultContent: $("toolResultContent"),
  toolResultActions: $("toolResultActions"),
  toolBackBtn: $("toolBackBtn"),
  historyList: $("historyList"),
  profileName: $("profileName"),
  profileUsername: $("profileUsername"),
  profilePlanBadge: $("profilePlanBadge"),
  profileLimitsText: $("profileLimitsText"),
  profileLimitsBar: $("profileLimitsBar"),
  userAvatar: $("userAvatar"),
  profileAvatar: $("profileAvatar"),
  billingModal: $("billingModal"),
  billingPlanList: $("billingPlanList"),
  paymentProviderBox: $("paymentProviderBox"),
  providerList: $("providerList"),
  billingError: $("billingError"),
  closeBillingBtn: $("closeBillingBtn"),
  backToPlansBtn: $("backToPlansBtn"),
  onboardingModal: $("onboardingModal"),
  onboardingTitle: $("onboardingTitle"),
  onboardingBody: $("onboardingBody"),
  onboardingError: $("onboardingError"),
  onboardingNextBtn: $("onboardingNextBtn"),
  onboardingBackBtn: $("onboardingBackBtn")
};

function $(id) {
  return document.getElementById(id);
}

function injectIcons() {
  document.querySelectorAll("[data-icon]").forEach((el) => {
    const iconName = el.dataset.icon;
    const path = iconPaths[iconName] || iconPaths["home"];
    el.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${path}</svg>`;
  });
}

function createIconSvg(name) {
  const path = iconPaths[name] || iconPaths["home"];
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${path}</svg>`;
}

function initTelegram() {
  if (tg) {
    tg.ready();
    tg.expand();
    if (tg.setHeaderColor) {
      tg.setHeaderColor("secondary_bg_color");
    }
  }
}

function getTelegramUser() {
  if (tg?.initDataUnsafe?.user) {
    return tg.initDataUnsafe.user;
  }
  return { id: 123456, first_name: "Тест Бизнес", username: "test_entrepreneur" };
}

async function request(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `Ошибка сервера: ${response.status}`);
  }
  return response.json();
}

function showToast(text, duration = 2500) {
  const toast = $("toast");
  if (!toast) return;
  toast.innerText = text;
  toast.hidden = false;
  setTimeout(() => { toast.hidden = true; }, duration);
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function switchView(viewName) {
  state.currentView = viewName;
  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("active", view.id === `view-${viewName}`);
  });
  document.querySelectorAll("#bottomNav .nav-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === viewName);
  });
  
  const titles = { home: "Главная", tools: "Инструменты", history: "История", profile: "Профиль" };
  if (els.pageTitle) els.pageTitle.innerText = titles[viewName] || "FounderPilot";

  if (viewName === "home") {
    // Ввод чата подстраиваем
  } else if (viewName === "tools") {
    renderTools();
  } else if (viewName === "history") {
    loadHistory().catch(() => {});
  } else if (viewName === "profile") {
    renderProfile();
  }
}

async function loadMe() {
  const tgUser = getTelegramUser();
  const payload = {
    telegram_id: tgUser.id,
    first_name: tgUser.first_name,
    username: tgUser.username
  };
  const user = await request("/api/me", {
    method: "POST",
    body: JSON.stringify(payload)
  });
  state.user = user;
  setupProfileHeader();
  if (!user.is_onboarded) {
    startOnboarding();
  }
}

function setupProfileHeader() {
  if (!state.user) return;
  const fName = state.user.first_name || "F";
  const initials = fName.substring(0, 2).toUpperCase();
  if (els.userAvatar) els.userAvatar.innerText = initials;
  if (els.profileAvatar) els.profileAvatar.innerText = initials;
  if (els.homeGreeting) els.homeGreeting.innerText = `Здравствуйте, ${fName}`;
}

/* ==========================================================================
   ОНБОРДИНГ ДЛЯ БИЗНЕСА
   ========================================================================== */
function startOnboarding() {
  state.onboardingIndex = 0;
  state.onboardingData = {};
  els.onboardingModal.hidden = false;
  renderOnboardingStep();
}

function renderOnboardingStep() {
  const step = onboardingSteps[state.onboardingIndex];
  els.onboardingTitle.innerText = step.title;
  els.onboardingError.hidden = true;
  
  const progressSpans = els.onboardingModal.querySelectorAll(".progress-row span");
  progressSpans.forEach((span, idx) => {
    span.classList.toggle("active", idx <= state.onboardingIndex);
  });

  els.onboardingBackBtn.style.visibility = state.onboardingIndex === 0 ? "hidden" : "visible";
  els.onboardingNextBtn.innerText = state.onboardingIndex === onboardingSteps.length - 1 ? "Готово" : "Далее";

  let html = "";
  const savedVal = state.onboardingData[step.field] || "";

  if (step.type === "select") {
    html += `<select id="onboarding-${step.field}">`;
    step.options.forEach((opt) => {
      const selected = opt.value === savedVal ? "selected" : "";
      html += `<option value="${opt.value}" ${selected}>${opt.label}</option>`;
    });
    html += `</select>`;
  } else if (step.type === "input") {
    html += `<input id="onboarding-${step.field}" type="text" placeholder="${step.placeholder}" value="${escapeHtml(savedVal)}" />`;
  }
  
  if (step.help) {
    html += `<p class="field-help">${step.help}</p>`;
  }
  els.onboardingBody.innerHTML = html;
}

async function nextOnboarding() {
  const step = onboardingSteps[state.onboardingIndex];
  const inputEl = $(`onboarding-${step.field}`);
  const val = inputEl ? inputEl.value.trim() : "";
  
  if (!val && step.type === "input") {
    els.onboardingError.innerText = "Пожалуйста, заполните поле";
    els.onboardingError.hidden = false;
    return;
  }

  state.onboardingData[step.field] = val;

  if (state.onboardingIndex < onboardingSteps.length - 1) {
    state.onboardingIndex++;
    renderOnboardingStep();
  } else {
    try {
      const payload = {
        telegram_id: getTelegramUser().id,
        ...state.onboardingData
      };
      await request("/api/me/onboarding", {
        method: "PUT",
        body: JSON.stringify(payload)
      });
      els.onboardingModal.hidden = true;
      showToast("Профиль успешно настроен");
      await loadMe();
    } catch (e) {
      els.onboardingError.innerText = e.message;
      els.onboardingError.hidden = false;
    }
  }
}

function previousOnboarding() {
  if (state.onboardingIndex > 0) {
    state.onboardingIndex--;
    renderOnboardingStep();
  }
}

/* ==========================================================================
   СОВРЕМЕННЫЙ AI CHAT НА ГЛАВНОЙ
   ========================================================================== */
function updateChatSendButton() {
  const hasText = els.homeChatInput.value.trim().length > 0;
  els.homeChatSendBtn.disabled = !hasText;
}

function renderPromptSuggestions() {
  const suggestions = [
    { id: 1, title: "Посчитать маржу", prompt: "Помоги рассчитать маржинальность товара. Себестоимость 400р, цена на WB 1200р." },
    { id: 2, title: "Улучшить карточку", prompt: "Как оптимизировать карточку товара 'Термокружка автомобильная' для поднятия в топ?" },
    { id: 3, title: "Сделать оффер", prompt: "Составь сильный коммерческий оффер для оптовых покупателей детской одежды." },
    { id: 4, title: "Разобрать конкурента", prompt: "Какие параметры важнее всего оценить при экспресс-анализе карточки конкурента?" },
    { id: 5, title: "Ответить на отзыв", prompt: "Напиши вежливый профессиональный ответ на негативный отзыв: 'Коробка пришла рваная'." }
  ];

  els.homeSuggestions.innerHTML = suggestions.map((s) => `
    <button class="quick-action" data-prompt-id="${s.id}" type="button">
      <strong>${s.title}</strong>
    </button>
  `).join("");

  els.homeSuggestions.querySelectorAll(".quick-action").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = suggestions.find(s => s.id == btn.dataset.promptId);
      if (item) {
        state.activePromptId = item.id;
        els.homeActivePromptText.innerText = item.title;
        els.homeActivePromptRow.hidden = false;
        els.homeChatInput.value = item.prompt;
        els.homeChatInput.focus();
        updateChatSendButton();
      }
    });
  });
}

async function handleChatSubmit(event) {
  event.preventDefault();
  const text = els.homeChatInput.value.trim();
  if (!text) return;

  els.homeChatInput.value = "";
  updateChatSendButton();
  els.homeChatEmpty.style.display = "none";

  appendChatMessage("user", text);
  
  const loadingId = "loader-" + Date.now();
  appendChatLoader(loadingId);
  
  els.homeActivePromptRow.hidden = true;

  try {
    const payload = {
      telegram_id: getTelegramUser().id,
      message: text,
      suggestion_id: state.activePromptId
    };
    state.activePromptId = null;

    const data = await request("/api/chat", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    
    $(loadingId)?.remove();
    appendChatMessage("assistant", data.response, data.chat_id);
  } catch (err) {
    $(loadingId)?.remove();
    appendChatMessage("assistant", `Не удалось получить ответ: ${err.message}`);
  }
}

function appendChatMessage(role, content, chatId = null) {
  const isUser = role === "user";
  const msgDiv = document.createElement("div");
  msgDiv.className = `chat-message ${role}`;
  
  let actionsHtml = "";
  if (!isUser && chatId) {
    actionsHtml = `
      <div class="message-actions">
        <button class="icon-btn compact" onclick="copyTextToClipboard(this, \`${escapeHtml(content)}\`)" title="Скопировать">
          <span data-icon="copy">${createIconSvg("copy")}</span>
        </button>
        <button class="icon-btn compact" onclick="toggleSaveChat(this, ${chatId})" title="Сохранить">
          <span data-icon="save">${createIconSvg("save")}</span>
        </button>
      </div>
    `;
  }

  msgDiv.innerHTML = `
    <div class="bubble">${escapeHtml(content).replace(/\n/g, "<br>")}</div>
    ${actionsHtml}
  `;
  els.homeChatMessages.appendChild(msgDiv);
  els.homeChatScroll.scrollTop = els.homeChatScroll.scrollHeight;
}

function appendChatLoader(id) {
  const loader = document.createElement("div");
  loader.className = "chat-message assistant";
  loader.id = id;
  loader.innerHTML = `<div class="bubble muted">AI готовит ответ...</div>`;
  els.homeChatMessages.appendChild(loader);
  els.homeChatScroll.scrollTop = els.homeChatScroll.scrollHeight;
}

async function toggleSaveChat(btn, chatId) {
  try {
    const res = await request("/api/saved", {
      method: "POST",
      body: JSON.stringify({
        telegram_id: getTelegramUser().id,
        item_type: "chat",
        item_id: chatId
      })
    });
    showToast(res.status === "saved" ? "Сохранено в историю" : "Удалено из сохранённого");
    btn.classList.toggle("active", res.status === "saved");
  } catch (e) {
    showToast(e.message);
  }
}

/* ==========================================================================
   ИНСТРУМЕНТЫ БИЗНЕСА И ФОРМЫ
   ========================================================================== */
async function loadTools() {
  try {
    const data = await request("/api/tools");
    state.tools = data.tools || [];
  } catch (e) {
    // В случае отсутствия эндпоинта разворачиваем дефолтную бизнес-сетку инструментов
    state.tools = [
      { id: 1, name: "WB/Ozon карточка товара", description: "Генерация продающего контента для маркетплейсов", fields: [{ name: "product", label: "Товар или ниша", type: "input", placeholder: "Например: Кожаный кошелёк мужской" }, { name: "features", label: "Преимущества и ключевые слова", type: "textarea", placeholder: "Натуральная кожа, 6 слотов для карт" }] },
      { id: 2, name: "Расчёт маржи", description: "Оценка чистой прибыли и рентабельности", fields: [{ name: "cost", label: "Себестоимость (руб)", type: "input", placeholder: "500" }, { name: "price", label: "Цена продажи (руб)", type: "input", placeholder: "1500" }] },
      { id: 3, name: "Идея товара", description: "Поиск прибыльных направлений для запуска", fields: [{ name: "budget", label: "Стартовый бюджет (руб)", type: "input", placeholder: "50000" }] },
      { id: 4, name: "Описание товара", description: "SEO-оптимизированные тексты для магазинов", fields: [{ name: "name", label: "Название товара", type: "input", placeholder: "Увлажнитель воздуха" }] },
      { id: 5, name: "Реклама и оффер", description: "Создание цепляющих заголовков", fields: [{ name: "audience", label: "Целевая аудитория", type: "input", placeholder: "Предприниматели" }] },
      { id: 6, name: "Ответ на отзыв", description: "Работа со сложным негативом и лояльностью", fields: [{ name: "review", label: "Текст отзыва", type: "textarea", placeholder: "Товар пришёл с задержкой..." }] },
      { id: 7, name: "Анализ конкурента", description: "Выявление слабых мест на рынке", fields: [{ name: "comp", label: "Название конкурента", type: "input", placeholder: "Бренд X" }] },
      { id: 8, name: "SWOT-анализ", description: "Матрица рисков и возможностей", fields: [{ name: "desc", label: "Описание проекта", type: "textarea", placeholder: "Кофейня в спальном районе" }] },
      { id: 9, name: "Контент-план", description: "План публикаций на месяц вперед", fields: [{ name: "topic", label: "Тематика бизнеса", type: "input", placeholder: "Продажи на маркетплейсах" }] },
      { id: 10, name: "План продаж", description: "Расчет финансовой декомпозиции целей", fields: [{ name: "target", label: "Желаемая прибыль (руб)", type: "input", placeholder: "300000" }] },
      { id: 11, name: "Проверка бизнес-идеи", description: "Анализ рисков стартап-концепции", fields: [{ name: "idea", label: "Суть идеи", type: "textarea", placeholder: "Аренда инструмента через приложение" }] }
    ];
  }
  renderTools();
}

function renderTools() {
  if (state.activeTool) {
    els.toolsGrid.hidden = true;
    els.toolRunnerBox.hidden = false;
    return;
  }
  els.toolsGrid.hidden = false;
  els.toolRunnerBox.hidden = true;

  els.toolsGrid.innerHTML = state.tools.map((t) => `
    <button class="tool-tile" type="button" data-tool-id="${t.id}">
      <div class="card-icon">${createIconSvg(toolIcons[t.id] || "tools")}</div>
      <h3>${escapeHtml(t.name)}</h3>
      <p>${escapeHtml(t.description)}</p>
    </button>
  `).join("");

  els.toolsGrid.querySelectorAll(".tool-tile").forEach((btn) => {
    btn.addEventListener("click", () => {
      const tool = state.tools.find(t => t.id == btn.dataset.toolId);
      if (tool) openToolRunner(tool);
    });
  });
}

function openToolRunner(tool) {
  state.activeTool = tool;
  els.toolRunnerTitle.innerText = tool.name;
  els.toolRunnerDesc.innerText = tool.description;
  els.toolResultCard.hidden = true;

  let formHtml = "";
  tool.fields.forEach((f) => {
    formHtml += `
      <div class="field-container">
        <label class="field-label" for="tool-field-${f.name}">${f.label}</label>
    `;
    if (f.type === "textarea") {
      formHtml += `<textarea id="tool-field-${f.name}" placeholder="${f.placeholder || ''}" rows="4"></textarea>`;
    } else {
      formHtml += `<input id="tool-field-${f.name}" type="text" placeholder="${f.placeholder || ''}" />`;
    }
    formHtml += `</div>`;
  });

  formHtml += `<button class="primary full" type="submit">Сгенерировать</button>`;
  els.toolForm.innerHTML = formHtml;
  renderTools();
}

async function handleToolSubmit(event) {
  event.preventDefault();
  if (!state.activeTool) return;

  const fieldsData = {};
  let hasEmpty = false;

  state.activeTool.fields.forEach((f) => {
    const el = $(`tool-field-${f.name}`);
    const val = el ? el.value.trim() : "";
    if (!val) hasEmpty = true;
    fieldsData[f.name] = val;
  });

  if (hasEmpty) {
    showToast("Заполните все поля инструмента");
    return;
  }

  els.toolResultCard.hidden = true;
  const submitBtn = els.toolForm.querySelector("button[type='submit']");
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerText = "AI готовит ответ...";
  }

  try {
    const payload = {
      telegram_id: getTelegramUser().id,
      tool_id: state.activeTool.id,
      fields: fieldsData
    };
    const data = await request("/api/tools/run", {
      method: "POST",
      body: JSON.stringify(payload)
    });

    els.toolResultContent.innerHTML = `<p>${escapeHtml(data.result).replace(/\n/g, "<br>")}</p>`;
    
    els.toolResultActions.innerHTML = `
      <button class="ghost compact" id="copyToolResultBtn" type="button">Скопировать</button>
      <button class="ghost compact" id="saveToolResultBtn" type="button">Сохранить</button>
    `;

    $("copyToolResultBtn").addEventListener("click", (e) => copyTextToClipboard(e.target, data.result));
    $("saveToolResultBtn").addEventListener("click", (e) => toggleSaveToolRun(e.target, data.run_id));

    els.toolResultCard.hidden = false;
  } catch (err) {
    showToast(err.message);
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerText = "Сгенерировать";
    }
  }
}

async function toggleSaveToolRun(btn, runId) {
  if (!runId) return;
  try {
    const res = await request("/api/saved", {
      method: "POST",
      body: JSON.stringify({
        telegram_id: getTelegramUser().id,
        item_type: "tool_run",
        item_id: runId
      })
    });
    showToast(res.status === "saved" ? "Сохранено" : "Удалено");
    btn.classList.toggle("active", res.status === "saved");
  } catch (e) {
    showToast(e.message);
  }
}

/* ==========================================================================
   ИСТОРИЯ И ФИЛЬТРАЦИЯ С КАРТОЧКАМИ
   ========================================================================== */
async function loadHistory() {
  try {
    const data = await request(`/api/history?telegram_id=${getTelegramUser().id}`);
    state.history = data.history || [];
    renderHistory();
  } catch (err) {
    renderHistory();
  }
}

function renderHistory() {
  let items = state.history;
  if (state.historyFilter !== "all") {
    items = state.history.filter(h => h.type === state.historyFilter);
  }

  if (items.length === 0) {
    els.historyList.innerHTML = `<div class="empty-state"><p>Здесь появятся ваши результаты.</p></div>`;
    return;
  }

  els.historyList.innerHTML = items.map((h) => `
    <article class="history-card">
      <div class="avatar">${createIconSvg(h.type === "chat" ? "chat" : "tools")}</div>
      <div class="history-body">
        <strong>${escapeHtml(h.title || "Результат генерации")}</strong>
        <p>${escapeHtml(h.preview || "")}</p>
        <small>${h.date || ""}</small>
      </div>
    </article>
  `).join("");
}

/* ==========================================================================
   ПРОФИЛЬ, БИЛЛИНГ И ПЛАТЕЖНЫЕ ШЛЮЗЫ
   ========================================================================== */
function renderProfile() {
  if (!state.user) return;
  els.profileName.innerText = state.user.first_name || "Предприниматель";
  els.profileUsername.innerText = state.user.username ? `@${state.user.username}` : "";
  els.profilePlanBadge.innerText = (state.user.plan || "Free").toUpperCase();

  const used = state.user.used_today || 0;
  const max = state.user.daily_limit || 20;
  els.profileLimitsText.innerText = `${used} / ${max}`;
  const pct = Math.min(100, (used / max) * 100);
  els.profileLimitsBar.style.width = `${pct}%`;
}

async function loadBillingPlans() {
  try {
    const data = await request("/api/billing/plans");
    state.plans = data.plans || [];
  } catch (e) {
    state.plans = [
      { id: "free", name: "Free", price_text: "0 Stars", description: "Базовый доступ", limits_text: "20 запросов в день" },
      { id: "pro", name: "Pro", price_text: "299 Stars", description: "Для регулярной работы", limits_text: "300 запросов в день" },
      { id: "business", name: "Business", price_text: "999 Stars", description: "Для активной работы", limits_text: "1500 запросов в день" }
    ];
  }
}

function openBillingModal() {
  els.billingModal.hidden = false;
  renderBillingPlans();
}

function closeBillingModal() {
  els.billingModal.hidden = true;
}

function renderBillingPlans() {
  els.paymentProviderBox.hidden = true;
  els.billingPlanList.hidden = false;
  els.billingError.hidden = true;

  els.billingPlanList.innerHTML = state.plans.map((p) => {
    const isCurrent = state.user?.plan === p.id;
    return `
      <div class="plan-card ${isCurrent ? 'muted-plan' : ''}" data-plan-id="${p.id}">
        <div class="plan-main">
          <div class="avatar">${createIconSvg("wallet")}</div>
          <div>
            <h4>Тариф ${p.name} ${isCurrent ? '(Текущий)' : ''}</h4>
            <small>${p.description} • ${p.limits_text}</small>
          </div>
        </div>
        <button class="secondary compact" type="button" ${isCurrent ? 'disabled' : ''}>${p.price_text}</button>
      </div>
    `;
  }).join("");

  els.billingPlanList.querySelectorAll(".plan-card").forEach((card) => {
    card.addEventListener("click", () => {
      const planId = card.dataset.planId;
      if (state.user?.plan === planId) return;
      selectBillingPlan(planId);
    });
  });
}

async function selectBillingPlan(planId) {
  state.billingSelectedPlan = planId;
  els.billingPlanList.hidden = true;
  els.billingError.hidden = true;

  try {
    const data = await request(`/api/billing/status?telegram_id=${getTelegramUser().id}`);
    const providers = data.available_providers || ["Telegram Stars", "ЮKassa"];
    
    els.providerList.innerHTML = providers.map((prov) => `
      <button class="provider-card" type="button" data-provider="${prov}">
        <strong>${prov}</strong>
      </button>
    `).join("");

    els.providerList.querySelectorAll(".provider-card").forEach((btn) => {
      btn.addEventListener("click", () => createBillingOrder(planId, btn.dataset.provider));
    });

    els.paymentProviderBox.hidden = false;
  } catch (err) {
    els.billingError.innerText = err.message;
    els.billingError.hidden = false;
    els.billingPlanList.hidden = false;
  }
}

async function createBillingOrder(planId, provider) {
  els.billingError.hidden = true;
  try {
    const payload = {
      telegram_id: getTelegramUser().id,
      plan_id: planId,
      provider: provider
    };
    const order = await request("/api/billing/create-order", {
      method: "POST",
      body: JSON.stringify(payload)
    });

    if (order.payment_url) {
      if (tg && provider === "Telegram Stars") {
        tg.openInvoice(order.payment_url);
      } else {
        window.open(order.payment_url, "_blank");
      }
      showToast("Ссылка для оплаты открыта");
      closeBillingModal();
    } else {
      showToast("Ошибка формирования счёта");
    }
  } catch (err) {
    els.billingError.innerText = err.message;
    els.billingError.hidden = false;
  }
}

async function submitFeedback(itemId, itemType, context, message) {
  try {
    await request("/api/feedback", {
      method: "POST",
      body: JSON.stringify({
        telegram_id: getTelegramUser().id,
        item_id: itemId,
        item_type: itemType,
        context: context,
        message: message
      })
    });
    showToast("Отзыв успешно отправлен");
  } catch (e) {
    showToast("Не удалось отправить отзыв");
  }
}

function copyTextToClipboard(btn, text) {
  if (!navigator.clipboard) return;
  navigator.clipboard.writeText(text).then(() => {
    const oldText = btn.innerText;
    btn.innerText = "Скопировано";
    setTimeout(() => { btn.innerText = oldText; }, 2000);
  }).catch(() => {
    showToast("Не удалось скопировать");
  });
}

/* ==========================================================================
   ИВЕНТЫ И ЖИЗНЕННЫЙ ЦИКЛ ПРИЛОЖЕНИЯ
   ========================================================================== */
function bindEvents() {
  $("bottomNav").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-view]");
    if (button) switchView(button.dataset.view);
  });

  document.querySelectorAll("[data-open-view]").forEach((el) => {
    el.addEventListener("click", () => switchView(el.dataset.openView));
  });

  els.homeChatInput.addEventListener("input", () => {
    els.homeChatInput.style.height = "auto";
    els.homeChatInput.style.height = els.homeChatInput.scrollHeight + "px";
    updateChatSendButton();
  });

  els.homeCancelPromptBtn.addEventListener("click", () => {
    state.activePromptId = null;
    els.homeActivePromptRow.hidden = true;
    els.homeChatInput.value = "";
    updateChatSendButton();
  });

  els.homeChatForm.addEventListener("submit", handleChatSubmit);
  els.toolForm.addEventListener("submit", handleToolSubmit);

  els.toolBackBtn.addEventListener("click", () => {
    state.activeTool = null;
    renderTools();
  });

  $("submitAppFeedbackBtn")?.addEventListener("click", async (event) => {
    event.preventDefault();
    const message = $("appFeedbackText").value.trim();
    if (!message) {
      showToast("Напишите, что улучшить");
      return;
    }
    await submitFeedback(-1, "app", "profile", message);
    $("appFeedbackText").value = "";
  });

  $("openBillingBtn")?.addEventListener("click", openBillingModal);
  $("closeBillingBtn")?.addEventListener("click", closeBillingModal);
  $("backToPlansBtn")?.addEventListener("click", renderBillingPlans);
  
  els.billingModal?.addEventListener("click", (event) => {
    if (event.target === els.billingModal) closeBillingModal();
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

  els.headerProfileBtn?.addEventListener("click", () => switchView("profile"));
}

(async function boot() {
  injectIcons();
  initTelegram();
  bindEvents();
  renderPromptSuggestions();
  setupProfileHeader();
  updateChatSendButton();
  
  await Promise.all([loadTools(), loadBillingPlans()]);
  try {
    await loadMe();
  } catch (error) {
    showToast(error.message);
  }
  await Promise.all([loadHistory()]);
})();