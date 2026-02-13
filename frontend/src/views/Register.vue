<template>
  <div class="page">
    <header class="header">
      <h1>Registro</h1>
      <p class="tagline">Crear cuenta en LifeHub</p>
    </header>
    <main class="main">
      <form class="form" @submit.prevent="submit">
        <div class="field">
          <label for="email">Email</label>
          <input id="email" v-model="email" type="email" required placeholder="tu@email.com" autocomplete="email" />
        </div>
        <div class="field">
          <label for="password">Contraseña</label>
          <input id="password" v-model="password" type="password" required placeholder="••••••••" autocomplete="new-password" minlength="6" />
        </div>
        <div class="field">
          <label for="full_name">Nombre (opcional)</label>
          <input id="full_name" v-model="fullName" type="text" placeholder="Tu nombre" autocomplete="name" />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" class="btn btn-primary" :disabled="loading">Registrarse</button>
      </form>
      <p class="footer">
        ¿Ya tienes cuenta? <router-link to="/login">Iniciar sesión</router-link>
      </p>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { setToken, fetchUser } = useAuth()

const email = ref('')
const password = ref('')
const fullName = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
        full_name: fullName.value || undefined,
      }),
    })
    const data = await res.json().catch(() => ({}))
    if (!res.ok) {
      error.value = data.detail || 'Error al registrar'
      return
    }
    const loginRes = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value, password: password.value }),
    })
    const loginData = await loginRes.json().catch(() => ({}))
    if (loginRes.ok && loginData.access_token) {
      setToken(loginData.access_token)
      await fetchUser()
      router.push('/dashboard')
    } else {
      router.push('/login')
    }
  } catch {
    error.value = 'Error de conexión'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page { max-width: 420px; margin: 0 auto; padding: 2rem; }
.header { text-align: center; margin-bottom: 2rem; }
.header h1 { font-size: 1.75rem; font-weight: 700; }
.tagline { color: var(--text-muted); margin-top: 0.25rem; font-size: 0.9rem; }
.main { background: var(--hover-bg); border-radius: 1rem; padding: 1.5rem; border: 1px solid var(--card-border-subtle); }
.form { display: flex; flex-direction: column; gap: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.35rem; }
.field label { font-size: 0.875rem; color: var(--text-muted); }
.field input { padding: 0.6rem 0.75rem; border-radius: 0.5rem; border: 1px solid var(--input-border); background: var(--input-bg); color: var(--text); }
.field input::placeholder { color: var(--input-placeholder); }
.error { color: var(--danger); font-size: 0.875rem; margin: 0; }
.btn { padding: 0.6rem 1rem; border-radius: 0.5rem; border: none; font-weight: 500; cursor: pointer; }
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary { background: var(--primary); color: #fff; }
.footer { text-align: center; margin-top: 1rem; font-size: 0.9rem; color: var(--text-muted); }
.footer a { color: var(--link); }
</style>
