<template>
  <div class="chat-wrapper">
    <div class="chat-header">
      <div class="header-title">
        <div class="ai-badge">AI</div>
        <div>
          <h3>Assistant</h3>
          <p>ITK LostFound</p>
        </div>
      </div>
      <div class="status-dot"></div>
    </div>

    <!-- Messages Area -->
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="chat-empty">
        <div class="empty-brand">
          <span class="empty-lost">LOST</span>
          <span class="empty-found">FOUND</span>
        </div>
        <p class="empty-desc">Tanya apapun tentang barang hilang & ditemukan</p>
        
        <div class="chat-suggestions">
          <button v-for="s in suggestions" :key="s" @click="sendSuggestion(s)" class="suggestion-btn">
            {{ s }}
            <span class="arrow">→</span>
          </button>
        </div>
      </div>

      <div v-for="(msg, i) in messages" :key="i" :class="['chat-msg', msg.role]">
        <div v-if="msg.role === 'ai'" class="msg-avatar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"/><circle cx="9" cy="13" r="1" fill="currentColor"/><circle cx="15" cy="13" r="1" fill="currentColor"/><path d="M9 17h6"/></svg>
        </div>
        <div class="msg-content">
          <pre class="msg-text">{{ msg.text }}</pre>
          <span class="msg-time">{{ msg.time }}</span>
        </div>
      </div>

      <div v-if="loading" class="chat-msg ai">
        <div class="msg-avatar">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z"/><circle cx="9" cy="13" r="1" fill="currentColor"/><circle cx="15" cy="13" r="1" fill="currentColor"/><path d="M9 17h6"/></svg>
        </div>
        <div class="msg-content">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <form @submit.prevent="sendMessage" class="chat-input-form">
      <input
        v-model="input"
        type="text"
        placeholder="Ketik perintah..."
        class="chat-input"
        :disabled="loading"
      />
      <button type="submit" class="chat-send-btn" :disabled="loading || !input.trim()">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import api from '../services/api.js'

const emit = defineEmits(['data-changed'])

const messages = ref([])
const input = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

const suggestions = [
  'Lihat laporan terbaru',
  'Laporkan dompet hilang di Gedung A, pelapor Budi',
  'Cari barang elektronik yang ditemukan',
  'Cocokkan barang hilang dan ditemukan',
]

function getTime() {
  return new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
}

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

async function sendSuggestion(text) {
  input.value = text
  await sendMessage()
}

async function sendMessage() {
  const text = input.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', text, time: getTime() })
  input.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const res = await api.post('/api/ai/chat', { message: text })
    messages.value.push({
      role: 'ai',
      text: res.data.response,
      time: getTime(),
    })
    emit('data-changed', res.data.tools_used)
  } catch (err) {
    messages.value.push({
      role: 'ai',
      text: 'Error connecting to backend.',
      time: getTime(),
    })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

const sendMessageExt = async (text) => {
  input.value = text;
  await sendMessage();
};
defineExpose({ sendMessageExt });
</script>

<style scoped>
.chat-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 500px;
  width: 100%;
  background: var(--color-white);
  border-radius: var(--radius-lg);
  overflow: hidden;
  color: var(--color-black);
  box-shadow: var(--shadow-md);
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 20px 24px;
  background: var(--gradient-dark);
  color: var(--color-white);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-badge {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: var(--gradient-primary);
  font-size: 13px;
  font-weight: var(--font-weight-heavy);
  letter-spacing: 0.05em;
}

.header-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: var(--font-weight-heavy);
  text-transform: uppercase;
  letter-spacing: -0.02em;
  line-height: 1;
}

.header-title p {
  margin: 3px 0 0;
  font-size: 10px;
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.6;
}

.status-dot {
  margin-left: auto;
  width: 10px;
  height: 10px;
  background-color: #00FF40;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(0,255,64,0.5);
  animation: pulse 2s infinite;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--color-light-gray);
  min-height: 0;
}

.chat-empty {
  display: flex;
  flex-direction: column;
  height: 100%;
  justify-content: center;
}

.empty-brand {
  display: flex;
  flex-direction: column;
  margin-bottom: 8px;
}

.empty-lost {
  font-size: 72px;
  font-weight: 900;
  line-height: 0.85;
  letter-spacing: -0.05em;
  color: var(--color-lost);
  opacity: 0.15;
}

.empty-found {
  font-size: 72px;
  font-weight: 900;
  line-height: 0.85;
  letter-spacing: -0.05em;
  color: var(--color-found);
  opacity: 0.15;
}

.empty-desc {
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  color: var(--color-dark-gray);
  margin-bottom: 24px;
}

.chat-suggestions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.suggestion-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: var(--color-white);
  border: 1.5px solid var(--color-gray);
  border-radius: var(--radius-md);
  color: var(--color-black);
  font-weight: var(--font-weight-bold);
  font-size: 13px;
  text-align: left;
  cursor: pointer;
  transition: all 0.25s;
}

.suggestion-btn:hover {
  background: var(--color-black);
  color: var(--color-white);
  border-color: var(--color-black);
  transform: translateX(4px);
}

.suggestion-btn .arrow {
  font-size: 16px;
  transition: transform 0.25s;
}

.suggestion-btn:hover .arrow {
  transform: translateX(4px);
}

.chat-msg {
  display: flex;
  gap: 10px;
  animation: slideIn 0.3s ease;
}

.chat-msg.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-dark);
  color: var(--color-white);
  border-radius: 10px;
  align-self: flex-end;
  margin-bottom: 4px;
  flex-shrink: 0;
}

.msg-content {
  max-width: 85%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.chat-msg.user .msg-content {
  align-items: flex-end;
}

.msg-text {
  padding: 14px 18px;
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  line-height: 1.5;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  border-radius: var(--radius-md);
}

.chat-msg.user .msg-text {
  background: var(--gradient-dark);
  color: var(--color-white);
  border-bottom-right-radius: 4px;
}

.chat-msg.ai .msg-text {
  background: var(--color-white);
  color: var(--color-black);
  border: 1.5px solid var(--color-gray);
  border-top-left-radius: 4px;
  box-shadow: var(--shadow-sm);
}

.msg-time {
  font-size: 10px;
  font-weight: var(--font-weight-bold);
  color: var(--color-dark-gray);
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 18px;
  background: var(--color-white);
  border: 1.5px solid var(--color-gray);
  border-radius: var(--radius-md);
  border-top-left-radius: 4px;
}

.typing-indicator span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-dark-gray);
  animation: blink 1.4s infinite both;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

/* Input Form */
.chat-input-form {
  position: relative;
  display: flex;
  padding: 20px;
  border-top: 1.5px solid var(--color-gray);
  background: var(--color-white);
  align-items: center;
}

.chat-input {
  width: 100%;
  box-sizing: border-box;
  padding: 14px 60px 14px 20px;
  border: 1.5px solid var(--color-gray);
  border-radius: var(--radius-pill);
  background: var(--color-light-gray);
  color: var(--color-black);
  font-size: 15px;
  font-weight: var(--font-weight-medium);
  outline: none;
  transition: border-color 0.25s, box-shadow 0.25s;
}

.chat-input::placeholder {
  color: var(--color-dark-gray);
  font-weight: var(--font-weight-medium);
}

.chat-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(16,185,129,0.08);
}

.chat-send-btn {
  position: absolute;
  right: 32px;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: var(--gradient-primary);
  color: var(--color-white);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.chat-send-btn:hover:not(:disabled) {
  transform: scale(1.08);
  box-shadow: 0 4px 16px rgba(16,185,129,0.3);
}

.chat-send-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
</style>
