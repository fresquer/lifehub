<template>
  <div class="page">
    <header class="topbar">
      <div class="topbar-left">
        <router-link to="/" class="brand">LifeHub</router-link>
        <span class="page-title">{{ pageTitle }}</span>
      </div>
      <div class="topbar-right" ref="dropdownWrapRef">
        <button
          type="button"
          class="user-trigger"
          :aria-expanded="dropdownOpen"
          aria-haspopup="true"
          @click="dropdownOpen = !dropdownOpen"
        >
          <span class="user-avatar">{{ userInitial }}</span>
          <span class="user-email">{{ user?.email || '…' }}</span>
          <span class="dropdown-chevron" :class="{ open: dropdownOpen }">▾</span>
        </button>
        <Transition name="dropdown">
          <div v-if="dropdownOpen" class="dropdown-menu" role="menu">
            <div class="dropdown-header">
              <span class="dropdown-name">{{ user?.full_name || 'Usuario' }}</span>
              <span class="dropdown-email">{{ user?.email }}</span>
            </div>
            <div class="dropdown-divider" />
            <router-link to="/areas" class="dropdown-item" @click="dropdownOpen = false">
              <span class="dropdown-icon">📂</span>
              Áreas y proyectos
            </router-link>
            <router-link to="/usuario" class="dropdown-item" @click="dropdownOpen = false">
              <span class="dropdown-icon">ℹ️</span>
              Info
            </router-link>
            <router-link to="/usuario/configuracion" class="dropdown-item" @click="dropdownOpen = false">
              <span class="dropdown-icon">⚙️</span>
              Configuración
            </router-link>
            <router-link to="/areas/configuracion" class="dropdown-item" @click="dropdownOpen = false">
              <span class="dropdown-icon">📋</span>
              Configuración áreas
            </router-link>
            <div class="dropdown-divider" />
            <button type="button" class="dropdown-item danger" @click="logout">
              <span class="dropdown-icon">🚪</span>
              Cerrar sesión
            </button>
          </div>
        </Transition>
      </div>
    </header>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const route = useRoute()
const router = useRouter()
const { user, fetchUser, logout: doLogout } = useAuth()
const dropdownOpen = ref(false)
const dropdownWrapRef = ref(null)

const pageTitle = computed(() => route.meta.pageTitle || 'Mi espacio')

const userInitial = computed(() => {
  const u = user.value
  if (u?.full_name) return u.full_name.charAt(0).toUpperCase()
  if (u?.email) return u.email.charAt(0).toUpperCase()
  return '?'
})

function closeDropdown(e) {
  if (dropdownWrapRef.value && !dropdownWrapRef.value.contains(e.target)) {
    dropdownOpen.value = false
  }
}

onMounted(async () => {
  await fetchUser()
  document.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown)
})

function logout() {
  dropdownOpen.value = false
  doLogout()
  router.push('/login')
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-page, #0f172a);
  color: var(--text, #e2e8f0);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 1.25rem;
  background: rgba(15, 23, 42, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(8px);
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.brand {
  font-weight: 700;
  font-size: 1.15rem;
  color: #e2e8f0;
  text-decoration: none;
}

.brand:hover {
  color: #f8fafc;
}

.page-title {
  font-size: 0.95rem;
  color: #94a3b8;
  font-weight: 500;
}

.topbar-right {
  position: relative;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.6rem;
  border-radius: 0.5rem;
  border: 1px solid transparent;
  background: transparent;
  color: #e2e8f0;
  cursor: pointer;
  font-size: 0.9rem;
  max-width: 220px;
}

.user-trigger:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(255, 255, 255, 0.1);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  flex-shrink: 0;
}

.user-email {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #94a3b8;
}

.dropdown-chevron {
  font-size: 0.7rem;
  color: #64748b;
  transition: transform 0.2s;
}

.dropdown-chevron.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  min-width: 220px;
  padding: 0.5rem 0;
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
}

.dropdown-header {
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.dropdown-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: #f1f5f9;
}

.dropdown-email {
  font-size: 0.8rem;
  color: #94a3b8;
}

.dropdown-divider {
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
  margin: 0.25rem 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  padding: 0.6rem 1rem;
  border: none;
  background: none;
  color: #e2e8f0;
  font-size: 0.9rem;
  text-align: left;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s;
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.dropdown-item.danger {
  color: #f87171;
}

.dropdown-item.danger:hover {
  background: rgba(248, 113, 113, 0.1);
}

.dropdown-icon {
  font-size: 1rem;
  opacity: 0.9;
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.main {
  flex: 1;
  max-width: 720px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem;
  width: 100%;
}
</style>
