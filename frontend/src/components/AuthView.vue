<template>
  <div class="auth-container">
    <div class="auth-card bento-card">
      <div class="brand-header">
        <img class="brand-logo" src="../assets/itk/logo-itk-white-notext.webp" alt="Logo Institut Teknologi Kalimantan" />
        <span class="brand-kicker">Institut Teknologi Kalimantan</span>
        <h1>ITK <span class="brand-text">Lost & Found</span></h1>
        <p>Login untuk mengakses sistem</p>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form" v-if="!isRegister">
        <div class="form-group">
          <label>Username</label>
          <input type="text" v-model="loginForm.username" required />
          <span class="field-error" v-if="errors.username">{{ errors.username }}</span>
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="loginForm.password" required />
          <span class="field-error" v-if="errors.password">{{ errors.password }}</span>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">Login</button>
        <p class="toggle-text">Belum punya akun? <a href="#" @click.prevent="isRegister = true; clearErrors()">Daftar</a></p>
        <p class="error" v-if="generalError">{{ generalError }}</p>
      </form>

      <form @submit.prevent="handleRegister" class="auth-form" v-else>
        <div class="form-group">
          <label>Username</label>
          <input type="text" v-model="registerForm.username" required />
          <span class="field-error" v-if="errors.username">{{ errors.username }}</span>
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="registerForm.password" required />
          <span class="field-error" v-if="errors.password">{{ errors.password }}</span>
        </div>
        <div class="form-group">
          <label>Nama Lengkap</label>
          <input type="text" v-model="registerForm.full_name" required />
          <span class="field-error" v-if="errors.full_name">{{ errors.full_name }}</span>
        </div>
        <div class="form-group">
          <label>NIM (Opsional)</label>
          <input type="text" v-model="registerForm.nim" />
          <span class="field-error" v-if="errors.nim">{{ errors.nim }}</span>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">Daftar</button>
        <p class="toggle-text">Sudah punya akun? <a href="#" @click.prevent="isRegister = false; clearErrors()">Login</a></p>
        <p class="error" v-if="generalError">{{ generalError }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api.js'

const emit = defineEmits(['auth-success'])

const isRegister = ref(false)
const loading = ref(false)
const generalError = ref('')
const errors = ref({})

const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ username: '', password: '', full_name: '', nim: '' })
let abortController = null

function clearErrors() {
  errors.value = {}
  generalError.value = ''
}

function handleApiError(err) {
  clearErrors()
  if (err.code === 'ERR_CANCELED' || err.name === 'CanceledError') return
  console.error(err)
  
  const detail = err.response?.data?.detail
  if (Array.isArray(detail)) {
    detail.forEach(d => {
      const field = d.loc && d.loc.length > 0 ? d.loc[d.loc.length - 1] : null
      if (field && field !== 'body') {
        errors.value[field] = d.msg
      } else {
        generalError.value = d.msg
      }
    })
  } else {
    generalError.value = detail || err.message || 'Terjadi kesalahan'
  }
}

async function handleLogin() {
  if (abortController) abortController.abort()
  abortController = new AbortController()
  const timeoutId = setTimeout(() => abortController.abort(), 10000)
  
  loading.value = true
  clearErrors()
  try {
    const formData = new URLSearchParams()
    formData.append('username', loginForm.value.username)
    formData.append('password', loginForm.value.password)
    
    const res = await api.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      signal: abortController.signal
    })
    
    clearTimeout(timeoutId)
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    emit('auth-success', res.data.user)
  } catch (err) {
    clearTimeout(timeoutId)
    handleApiError(err)
  } finally {
    loading.value = false
    abortController = null
  }
}

async function handleRegister() {
  if (abortController) abortController.abort()
  abortController = new AbortController()
  const timeoutId = setTimeout(() => abortController.abort(), 10000)
  
  loading.value = true
  clearErrors()
  try {
    const res = await api.post('/api/auth/register', registerForm.value, {
      signal: abortController.signal
    })
    
    clearTimeout(timeoutId)
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    emit('auth-success', res.data.user)
  } catch (err) {
    clearTimeout(timeoutId)
    handleApiError(err)
  } finally {
    loading.value = false
    abortController = null
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--bg-color); /* as assumed in App.vue */
  padding: 20px;
  position: relative;
  overflow: hidden;
}
.auth-container::before {
  content: '';
  position: absolute;
  left: -160px;
  bottom: -110px;
  width: min(620px, 72vw);
  aspect-ratio: 1148 / 584;
  background-image: url('../assets/itk/gear-blue-half.webp');
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.08;
  pointer-events: none;
}
.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface);
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05); /* slightly soften visually */
  position: relative;
  z-index: 1;
}
.brand-header {
  text-align: center;
  margin-bottom: 30px;
}
.brand-logo {
  width: 58px;
  height: 68px;
  object-fit: contain;
  padding: 6px;
  border-radius: 14px;
  background: var(--color-primary);
  margin-bottom: 10px;
}
.brand-kicker {
  display: block;
  margin-bottom: 6px;
  color: var(--color-primary);
  font-size: 12px;
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.02em;
}
.brand-header h1 {
  font-size: 32px;
  margin: 0;
  letter-spacing: 0;
}
.brand-text {
  color: var(--color-primary);
}
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-main);
}
.form-group input {
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  font-size: 14px;
  transition: border-color 0.2s;
  background: var(--color-surface);
}
.form-group input:focus {
  outline: none;
  border-color: var(--color-primary);
}
.btn {
  padding: 14px;
  border-radius: 12px;
  border: none;
  font-weight: bold;
  cursor: pointer;
  background: var(--color-primary);
  color: var(--color-on-primary);
  font-size: 16px;
  margin-top: 10px;
  transition: opacity 0.2s;
}
.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
.toggle-text {
  text-align: center;
  font-size: 14px;
  margin-top: 10px;
}
.toggle-text a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
}
.error {
  color: var(--color-danger);
  text-align: center;
  font-size: 14px;
  font-weight: 500;
}
.field-error {
  color: var(--color-danger);
  font-size: 12px;
  margin-top: -4px;
}
</style>
