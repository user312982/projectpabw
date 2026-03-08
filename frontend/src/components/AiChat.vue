<template>
  <div class="chat-wrapper">
    <div class="chat-header">
      <div class="header-title">
        <h3>Action Log</h3>
        <p>Command Line Interface</p>
      </div>
      <div class="status-dot"></div>
    </div>

    <!-- Messages Area -->
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="messages.length === 0" class="chat-empty">
        <h2 class="empty-title">SYS<br>CMD</h2>
        
        <div class="chat-suggestions">
          <button v-for="s in suggestions" :key="s" @click="sendSuggestion(s)" class="suggestion-btn">
            {{ s }}
            <span class="arrow">→</span>
          </button>
        </div>
      </div>

      <div v-for="(msg, i) in messages" :key="i" :class="['chat-msg', msg.role]">
        <div v-if="msg.role === 'ai'" class="msg-avatar-text">SYS</div>
        <div class="msg-content">
          <pre class="msg-text">{{ msg.text }}</pre>
          <span class="msg-time">{{ msg.time }}</span>
        </div>
      </div>

      <div v-if="loading" class="chat-msg ai">
        <div class="msg-avatar-text">SYS</div>
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
        placeholder="Type a command..."
        class="chat-input"
        :disabled="loading"
      />
      <button type="submit" class="chat-send-btn" :disabled="loading || !input.trim()">
        ↑
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
  'Lihat semua produk',
  'Tambah produk Kopi harga 75000 stok 100',
  'Buatkan faktur Toko Makmur: 5 Kopi',
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
    emit('data-changed')
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
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 24px;
  border-bottom: 2px solid var(--color-black);
  background: var(--color-white);
}

.header-title h3 {
  margin: 0;
  font-size: 20px;
  font-weight: var(--font-weight-heavy);
  text-transform: uppercase;
  letter-spacing: -0.02em;
  line-height: 1;
}

.header-title p {
  margin: 4px 0 0;
  font-size: 10px;
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-dark-gray);
}

.status-dot {
  margin-left: auto;
  width: 12px;
  height: 12px;
  background-color: #00FF40; /* Neon green indicator */
  border-radius: 50%;
  border: 2px solid var(--color-black);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background: var(--bg-color);
  min-height: 0; /* Important for flex-child scrolling */
}

.chat-empty {
  display: flex;
  flex-direction: column;
  height: 100%;
  justify-content: center;
}

.empty-title {
  font-size: 80px;
  line-height: 0.85;
  letter-spacing: -0.05em;
  margin: 0 0 32px 0;
  color: var(--color-black);
}

.chat-suggestions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--color-white);
  border: 2px solid var(--color-black);
  border-radius: var(--radius-md);
  color: var(--color-black);
  font-weight: var(--font-weight-bold);
  font-size: 14px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-btn:hover {
  background: var(--color-black);
  color: var(--color-white);
}

.suggestion-btn .arrow {
  font-size: 18px;
}

.chat-msg {
  display: flex;
  gap: 12px;
  animation: slideIn 0.3s ease;
}

.chat-msg.user {
  flex-direction: row-reverse;
}

.msg-avatar-text {
  font-size: 10px;
  font-weight: var(--font-weight-heavy);
  padding: 4px 8px;
  background: var(--color-black);
  color: var(--color-white);
  border-radius: 4px;
  align-self: flex-end;
  margin-bottom: 4px;
}

.msg-content {
  max-width: 85%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-msg.user .msg-content {
  align-items: flex-end;
}

.msg-text {
  padding: 16px 20px;
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
  background: var(--color-black);
  color: var(--color-white);
  border-bottom-right-radius: 4px;
}

.chat-msg.ai .msg-text {
  background: var(--color-white);
  color: var(--color-black);
  border: 2px solid var(--color-black);
  border-top-left-radius: 4px;
}

.msg-time {
  font-size: 10px;
  font-weight: var(--font-weight-bold);
  color: var(--color-dark-gray);
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 6px;
  padding: 20px;
  background: var(--color-white);
  border: 2px solid var(--color-black);
  border-radius: var(--radius-md);
  border-top-left-radius: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-black);
  animation: blink 1.4s infinite both;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

/* Input Form */
.chat-input-form {
  position: relative;
  display: flex;
  padding: 24px;
  border-top: 2px solid var(--color-black);
  background: var(--color-white);
  align-items: center;
}

.chat-input {
  width: 100%;
  box-sizing: border-box; /* ensure padding doesn't burst width */
  padding: 16px 80px 16px 20px; /* Big right padding for the absolute button */
  border: 2px solid var(--color-gray);
  border-radius: var(--radius-pill);
  background: var(--bg-color);
  color: var(--color-black);
  font-size: 16px;
  font-weight: var(--font-weight-bold);
  outline: none;
  transition: border-color 0.2s;
}

.chat-input::placeholder {
  color: var(--color-dark-gray);
  font-weight: var(--font-weight-medium);
}

.chat-input:focus {
  border-color: var(--color-black);
}

.chat-send-btn {
  position: absolute;
  right: 48px; /* Move it inward a bit from the form edge */
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  background: var(--color-black);
  color: var(--color-white);
  font-size: 20px;
  font-weight: 900;
  cursor: pointer;
  transition: transform 0.2s, background 0.2s;
}

.chat-send-btn:hover:not(:disabled) {
  background: var(--color-orange);
  transform: scale(1.05);
}

.chat-send-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes blink {
  0%, 80%, 100% { opacity: 0.2; }
  40% { opacity: 1; }
}
</style>
