<template>
  <div class="auth-container">
    <div class="auth-card bento-card">
      <div class="brand-header">
        <h1>ITK <span class="brand-text">LostFound</span></h1>
        <p>Login untuk mengakses sistem</p>
      </div>

      <form @submit.prevent="handleLogin" class="auth-form" v-if="!isRegister">
        <div class="form-group">
          <label>Username</label>
          <input type="text" v-model="loginForm.username" required />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="loginForm.password" required />
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">Login</button>
        <p class="toggle-text">Belum punya akun? <a href="#" @click.prevent="isRegister = true">Daftar</a></p>
        <p class="error" v-if="error">{{ error }}</p>
      </form>

      <form @submit.prevent="handleRegister" class="auth-form" v-else>
        <div class="form-group">
          <label>Username</label>
          <input type="text" v-model="registerForm.username" required />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="registerForm.password" required />
        </div>
        <div class="form-group">
          <label>Nama Lengkap</label>
          <input type="text" v-model="registerForm.full_name" required />
        </div>
        <div class="form-group">
          <label>NIM (Opsional)</label>
          <input type="text" v-model="registerForm.nim" />
        </div>
        <button type="submit" class="btn btn-primary" :disabled="loading">Daftar</button>
        <p class="toggle-text">Sudah punya akun? <a href="#" @click.prevent="isRegister = false">Login</a></p>
        <p class="error" v-if="error">{{ error }}</p>
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
const error = ref('')

const loginForm = ref({ username: '', password: '' })
const registerForm = ref({ username: '', password: '', full_name: '', nim: '' })

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const formData = new URLSearchParams()
    formData.append('username', loginForm.value.username)
    formData.append('password', loginForm.value.password)
    
    // Login menggunakan format URL-encoded untuk OAuth2 Password Bearer di FastAPI
    const res = await api.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    emit('auth-success', res.data.user)
  } catch (err) {
    console.error(err)
    error.value = err.response?.data?.detail || 'Gagal login'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.post('/api/auth/register', registerForm.value)
    
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    emit('auth-success', res.data.user)
  } catch (err) {
    console.error(err)
    error.value = err.response?.data?.detail || 'Gagal daftar'
  } finally {
    loading.value = false
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
}
.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--color-white);
  padding: 40px;
  border-radius: 24px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05); /* slightly soften visually */
}
.brand-header {
  text-align: center;
  margin-bottom: 30px;
}
.brand-header h1 {
  font-size: 32px;
  margin: 0;
  letter-spacing: -1px;
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
  color: var(--color-black);
}
.form-group input {
  padding: 12px 16px;
  border: 1px solid var(--color-gray);
  border-radius: 12px;
  font-size: 14px;
  transition: border-color 0.2s;
  background: #fdfdfd;
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
  background: var(--gradient-primary);
  color: var(--color-white);
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
  color: #ef4444;
  text-align: center;
  font-size: 14px;
  font-weight: 500;
}
</style>
