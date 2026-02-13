<template>
  <div class="page">
    <header class="header">
      <h1>LifeHub</h1>
      <p class="tagline">Tu centro de vida</p>
    </header>
    <main class="main">
      <section class="hero">
        <p v-if="apiStatus">{{ apiStatus }}</p>
        <p v-else class="loading">Comprobando API...</p>
      </section>
      <nav class="nav">
        <router-link v-if="!isAuthenticated" to="/login" class="btn btn-primary">Iniciar sesión</router-link>
        <router-link v-if="!isAuthenticated" to="/signup" class="btn btn-secondary">Registrarse</router-link>
        <router-link v-if="isAuthenticated" to="/dashboard" class="btn btn-primary">Áreas y proyectos</router-link>
        <router-link v-if="isAuthenticated" to="/dashboard/usuario" class="btn btn-secondary">Mi perfil</router-link>
      </nav>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'

const apiStatus = ref('')
const { isAuthenticated } = useAuth()

onMounted(async () => {
  try {
    const res = await fetch('/api/')
    const data = await res.json()
    apiStatus.value = data.message
  } catch {
    apiStatus.value = 'No se pudo conectar con el backend'
  }
})
</script>

<style scoped>
.page { max-width: 720px; margin: 0 auto; padding: 2rem; }
.header { text-align: center; margin-bottom: 2rem; }
.header h1 { font-size: 2.5rem; font-weight: 700; letter-spacing: -0.02em; }
.tagline { color: var(--text-muted); margin-top: 0.5rem; }
.main { background: var(--hover-bg); border-radius: 1rem; padding: 2rem; border: 1px solid var(--card-border-subtle); }
.hero { text-align: center; font-size: 1.125rem; margin-bottom: 1.5rem; }
.loading { color: var(--text-muted); }
.nav { display: flex; gap: 0.75rem; justify-content: center; flex-wrap: wrap; }
.btn { padding: 0.6rem 1.2rem; border-radius: 0.5rem; text-decoration: none; font-weight: 500; transition: opacity 0.2s; }
.btn:hover { opacity: 0.9; }
.btn-primary { background: var(--primary); color: #fff; }
.btn-secondary { background: var(--hover-bg); color: var(--text); border: 1px solid var(--input-border); }
</style>
