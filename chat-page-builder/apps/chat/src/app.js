// Chat with the chat-assistant agent; pages it links to open in the panel.
// A page is any link to /i/<instance id>/ on an app host, usually an embed link
// that signs the panel in as the same visitor.
import { marked } from "/vendor/marked.js";
import DOMPurify from "/vendor/purify.js";

const $ = (id) => document.getElementById(id);
const el = {
  appName: $("app-name"),
  status: $("status"),
  user: $("user"),
  logout: $("logout"),
  newChat: $("new-chat"),
  scroll: $("scroll"),
  welcome: $("welcome"),
  ideas: $("ideas"),
  messages: $("messages"),
  form: $("composer"),
  input: $("input"),
  send: $("send"),
  panel: $("panel"),
  pageTitle: $("page-title"),
  pageVersion: $("page-version"),
  switcher: $("switcher"),
  pages: $("pages"),
  reload: $("reload"),
  openTab: $("open-tab"),
  closePanel: $("close-panel"),
  frame: $("frame"),
  frameLoading: $("frame-loading"),
};

const IDEAS = [
  ["Sales dashboard", "A sales dashboard for a small coffee chain with six stores: revenue by month, best-selling products and a store ranking. Use sample data."],
  ["Mortgage calculator", "A mortgage calculator with sliders for price, down payment, rate and term, and a chart of interest against principal over time."],
  ["Habit tracker", "A habit tracker for three habits where I tick off days. Save my check-ins so they are still there tomorrow."],
  ["Compare options", "A table and chart comparing three laptops on price, weight, battery life and screen size, with my pick highlighted."],
];

const STEPS = {
  trigger_agent: "Designing the page",
  db_find: "Reading your data",
  db_count: "Reading your data",
  db_insert: "Saving your data",
  db_update: "Saving your data",
  db_delete: "Removing data",
};

const PAGE_LINK = /^https?:\/\/[^/]+\/i\/([0-9a-f-]{36})\//i;
const CHAT_KEY = "chat-conversation";
const PAGE_ICON =
  '<svg viewBox="0 0 24 24" aria-hidden="true"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>';

let socket = null;
let connector = null;
let reconnectDelay = 1000;
let state = { messages: [], pages: [], open: null };
let pending = null;

function storedId(key) {
  let id = sessionStorage.getItem(key);
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem(key, id);
  }
  return id;
}

const conversationId = () => storedId(CHAT_KEY);
// One connection ID per tab: replies that finish while the socket is down arrive after reconnecting.
const connectionId = () => storedId("chat-connection");

const stateKey = () => `chat-state:${conversationId()}`;
const save = () => sessionStorage.setItem(stateKey(), JSON.stringify(state));

function setStatus(text, kind) {
  el.status.textContent = text;
  el.status.dataset.state = kind;
  el.status.hidden = kind === "online";
  updateSend();
}

function updateSend() {
  el.send.disabled = el.status.dataset.state !== "online" || pending !== null || !el.input.value.trim();
}

function scrollToEnd() {
  el.scroll.scrollTop = el.scroll.scrollHeight;
}

// Pages

function trackPage(url, title) {
  const instance = url.match(PAGE_LINK)[1];
  let page = state.pages.find((item) => item.instance === instance);
  if (!page) {
    page = { instance, url, title, version: 1 };
    state.pages.push(page);
  } else if (page.url !== url) {
    // Each publish returns a fresh link, so a new link means a new version.
    Object.assign(page, { url, title: title || page.title, version: page.version + 1 });
  }
  return page;
}

function openPage(instance) {
  const page = state.pages.find((item) => item.instance === instance);
  if (!page) return;
  const reload = state.open !== instance || el.frame.dataset.url !== page.url;
  state.open = instance;
  save();
  el.panel.hidden = false;
  el.pageTitle.textContent = page.title;
  el.pageVersion.textContent = `Version ${page.version}`;
  el.openTab.href = page.url;
  el.pages.replaceChildren(
    ...state.pages.map((item) => new Option(item.title, item.instance, false, item.instance === instance)),
  );
  el.switcher.hidden = state.pages.length < 2;
  el.pageTitle.hidden = state.pages.length >= 2;
  if (reload) loadFrame(page.url);
  for (const card of document.querySelectorAll(".page-card")) {
    card.setAttribute("aria-current", String(card.dataset.instance === instance));
  }
}

function loadFrame(url) {
  el.frameLoading.hidden = false;
  el.frame.dataset.url = url;
  el.frame.src = url;
}

function closePage() {
  state.open = null;
  save();
  el.panel.hidden = true;
  for (const card of document.querySelectorAll(".page-card")) card.setAttribute("aria-current", "false");
}

function pageCard(page) {
  const card = document.createElement("button");
  card.type = "button";
  card.className = "page-card";
  card.dataset.instance = page.instance;
  card.setAttribute("aria-current", String(state.open === page.instance));
  card.innerHTML = `<span class="tile">${PAGE_ICON}</span><span class="text"><span class="title"></span><span class="meta"></span></span>`;
  card.querySelector(".title").textContent = page.title;
  card.querySelector(".meta").textContent = `Version ${page.version} · Open`;
  card.addEventListener("click", () => openPage(page.instance));
  return card;
}

// Messages

function renderMarkdown(target, text, { final }) {
  target.innerHTML = DOMPurify.sanitize(marked.parse(text, { breaks: true }), {
    FORBID_TAGS: ["img", "style", "form", "input", "button"],
  });
  const opened = [];
  for (const link of target.querySelectorAll("a[href]")) {
    const match = link.href.match(PAGE_LINK);
    if (!match) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      continue;
    }
    if (!final) {
      link.removeAttribute("href");
      continue;
    }
    const label = link.textContent.trim();
    const page = trackPage(link.href, label && label !== link.href ? label : "Page");
    const card = pageCard(page);
    // A link alone in its paragraph becomes the card; a link inside a sentence keeps its text.
    const parent = link.parentElement;
    if (parent.tagName === "P" && parent.textContent.trim() === label) parent.replaceWith(card);
    else link.replaceWith(card);
    opened.push(page);
  }
  return opened;
}

function addMessage(role, text = "") {
  el.welcome.hidden = true;
  const item = document.createElement("li");
  item.className = `message ${role}`;
  if (role === "assistant") renderMarkdown(item, text, { final: true });
  else item.textContent = text;
  el.messages.append(item);
  return item;
}

function remember(role, text) {
  state.messages.push({ role, text });
  save();
}

function startReply() {
  const item = document.createElement("li");
  item.className = "message assistant";
  const progress = document.createElement("div");
  progress.className = "progress";
  progress.innerHTML = '<span class="spinner" aria-hidden="true"></span><span class="label">Thinking</span><span class="elapsed"></span>';
  item.append(progress);
  el.messages.append(item);
  pending = { item, progress, text: "", frame: 0, step: null, since: 0, timer: 0 };
  updateSend();
  scrollToEnd();
}

function setStep(label) {
  if (!pending) return;
  const elapsed = pending.progress.querySelector(".elapsed");
  pending.progress.querySelector(".label").textContent = label;
  clearInterval(pending.timer);
  elapsed.textContent = "";
  // The page designer takes a minute or two; show how long it has been working.
  if (label === STEPS.trigger_agent) {
    const since = Date.now();
    pending.timer = setInterval(() => {
      const seconds = Math.floor((Date.now() - since) / 1000);
      elapsed.textContent = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
    }, 1000);
  }
}

function streamText(chunk) {
  if (!pending) startReply();
  pending.text += chunk;
  pending.frame ||= requestAnimationFrame(() => {
    pending.frame = 0;
    const body = pending.item.querySelector(".body") ?? pending.item.insertBefore(document.createElement("div"), pending.progress);
    body.className = "body";
    renderMarkdown(body, pending.text, { final: false });
    scrollToEnd();
  });
}

function finishReply(text, error) {
  const reply = pending ?? (startReply(), pending);
  clearInterval(reply.timer);
  cancelAnimationFrame(reply.frame);
  pending = null;
  updateSend();
  if (error) {
    reply.item.className = "message error";
    reply.item.textContent = error;
    remember("error", error);
    return;
  }
  const opened = renderMarkdown(reply.item, text, { final: true });
  remember("assistant", text);
  if (opened.length) openPage(opened.at(-1).instance);
  scrollToEnd();
}

function handleEvent(event) {
  switch (event.type) {
    case "connected":
      reconnectDelay = 1000;
      setStatus("Connected", "online");
      if (pending) setStep("Waiting for the reply");
      break;
    case "ping":
      socket.send(JSON.stringify({ type: "pong" }));
      break;
    case "thinking":
      setStep("Thinking");
      break;
    case "tool_call":
      setStep(STEPS[event.tool] ?? "Working");
      break;
    case "stream_chunk":
      streamText(event.chunk);
      break;
    case "stream_end":
      finishReply(pending?.text || event.full_response || "", event.error);
      break;
    case "response":
      finishReply(event.response ?? "", event.error);
      break;
    case "error":
      finishReply("", event.error || "Something went wrong. Try again.");
      break;
  }
}

// Connection

function signIn() {
  location.href = `/_connic/login?return=${encodeURIComponent(location.pathname)}`;
}

async function loadJson(path) {
  const response = await fetch(path);
  if (response.status === 401) {
    signIn();
    throw new Error("Sign-in required");
  }
  return response.json();
}

function connect() {
  setStatus("Connecting", "connecting");
  const protocol = location.protocol === "https:" ? "wss:" : "ws:";
  socket = new WebSocket(`${protocol}//${location.host}/_connic/c/${connector}/${connectionId()}`);
  socket.addEventListener("message", (message) => handleEvent(JSON.parse(message.data)));
  socket.addEventListener("close", async (event) => {
    // 4009: the same chat connected from another tab, which now gets the replies.
    if (event.code === 4009) {
      setStatus("Open in another tab", "offline");
      if (pending) finishReply("", "This chat continued in another tab.");
      return;
    }
    setStatus("Reconnecting", "offline");
    if (pending) setStep("Reconnecting");
    const session = await fetch("/_connic/me").catch(() => null);
    if (session?.status === 401) return signIn();
    setTimeout(connect, reconnectDelay);
    reconnectDelay = Math.min(reconnectDelay * 2, 15000);
  });
}

function send(text) {
  if (socket?.readyState !== WebSocket.OPEN || pending) return;
  addMessage("user", text);
  remember("user", text);
  startReply();
  socket.send(JSON.stringify({
    type: "message",
    id: crypto.randomUUID(),
    payload: { message: text, conversation_id: conversationId() },
  }));
}

function restore() {
  state = JSON.parse(sessionStorage.getItem(stateKey()) || "null") ?? { messages: [], pages: [], open: null };
  const open = state.open;
  state.pages = [];
  for (const message of state.messages) addMessage(message.role, message.text);
  if (open) openPage(open);
  scrollToEnd();
}

function reset() {
  sessionStorage.removeItem(CHAT_KEY);
  state = { messages: [], pages: [], open: null };
  el.messages.replaceChildren();
  el.welcome.hidden = false;
  closePage();
  el.frame.removeAttribute("src");
  delete el.frame.dataset.url;
  el.input.focus();
}

el.ideas.append(
  ...IDEAS.map(([title, prompt]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.innerHTML = "<strong></strong><span></span>";
    button.querySelector("strong").textContent = title;
    button.querySelector("span").textContent = prompt;
    button.addEventListener("click", () => send(prompt));
    return button;
  }),
);

el.form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = el.input.value.trim();
  if (!text || el.send.disabled) return;
  send(text);
  el.input.value = "";
  el.input.style.height = "";
  updateSend();
});

el.input.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    el.form.requestSubmit();
  }
});

el.input.addEventListener("input", () => {
  el.input.style.height = "";
  el.input.style.height = `${el.input.scrollHeight}px`;
  updateSend();
});

el.frame.addEventListener("load", () => {
  el.frameLoading.hidden = true;
});
el.pages.addEventListener("change", () => openPage(el.pages.value));
el.reload.addEventListener("click", () => {
  const page = state.pages.find((item) => item.instance === state.open);
  if (page) loadFrame(page.url);
});
el.closePanel.addEventListener("click", closePage);
el.newChat.addEventListener("click", reset);

restore();

const [config, me] = await Promise.all([loadJson("/_connic/config.json"), loadJson("/_connic/me")]);
el.appName.textContent = config.app.name;
document.title = config.app.name;
if (me.user?.signed_in) el.user.textContent = me.user.name || me.user.email;
if (config.logout_url) {
  el.logout.href = config.logout_url;
  el.logout.hidden = false;
}
connector = config.connectors[0];
if (connector) connect();
else setStatus("No connector in apps/chat.yaml", "offline");
