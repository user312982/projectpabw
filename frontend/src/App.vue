<template>
  <div id="app-root">
    <AuthView v-if="!user" @auth-success="handleAuthSuccess" />
    <PetugasView v-else-if="user.role === 'petugas'" @logout="handleLogout" :user="user" />
    <UserView v-else-if="user.role === 'user'" @logout="handleLogout" :user="user" />
    <div v-else class="center-content">
      <p>Role tidak dikenali: {{ user.role }}</p>
      <button @click="handleLogout" class="btn">Kembali</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AuthView from './components/AuthView.vue'
import UserView from './components/UserView.vue'
import PetugasView from './components/PetugasView.vue'
import api from './services/api.js'

const user = ref(null)

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (token) {
    try {
      const res = await api.get('/api/auth/me')
      user.value = res.data
      localStorage.setItem('user', JSON.stringify(res.data))
    } catch(e) {
      if (e.code !== 'ERR_CANCELED' && e.code !== 'ECONNABORTED') {
        console.error(e)
        handleLogout()
      }
    }
  }
})

function handleAuthSuccess(userData) {
  user.value = userData
}

function handleLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  user.value = null
}
</script>

<style>
#app-root {
  min-height: 100vh;
  width: 100%;
}
.center-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
  gap: 20px;
  color: var(--color-text-main);
  background: var(--bg-color, #F7F9FC);
}
.btn {
  padding: 10px 20px;
  background: var(--color-primary, #0B61AA);
  color: var(--color-on-primary, #FFFFFF);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}
</style>
