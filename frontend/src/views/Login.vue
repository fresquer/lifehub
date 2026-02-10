<template>
  <div class="page">
    <header class="header">
      <h1>Iniciar sesión</h1>
      <p class="tagline">LifeHub</p>
    </header>
    <main class="main">
      <form class="form" @submit.prevent="submit">
        <div class="field">
          <label for="email">Email</label>
          <input id="email" v-model="email" type="email" required placeholder="tu@email.com" autocomplete="email" />
        </div>
        <div class="field">
          <label for="password">Contraseña</label>
          <input id="password" v-model="password" type="password" required placeholder="••••••••" autocomplete="current-password" />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" class="btn btn-primary" :disabled="loading">Entrar</button>
      </form>
      <div class="dev-quick">
        <p class="dev-label">Dev: acceso rápido</p>
        <button type="button" class="btn btn-dev" :disabled="loading" @click="quickLogin">
          Login con usuario test
        </button>
        <p class="dev-url">O abre <router-link :to="{ path: '/login', query: { quick: '1', redirect: redirectTo } }">/login?quick=1</router-link> para entrar al instante.</p>
      </div>
      <p class="footer">
        ¿No tienes cuenta? <router-link to="/signup">Regístrate</router-link>
      </p>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const route = useRoute()
const { setToken, fetchUser } = useAuth()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const redirectTo = computed(() => route.query.redirect || '/dashboard')

onMounted(() => {
  if (route.query.quick === '1') {
    quickLogin()
  }
})

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      error.value = data.detail || 'Email o contraseña incorrectos'
      return
    }
    setToken(data.access_token)
    await fetchUser()
    router.push(redirectTo.value)
  } catch {
    error.value = 'Error de conexión'
  } finally {
    loading.value = false
  }
}

async function quickLogin() {
  email.value = 'test@lifehub.local'
  password.value = 'test123'
  await submit()
}
</script>

<style scoped>
.page { max-width: 420px; margin: 0 auto; padding: 2rem; }
.header { text-align: center; margin-bottom: 2rem; }
.header h1 { font-size: 1.75rem; font-weight: 700; }
.tagline { color: #94a3b8; margin-top: 0.25rem; font-size: 0.9rem; }
.main { background: rgba(255,255,255,0.05); border-radius: 1rem; padding: 1.5rem; border: 1px solid rgba(255,255,255,0.08); }
.form { display: flex; flex-direction: column; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.35rem; }
.field label { font-size: 0.875rem; color: #94a3b8; }
.field input { padding: 0.6rem 0.75rem; border-radius: 0.5rem; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.2); color: #fff; }
.field input::placeholder { color: #64748b; }
.error { color: #f87171; font-size: 0.875rem; margin: 0; }
.btn { padding: 0.6rem 1rem; border-radius: 0.5rem; border: none; font-weight: 500; cursor: pointer; transition: opacity 0.2s; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary { background: #3b82f6; color: #fff; }
.dev-quick { margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.08); }
.dev-label { font-size: 0.75rem; color: #64748b; margin-bottom: 0.5rem; }
.btn-dev { background: rgba(251,191,36,0.2); color: #fbbf24; border: 1px solid rgba(251,191,36,0.4); font-size: 0.875rem; }
.dev-url { font-size: 0.75rem; color: #64748b; margin-top: 0.5rem; }
.dev-url a { color: #94a3b8; }
.footer { text-align: center; margin-top: 1rem; font-size: 0.9rem; color: #94a3b8; }
.footer a { color: #60a5fa; }
</style>
