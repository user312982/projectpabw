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
      // Validate token internally or just use the cached user and rely on interceptor logic. 
      // Better to check with backend just in case.
      const res = await api.get('/api/auth/me')
      user.value = res.data
      localStorage.setItem('user', JSON.stringify(res.data))
    } catch(e) {
      console.error(e)
      handleLogout()
    }
  }
})

function handleAuthSuccess(userData) {
  user.value = userData
}

function handleLogout() {
  localStorage.removeItem('token')
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
  color: white;
  background: var(--bg-color, #1a1a1a);
}
.btn {
  padding: 10px 20px;
  background: var(--color-primary, #10b981);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}
</style>
