/**
 * FounderPilot AI - Core Frontend Logic
 * Premium Minimal Vanilla JavaScript Engine
 */

const tg = window.Telegram?.WebApp || null;

// Whitelist-словарь всех разрешенных иконок для безопасной вставки в innerHTML
const iconPaths = {
  home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
  chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7A8.4 8.4 0 0 1 4 11.5a8.5 8.5 0 0 1 17 0Z"/></svg>',
  tools: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>',
  history: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
  user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
  send: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
  close: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
  back: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>',
  copy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
  save: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyitalic points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>',
  edit: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
  trash: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
  warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
  'credit-card': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>',
  tg_stars: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
  ton: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>',
  btc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 9h6a2 2 0 0 1 2 2v0a2 2 0 0 1-2 2H8"/><path d="M8 13h7a2 2 0 0 1 2 2v0a2 2 0 0 1-2 2H8"/><line x1="10" y1="6" x2="10" y2="18"/><line x1="12" y1="6" x2="12" y2="18"/></svg>',
  chart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
  calculator: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2" ry="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="16" y1="14" x2="16" y2="18"/><path d="M16 10h.01"/><path d="M12 10h.01"/><path d="M8 10h.01"/><path d="M12 14h.01"/><path d="M8 14h.01"/><path d="M8 18h.01"/><path d="M12 18h.01"/></svg>',
  search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
  target: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
  link: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>'
};

// Единый глобальный стейт
const state = {
  user: null,
  tools: [],
  plans: {},
  history: [],
  messages: [],
  activeView: "home",
  activePlanKey: null,
  activePlan: null,
  historyFilter: "all",
  isSending: false,
  onboardingStep: 0,
  onboardingData: {},
  toastTimer: null
};

// Хелпер быстрого выбора элементов
const $ = (id) => document.getElementById(id);

// Экранирование HTML (Защита от XSS атак)
function escapeHTML(value) {
  if (!value) return "";
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;")
    .replace(/\//g, "&#x2F;");
}

// Получить валидный inline SVG по имени
function icon(name) {
  return iconPaths[name] || "";
}

// Инъекция безопасных иконок
function injectIcons(root = document) {
  root.querySelectorAll("[data-icon]").forEach((el) => {
    const key = el.dataset.icon;
    if (iconPaths[key]) {
      el.innerHTML = iconPaths[key];
    }
  });
}

// Инициализация Telegram WebApp среды
function initTelegram() {
  if (tg) {
    tg.ready();
    tg.expand();
    if (tg.setHeaderColor) tg.setHeaderColor(tg.themeParams?.bg_color || "#0a0a0c");
    document.body.classList.add("tg-theme");
  }
}

// Получение инфо о текущем ТГ-юзере
function getTelegramUser() {
  if (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) {
    return tg.initDataUnsafe.user;
  }
  return { id: 12345678, first_name: "Предприниматель", username: "founder" };
}

// Устойчивая обертка для сетевых запросов
async function apiRequest(url, options = {}) {
  const initData = tg ? tg.initData : "";
  options.headers = {
    ...options.headers,
    "Content-Type": "application/json",
    "X-Telegram-Init-Data": initData
  };
  
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`HTTP Error: ${response.status}`);
  }
  return await response.json();
}

// Защищенный вызов API с подавлением фатальных ошибок (Graceful Degradation)
async function apiTry(url, options = {}, fallbackValue = null) {
  try {
    return await apiRequest(url, options);
  } catch (err) {
    console.error(`Ошибка при запросе к ${url}:`, err);
    return fallbackValue;
  }
}

// Нативная система Toast уведомлений вместо alert()
function showToast(message, type = "info") {
  const toastNode = $("toast");
  if (!toastNode) return;
  
  clearTimeout(state.toastTimer);
  toastNode.className = `toast visible ${type}`;
  toastNode.textContent = message;
  
  state.toastTimer = setTimeout(() => {
    toastNode.classList.remove("visible");
  }, 3500);
}

// Переключение вкладок приложения (Внутренний роутинг)
function switchView(target) {
  state.activeView = target;
  
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  
  const targetView = $(`view-${target}`);
  if (targetView) targetView.classList.add("active");
  
  const navBtn = document.querySelector(`.nav-item[data-view="${target}"]`);
  if (navBtn) navBtn.classList.add("active");
  
  // Динамические заголовки
  const titles = { home: "Главная", tools: "Инструменты", history: "История", profile: "Профиль" };
  if ($("pageTitle")) $("pageTitle").textContent = titles[target] || "Сервис";
  
  if (target === "history") loadHistory();
  if (target === "tools") loadTools();
  if (target === "profile") renderProfile();
}

// Управление состоянием лоадинга на кнопках
function setLoading(button, isLoading) {
  if (!button) return;
  if (isLoading) {
    button.disabled = true;
    button.dataset.originalText = button.textContent;
    button.textContent = "Загрузка...";
  } else {
    button.disabled = false;
    if (button.dataset.originalText) {
      button.textContent = button.dataset.originalText;
    }
  }
}

// Автоматический ресайз textarea чата
function autoResizeTextarea(textarea) {
  if (!textarea) return;
  textarea.style.height = "auto";
  textarea.style.height = (textarea.scrollHeight) + "px";
}

// Обновление состояния кнопки отправки сообщения
function updateSendButton() {
  const input = $("homeChatInput");
  const btn = $("homeChatSendBtn");
  if (!input || !btn) return;
  btn.disabled = state.isSending || !input.value.trim();
}

// Безопасное добавление сообщений в DOM-дерево
function appendMessage(role, text, actions = false) {
  const scrollContainer = $("homeChatScroll");
  if (!scrollContainer) return;
  
  const emptyState = $("chatEmptyState");
  if (emptyState) emptyState.style.display = "none";
  
  const msgDiv = document.createElement("div");
  msgDiv.className = `msg ${role}`;
  
  // Вставляем безопасный экранированный текст
  const contentSpan = document.createElement("span");
  contentSpan.textContent = text;
  msgDiv.appendChild(contentSpan);
  
  // Кнопки действий для ответов ассистента
  if (actions && role === "bot") {
    const actionsDiv = document.createElement("div");
    actionsDiv.className = "message-actions";
    
    const copyBtn = document.createElement("button");
    copyBtn.textContent = "Скопировать";
    copyBtn.onclick = () => copyText(text);
    
    const saveBtn = document.createElement("button");
    saveBtn.textContent = "Сохранить";
    saveBtn.onclick = () => saveResult(text, "Результат генерации");
    
    const shorterBtn = document.createElement("button");
    shorterBtn.textContent = "Короче";
    shorterBtn.onclick = () => improveLastAnswer("Сделай короче");
    
    const longerBtn = document.createElement("button");
    longerBtn.textContent = "Подробнее";
    longerBtn.onclick = () => improveLastAnswer("Расскажи подробнее");
    
    actionsDiv.appendChild(copyBtn);
    actionsDiv.appendChild(saveBtn);
    actionsDiv.appendChild(shorterBtn);
    actionsDiv.appendChild(longerBtn);
    
    msgDiv.appendChild(actionsDiv);
  }
  
  scrollContainer.appendChild(msgDiv);
  scrollContainer.scrollTop = scrollContainer.scrollHeight;
}

// Отрисовка всей цепочки чата из стейта
function renderChat() {
  const scrollContainer = $("homeChatScroll");
  if (!scrollContainer) return;
  
  // Очистка кроме empty state
  scrollContainer.querySelectorAll(".msg").forEach(m => m.remove());
  
  if (state.messages.length === 0) {
    if ($("chatEmptyState")) $("chatEmptyState").style.display = "block";
    return;
  }
  
  if ($("chatEmptyState")) $("chatEmptyState").style.display = "none";
  
  state.messages.forEach((m, idx) => {
    const isLast = idx === state.messages.length - 1;
    appendMessage(m.role, m.text, isLast);
  });
}

// Отправка сообщений на бэкенд
async function sendChatMessage(text, options = {}) {
  if (!text || state.isSending) return;
  
  state.isSending = true;
  updateSendButton();
  
  state.messages.push({ role: "user", text: text });
  renderChat();
  
  if ($("homeChatInput")) {
    $("homeChatInput").value = "";
    autoResizeTextarea($("homeChatInput"));
  }
  
  // Добавление временного системного сообщения ожидания генерации
  appendMessage("system", "AI готовит ответ...");
  
  // Проверяем доступность /api/chat с автопереходом на /api/ask
  let result = null;
  const payload = { prompt: text, context: state.messages, ...options };
  
  try {
    result = await apiRequest("/api/chat", { method: "POST", body: JSON.stringify(payload) });
  } catch (e) {
    try {
      result = await apiRequest("/api/ask", { method: "POST", body: JSON.stringify({ message: text, ...options }) });
    } catch (err) {
      console.error("Оба эндпоинта отправки недоступны", err);
    }
  }
  
  // Удаляем сообщение ожидания
  const scrollContainer = $("homeChatScroll");
  if (scrollContainer && scrollContainer.lastChild) {
    scrollContainer.lastChild.remove();
  }
  
  state.isSending = false;
  updateSendButton();
  
  if (result && (result.answer || result.response || result.text)) {
    const aiText = result.answer || result.response || result.text;
    state.messages.push({ role: "bot", text: aiText });
    renderChat();
  } else {
    showToast("Не удалось получить ответ от ИИ. Проверьте соединение.", "error");
    if (state.messages.length > 0) {
      state.messages.pop(); // Удаляем последнее безответное сообщение
      renderChat();
    }
  }
}

// Корректировка последнего ответа ИИ
function improveLastAnswer(instruction) {
  const lastUserMsg = [...state.messages].reverse().find(m => m.role === "user");
  if (!lastUserMsg) return;
  sendChatMessage(lastUserMsg.text, { refinement: instruction });
}

// Нативное копирование текста в буфер обмена
function copyText(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text)
      .then(() => showToast("Текст скопирован в буфер обмена", "success"))
      .catch(() => showToast("Не удалось скопировать текст", "error"));
  } else {
    // Резервный метод для старых браузеров (Fallback)
    const area = document.createElement("textarea");
    area.value = text;
    area.style.position = "fixed";
    document.body.appendChild(area);
    area.select();
    try {
      document.execCommand("copy");
      showToast("Текст скопирован в буфер обмена", "success");
    } catch (e) {
      showToast("Не удалось скопировать", "error");
    }
    document.body.removeChild(area);
  }
}

// Сохранение результатов генерации
async function saveResult(content, title) {
  try {
    await apiRequest("/api/saved", { method: "POST", body: JSON.stringify({ content, title }) });
    showToast("Результат успешно сохранен", "success");
  } catch (e) {
    // Мягкий фоллбэк согласно ТЗ
    showToast("Сохранение временно недоступно", "info");
  }
}

// Загрузка данных аккаунта пользователя
async function loadMe() {
  const tgUser = getTelegramUser();
  const fallbackMe = {
    name: tgUser.first_name,
    username: tgUser.username || String(tgUser.id),
    plan_name: "Free",
    used_today: 0,
    limit_today: 10,
    business_profile: "",
    onboarding_required: false
  };
  
  state.user = await apiTry("/api/me", { method: "GET" }, fallbackMe);
  
  if ($("homeGreeting")) {
    $("homeGreeting").textContent = `Здравствуйте, ${state.user.name || "предприниматель"}`;
  }
  
  if (state.user.onboarding_required) {
    openOnboarding();
  }
}

// Обновление интерфейса профиля
function renderProfile() {
  if (!state.user) return;
  
  if ($("headerUserAvatar")) $("headerUserAvatar").textContent = (state.user.name || "FP").substring(0, 2).toUpperCase();
  if ($("profileUserAvatar")) $("profileUserAvatar").textContent = (state.user.name || "FP").substring(0, 2).toUpperCase();
  if ($("profileUserTitle")) $("profileUserTitle").textContent = state.user.name || "Пользователь";
  if ($("profilePlanLabel")) $("profilePlanLabel").textContent = state.user.plan_name || "Free";
  
  const used = state.user.used_today || 0;
  const limit = state.user.limit_today || 0;
  if ($("profileUsageText")) $("profileUsageText").textContent = `${used} / ${limit}`;
  
  if ($("profileUsageFill")) {
    const pct = limit > 0 ? Math.min(100, (used / limit) * 100) : 0;
    $("profileUsageFill").style.width = `${pct}%`;
  }
  
  if ($("profileBusinessDescription")) {
    $("profileBusinessDescription").value = state.user.business_profile || "";
  }
}

// Загрузка библиотеки инструментов ИИ
async function loadTools() {
  const defaultTools = [
    { id: "t1", title: "Расчёт маржинальности", description: "Быстрая юнит-экономика товара.", prompt_template: "Помоги рассчитать маржу товара. Вот исходные данные: " },
    { id: "t2", title: "Оптимизация карточки", description: "Генерация сильного SEO-описания.", prompt_template: "Улучши описание карточки товара для маркетплейса: " },
    { id: "t3", title: "Анализ конкурентов", description: "Разбор преимуществ и слабых мест.", prompt_template: "Сделай анализ конкурентов для следующей ниши: " }
  ];
  
  state.tools = await apiTry("/api/tools", { method: "GET" }, defaultTools);
  renderTools();
}

// Отрисовка сетки инструментов
function renderTools() {
  const grid = $("toolsGrid");
  if (!grid) return;
  
  grid.innerHTML = "";
  if (!state.tools || state.tools.length === 0) {
    grid.innerHTML = '<div class="empty-state">Инструменты временно недоступны.</div>';
    return;
  }
  
  state.tools.forEach(tool => {
    const row = document.createElement("div");
    row.className = "tool-item-row";
    
    // Подбор иконки по типу/id
    let currentIcon = "calculator";
    if (tool.id === "t2") currentIcon = "target";
    if (tool.id === "t3") currentIcon = "chart";
    
    row.innerHTML = `
      <div class="tool-icon-box">${icon(currentIcon)}</div>
      <div class="tool-text-box">
        <h4>${escapeHTML(tool.title)}</h4>
        <p>${escapeHTML(tool.description)}</p>
      </div>
    `;
    
    row.onclick = () => {
      switchView("home");
      if (tool.prompt_template && $("homeChatInput")) {
        $("homeChatInput").value = tool.prompt_template;
        $("homeChatInput").focus();
        autoResizeTextarea($("homeChatInput"));
        updateSendButton();
      }
    };
    
    grid.appendChild(row);
  });
}

// Загрузка истории генераций
async function loadHistory() {
  state.history = await apiTry("/api/history", { method: "GET" }, []);
  renderHistory();
}

// Отрисовка списка истории с учетом полифилла форматов
function renderHistory() {
  const container = $("historyList");
  if (!container) return;
  
  container.innerHTML = "";
  
  // Фильтрация данных по стейту фильтра
  let list = state.history || [];
  if (state.historyFilter === "chats") {
    list = list.filter(h => h.mode === "chat" || h.type === "chat");
  } else if (state.historyFilter === "tools") {
    list = list.filter(h => h.mode && h.mode !== "chat" || h.type === "tool");
  } else if (state.historyFilter === "saved") {
    list = list.filter(h => h.is_saved || h.type === "saved");
  }
  
  if (list.length === 0) {
    container.innerHTML = '<div class="empty-state">Здесь появятся ваши результаты.</div>';
    return;
  }
  
  list.forEach(item => {
    // Поддержка форматов old format и new format
    const title = item.title || item.mode || "Генерация";
    const preview = item.preview || item.text || item.answer || "";
    const rawDate = item.created_at || item.timestamp || "";
    
    let formattedDate = "";
    if (rawDate) {
      const d = new Date(rawDate);
      formattedDate = isNaN(d.getTime()) ? rawDate : d.toLocaleDateString("ru-RU");
    }
    
    const card = document.createElement("div");
    card.className = "history-row";
    card.innerHTML = `
      <h4>${escapeHTML(title)}</h4>
      <p>${escapeHTML(preview)}</p>
      <div class="meta">${escapeHTML(formattedDate)}</div>
    `;
    
    card.onclick = () => {
      // Клик по истории разворачивает элемент в чат
      switchView("home");
      state.messages = [
        { role: "user", text: item.text || item.title || "Исходный запрос" },
        { role: "bot", text: item.answer || item.content || preview }
      ];
      renderChat();
    };
    
    container.appendChild(card);
  });
}

// Мутатор фильтров истории
function setHistoryFilter(filter) {
  state.historyFilter = filter;
  document.querySelectorAll("#historyFilters .filter-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.filter === filter);
  });
  renderHistory();
}

// Загрузка биллинг-планов
async function loadBillingPlans() {
  const fallbackPlans = {
    plans: [
      { key: "free", title: "Free", description: "Базовые возможности ИИ", price_text: "0 ₽" },
      { key: "pro", title: "Pro", description: "Расширенный бизнес-анализ", price_text: "990 ₽/мес" },
      { key: "business", title: "Business", description: "Максимальные лимиты и приоритет", price_text: "2990 ₽/мес" }
    ],
    providers: [
      { id: "telegram_stars", name: "Telegram Stars", icon: "tg_stars" },
      { id: "yookassa", name: "ЮKassa / ЮMoney", icon: "credit-card" },
      { id: "ton", name: "TON / Tonkeeper", icon: "ton" },
      { id: "btc", name: "Bitcoin", icon: "btc" }
    ]
  };
  
  const res = await apiTry("/api/billing/plans", { method: "GET" }, fallbackPlans);
  state.plans = res;
}

// Открытие биллинг окна
function openBillingModal() {
  $("billingModal").hidden = false;
  $("paymentProviderBox").hidden = true;
  $("billingPlanList").hidden = false;
  $("billingError").hidden = true;
  renderBillingPlans();
}

function closeBillingModal() {
  $("billingModal").hidden = true;
}

// Рендер тарифов
function renderBillingPlans() {
  const container = $("billingPlanList");
  if (!container) return;
  
  container.innerHTML = "";
  const plansList = state.plans?.plans || [];
  
  if (plansList.length === 0) {
    container.innerHTML = '<div class="empty-state">Тарифы временно недоступны.</div>';
    return;
  }
  
  plansList.forEach(plan => {
    const card = document.createElement("div");
    card.className = "plan-item-row";
    card.setAttribute("data-plan-key", plan.key);
    card.innerHTML = `
      <h3>${escapeHTML(plan.title)}</h3>
      <p>${escapeHTML(plan.description)}</p>
      <div class="plan-price">${escapeHTML(plan.price_text)}</div>
    `;
    container.appendChild(card);
  });
}

// Клик по тарифу -> выбор шлюза
function selectPlan(planKey) {
  state.activePlanKey = planKey;
  state.activePlan = (state.plans?.plans || []).find(p => p.key === planKey);
  
  $("billingPlanList").hidden = true;
  $("paymentProviderBox").hidden = false;
  
  const container = $("providerList");
  if (!container) return;
  container.innerHTML = "";
  
  const providers = state.plans?.providers || [];
  providers.forEach(prov => {
    const row = document.createElement("div");
    row.className = "provider-item-row";
    row.setAttribute("data-provider", prov.id);
    
    row.innerHTML = `
      <div class="provider-icon">${icon(prov.icon || "credit-card")}</div>
      <div class="provider-info">
        <div class="provider-title">${escapeHTML(prov.name)}</div>
      </div>
      <div class="provider-price-tag">${escapeHTML(state.activePlan?.price_text)}</div>
    `;
    container.appendChild(row);
  });
}

// Запуск оплаты
async function checkout(providerId) {
  $("billingError").hidden = true;
  
  const payload = { plan: state.activePlanKey, provider: providerId };
  let orderData = null;
  
  try {
    orderData = await apiRequest("/api/billing/create-order", { method: "POST", body: JSON.stringify(payload) });
  } catch (e) {
    try {
      orderData = await apiRequest("/api/billing/checkout", { method: "POST", body: JSON.stringify(payload) });
    } catch (err) {
      $("billingError").textContent = "Не удалось инициировать оплату. Попробуйте позже.";
      $("billingError").hidden = false;
      return;
    }
  }
  
  if (!orderData) return;
  
  // Логика TON криптовалюты
  if (providerId === "ton") {
    if (orderData.payment_url || orderData.invoice_url) {
      if (tg) tg.openLink(orderData.payment_url || orderData.invoice_url);
      else window.open(orderData.payment_url || orderData.invoice_url, "_blank");
    }
    showToast("Оплата TON будет подтверждена после проверки транзакции.", "info");
    closeBillingModal();
    return;
  }
  
  // Логика Telegram Stars
  if (providerId === "telegram_stars" && orderData.invoice_link) {
    if (tg && tg.openInvoice) {
      tg.openInvoice(orderData.invoice_link, (status) => {
        if (status === "paid") showToast("Оплата прошла успешно!", "success");
        else if (status === "cancelled") showToast("Оплата отменена", "info");
        else showToast("Не удалось проверить оплату", "error");
        loadMe();
      });
    }
    closeBillingModal();
    return;
  }
  
  // Логика внешних шлюзов (ЮKassa, BTC)
  const targetUrl = orderData.invoice_url || orderData.payment_url || orderData.url;
  if (targetUrl) {
    if (tg) tg.openLink(targetUrl);
    else window.open(targetUrl, "_blank");
  }
  
  // Включение поллинга ордера при возврате order_id
  if (orderData.order_id) {
    showToast("Ожидаем оплату...", "info");
    pollOrderStatus(orderData.order_id);
  }
  
  closeBillingModal();
}

// Поллинг статуса транзакций
async function pollOrderStatus(orderId) {
  let counter = 0;
  const maxAttempts = 30;
  
  const timer = setInterval(async () => {
    counter++;
    if (counter > maxAttempts) {
      clearInterval(timer);
      showToast("Не удалось проверить оплату автоматически. Проверьте профиль.", "warning");
      return;
    }
    
    const statusData = await apiTry(`/api/billing/order/${orderId}`, { method: "GET" });
    if (statusData && statusData.status) {
      if (statusData.status === "paid" || statusData.status === "success") {
        clearInterval(timer);
        showToast("Оплата прошла успешно! Ваш тариф обновлен.", "success");
        loadMe();
      } else if (statusData.status === "cancelled" || statusData.status === "failed") {
        clearInterval(timer);
        showToast("Оплата отменена или отклонена бэкендом", "error");
      }
    }
  }, 4000);
}

// Онбординг
const onboardingStepsConfig = [
  {
    title: "Чем вы занимаетесь?",
    type: "select",
    key: "occupation",
    options: ["Селлер WB/Ozon", "Предприниматель", "Маркетолог", "Новичок", "Другое"]
  },
  {
    title: "Что хотите улучшить?",
    type: "select",
    key: "target",
    options: ["Продажи", "Карточки товара", "Рекламу", "Идеи товара", "Стратегию", "Расчёты"]
  },
  {
    title: "Коротко опишите бизнес",
    type: "textarea",
    key: "description",
    placeholder: "Ваши основные товары, текущие показатели и проблемы..."
  }
];

function openOnboarding() {
  state.onboardingStep = 0;
  state.onboardingData = {};
  $("onboardingModal").hidden = false;
  renderOnboardingStep();
}

function renderOnboardingStep() {
  const currentCfg = onboardingStepsConfig[state.onboardingStep];
  if (!currentCfg) return;
  
  $("onboardingTitle").textContent = currentCfg.title;
  $("onboardingError").hidden = true;
  
  // Прогресс бар бар-линии
  const progressRow = $("onboardingProgressRow");
  progressRow.innerHTML = "";
  onboardingStepsConfig.forEach((_, idx) => {
    const span = document.createElement("span");
    span.style.width = `calc(${100 / onboardingStepsConfig.length}% - 4px)`;
    if (idx <= state.onboardingStep) span.className = "active";
    progressRow.appendChild(span);
  });
  
  const body = $("onboardingBody");
  body.innerHTML = "";
  
  if (currentCfg.type === "select") {
    currentCfg.options.forEach(opt => {
      const btn = document.createElement("button");
      btn.className = "onboarding-option";
      if (state.onboardingData[currentCfg.key] === opt) btn.classList.add("active");
      btn.textContent = opt;
      btn.onclick = () => {
        state.onboardingData[currentCfg.key] = opt;
        renderOnboardingStep();
      };
      body.appendChild(btn);
    });
  } else if (currentCfg.type === "textarea") {
    const tx = document.createElement("textarea");
    tx.className = "profile-textarea";
    tx.placeholder = currentCfg.placeholder;
    tx.value = state.onboardingData[currentCfg.key] || "";
    tx.oninput = (e) => { state.onboardingData[currentCfg.key] = e.target.value; };
    body.appendChild(tx);
  }
  
  $("onboardingBackBtn").style.visibility = state.onboardingStep === 0 ? "hidden" : "visible";
  $("onboardingNextBtn").textContent = state.onboardingStep === onboardingStepsConfig.length - 1 ? "Готово" : "Далее";
}

async function nextOnboarding() {
  const currentCfg = onboardingStepsConfig[state.onboardingStep];
  if (!state.onboardingData[currentCfg.key]) {
    $("onboardingError").textContent = "Пожалуйста, заполните или выберите ответ";
    $("onboardingError").hidden = false;
    return;
  }
  
  if (state.onboardingStep < onboardingStepsConfig.length - 1) {
    state.onboardingStep++;
    renderOnboardingStep();
  } else {
    // Финал онбординга
    setLoading($("onboardingNextBtn"), true);
    try {
      await apiRequest("/api/onboarding", { method: "POST", body: JSON.stringify(state.onboardingData) });
      showToast("Профиль успешно настроен", "success");
    } catch (e) {
      showToast("Профиль можно заполнить позже.", "info");
    }
    setLoading($("onboardingNextBtn"), false);
    $("onboardingModal").hidden = true;
    loadMe();
  }
}

function previousOnboarding() {
  if (state.onboardingStep > 0) {
    state.onboardingStep--;
    renderOnboardingStep();
  }
}

// Сохранение кастомного контекста бизнес-профиля
async function saveBusinessProfile() {
  const desc = $("profileBusinessDescription")?.value || "";
  setLoading($("saveProfileBtn"), true);
  try {
    await apiRequest("/api/profile/save", { method: "POST", body: JSON.stringify({ business_profile: desc }) });
    showToast("Бизнес-профиль успешно сохранен", "success");
    if (state.user) state.user.business_profile = desc;
  } catch (e) {
    showToast("Не удалось сохранить профиль", "error");
  }
  setLoading($("saveProfileBtn"), false);
}

// Отправка формы обратной связи
async function submitFeedback() {
  const text = $("appFeedbackText")?.value || "";
  if (!text.trim()) {
    showToast("Пожалуйста, введите текст сообщения", "warning");
    return;
  }
  setLoading($("submitAppFeedbackBtn"), true);
  try {
    await apiRequest("/api/feedback", { method: "POST", body: JSON.stringify({ text }) });
    showToast("Отзыв успешно отправлен. Спасибо!", "success");
    if ($("appFeedbackText")) $("appFeedbackText").value = "";
  } catch (e) {
    showToast("Не удалось отправить обратную связь", "error");
  }
  setLoading($("submitAppFeedbackBtn"), false);
}

// Привязка слушателей событий и обработчиков элементов
function bindEvents() {
  // Навигационный бар
  document.querySelectorAll(".app-nav .nav-item").forEach(item => {
    item.addEventListener("click", () => switchView(item.dataset.view));
  });
  
  // Клик по аватару в шапке открывает профиль
  $("headerProfileBtn")?.addEventListener("click", () => switchView("profile"));
  
  // Быстрые подсказки-chips на главном экране
  $("quickStrip")?.addEventListener("click", (e) => {
    const actionBtn = e.target.closest(".quick-action");
    if (actionBtn && actionBtn.dataset.prompt) {
      sendChatMessage(actionBtn.dataset.prompt);
    }
  });
  
  // Логика авторесайза и отправки по Enter (без Shift)
  const chatInput = $("homeChatInput");
  if (chatInput) {
    chatInput.addEventListener("input", () => {
      autoResizeTextarea(chatInput);
      updateSendButton();
    });
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        const txt = chatInput.value.trim();
        if (txt && !state.isSending) sendChatMessage(txt);
      }
    });
  }
  
  $("homeChatSendBtn")?.addEventListener("click", () => {
    const txt = $("homeChatInput")?.value.trim();
    if (txt) sendChatMessage(txt);
  });
  
  // Фильтры экрана истории
  $("historyFilters")?.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-filter]");
    if (btn) setHistoryFilter(btn.dataset.filter);
  });
  
  // Кнопки управления биллингом
  $("openBillingBtn")?.addEventListener("click", openBillingModal);
  $("closeBillingBtn")?.addEventListener("click", closeBillingModal);
  $("backToPlansBtn")?.addEventListener("click", renderBillingPlans);
  
  $("billingPlanList")?.addEventListener("click", (e) => {
    const card = e.target.closest("[data-plan-key]");
    if (card) selectPlan(card.dataset.planKey);
  });
  
  $("providerList")?.addEventListener("click", (e) => {
    const row = e.target.closest("[data-provider]");
    if (row) checkout(row.dataset.provider);
  });
  
  // События онбординга
  $("onboardingNextBtn")?.addEventListener("click", nextOnboarding);
  $("onboardingBackBtn")?.addEventListener("click", previousOnboarding);
  
  // События кнопок в профиле
  $("saveProfileBtn")?.addEventListener("click", saveBusinessProfile);
  $("submitAppFeedbackBtn")?.addEventListener("click", submitFeedback);
}

// Точка входа boot приложения
(async function boot() {
  injectIcons();
  initTelegram();
  bindEvents();
  
  // Конкурентный параллельный асинхронный запуск без блокировки интерфейса (Resilient Boot)
  await Promise.all([
    loadMe().then(() => renderProfile()),
    loadTools(),
    loadBillingPlans()
  ]);
})();