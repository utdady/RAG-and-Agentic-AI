let messages = [];
let isLoading = false;

const welcomeScreen = document.getElementById("welcomeScreen");
const messagesContainer = document.getElementById("messagesContainer");
const loadingIndicator = document.getElementById("loadingIndicator");
const messagesEnd = document.getElementById("messagesEnd");
const clearBtn = document.getElementById("clearBtn");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const modelSelect = document.getElementById("modelSelect");
const sendButton = document.getElementById("sendButton");
const sendIcon = document.getElementById("sendIcon");
const loadingSpinner = document.getElementById("loadingSpinner");

document.addEventListener("DOMContentLoaded", function () {
  setupEventListeners();
  updateSendButton();
});

function setupEventListeners() {
  chatForm.addEventListener("submit", handleSubmit);
  clearBtn.addEventListener("click", clearChat);
  messageInput.addEventListener("input", handleInputChange);
  messageInput.addEventListener("keydown", handleKeyDown);
}

function handleSubmit(e) {
  e.preventDefault();
  const content = messageInput.value.trim();
  const model = modelSelect.value;
  if (!content || isLoading) return;
  sendMessage(content, model);
}

function handleKeyDown(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSubmit(e);
  }
}

function handleInputChange() {
  autoResizeTextarea();
  updateSendButton();
}

function autoResizeTextarea() {
  messageInput.style.height = "auto";
  messageInput.style.height = Math.min(messageInput.scrollHeight, 128) + "px";
}

function updateSendButton() {
  const hasContent = messageInput.value.trim().length > 0;
  sendButton.disabled = !hasContent || isLoading;
}

async function sendMessage(content, model) {
  const userMessage = {
    id: Date.now().toString(),
    content,
    type: "user",
    timestamp: new Date(),
  };
  messages.push(userMessage);
  displayMessage(userMessage);

  messageInput.value = "";
  messageInput.style.height = "auto";
  hideWelcomeScreen();
  showClearButton();
  setLoadingState(true);

  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: content, model }),
    });
    const data = await response.json();

    let text;
    if (data.error) {
      text = `Error: ${data.error}`;
    } else {
      const parts = [];
      if (data.summary) parts.push(`Summary: ${data.summary}`);
      if (data.sentiment !== undefined && data.sentiment !== null) {
        parts.push(`Sentiment: ${data.sentiment}/100`);
      }
      parts.push(data.response || "(no response)");
      text = parts.join("\n\n");
    }

    const aiMessage = {
      id: (Date.now() + 1).toString(),
      content: text,
      type: "ai",
      model: data.model_label || model,
      duration: data.duration,
      timestamp: new Date(),
    };
    messages.push(aiMessage);
    displayMessage(aiMessage);
  } catch (error) {
    const errorMessage = {
      id: (Date.now() + 1).toString(),
      content: `Error: ${error.message}`,
      type: "ai",
      model,
      timestamp: new Date(),
    };
    messages.push(errorMessage);
    displayMessage(errorMessage);
  } finally {
    setLoadingState(false);
  }
}

function displayMessage(message) {
  const messageEl = document.createElement("div");
  messageEl.className = `message ${message.type}`;

  const time = message.timestamp.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
  const modelBadge = message.model
    ? `<span class="message-model">${escapeHtml(message.model)}</span>`
    : "";
  const duration =
    message.duration !== undefined && message.duration !== null
      ? `<span>${Number(message.duration).toFixed(2)}s</span>`
      : "";

  messageEl.innerHTML = `
    <div class="message-wrapper">
      <div class="message-header">
        <div class="message-avatar">${message.type === "user" ? "U" : "AI"}</div>
        <div class="message-info">
          <span class="message-sender">${message.type === "user" ? "You" : "AI Assistant"}</span>
          ${modelBadge}
        </div>
      </div>
      <div class="message-bubble">
        <div class="message-text">${escapeHtml(message.content)}</div>
      </div>
      <div class="message-footer">
        <span>${time}</span>
        ${duration}
      </div>
    </div>
  `;

  messagesContainer.appendChild(messageEl);
  scrollToBottom();
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function setLoadingState(loading) {
  isLoading = loading;
  updateSendButton();
  messageInput.disabled = loading;
  if (loading) {
    loadingIndicator.style.display = "block";
    sendIcon.style.display = "none";
    loadingSpinner.style.display = "block";
    scrollToBottom();
  } else {
    loadingIndicator.style.display = "none";
    sendIcon.style.display = "inline";
    loadingSpinner.style.display = "none";
  }
}

function hideWelcomeScreen() {
  welcomeScreen.style.display = "none";
}

function showWelcomeScreen() {
  welcomeScreen.style.display = "flex";
}

function showClearButton() {
  clearBtn.style.display = "flex";
}

function hideClearButton() {
  clearBtn.style.display = "none";
}

function clearChat() {
  messages = [];
  messagesContainer.innerHTML = "";
  showWelcomeScreen();
  hideClearButton();
  setLoadingState(false);
  updateSendButton();
}

function scrollToBottom() {
  messagesEnd.scrollIntoView({ behavior: "smooth" });
}
