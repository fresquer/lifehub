<template>
  <div class="page">
    <header class="topbar">
      <div class="topbar-left">
        <router-link to="/dashboard" class="brand">LifeHub</router-link>
        <nav class="topbar-nav">
          <router-link to="/dashboard" class="nav-link" exact-active-class="active">Áreas</router-link>
          <router-link to="/dashboard/tareas" class="nav-link" exact-active-class="active">Tareas</router-link>
        </nav>
      </div>
      <div class="topbar-right" ref="dropdownWrapRef">
        <button
          type="button"
          class="theme-toggle"
          :aria-label="theme === 'dark' ? 'Usar tema claro' : 'Usar tema oscuro'"
          :title="theme === 'dark' ? 'Tema claro' : 'Tema oscuro'"
          @click="toggle()"
        >
          <Sun v-if="theme === 'dark'" :size="20" class="theme-icon" aria-hidden="true" />
          <Moon v-else :size="20" class="theme-icon" aria-hidden="true" />
        </button>
        <button
          type="button"
          class="user-trigger"
          :aria-expanded="dropdownOpen"
          aria-haspopup="true"
          @click="dropdownOpen = !dropdownOpen"
        >
          <span class="user-avatar">{{ userInitial }}</span>
          <span class="user-email">{{ user?.email || "…" }}</span>
          <ChevronDown :size="16" class="dropdown-chevron" :class="{ open: dropdownOpen }" aria-hidden="true" />
        </button>
        <Transition name="dropdown">
          <div v-if="dropdownOpen" class="dropdown-menu" role="menu">
            <div class="dropdown-header">
              <span class="dropdown-name">{{
                user?.full_name || "Usuario"
              }}</span>
              <span class="dropdown-email">{{ user?.email }}</span>
            </div>
            <div class="dropdown-divider" />
            <router-link
              to="/dashboard/usuario"
              class="dropdown-item"
              @click="dropdownOpen = false"
            >
              <Info :size="18" class="dropdown-icon" />
              Info
            </router-link>
            <router-link
              to="/dashboard/usuario/configuracion"
              class="dropdown-item"
              @click="dropdownOpen = false"
            >
              <Settings :size="18" class="dropdown-icon" />
              Configuración
            </router-link>
            <router-link
              to="/dashboard/configuracion-areas"
              class="dropdown-item"
              @click="dropdownOpen = false"
            >
              <ClipboardList :size="18" class="dropdown-icon" />
              Configuración áreas
            </router-link>
            <div class="dropdown-divider" />
            <button type="button" class="dropdown-item danger" @click="logout">
              <LogOut :size="18" class="dropdown-icon" />
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
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { Sun, Moon, ChevronDown, Info, Settings, ClipboardList, LogOut } from "lucide-vue-next";
import { useAuth } from "../composables/useAuth";
import { useTheme } from "../composables/useTheme";

const { theme, toggle } = useTheme();
const router = useRouter();
const { user, fetchUser, logout: doLogout } = useAuth();
const dropdownOpen = ref(false);
const dropdownWrapRef = ref(null);

const userInitial = computed(() => {
  const u = user.value;
  if (u?.full_name) return u.full_name.charAt(0).toUpperCase();
  if (u?.email) return u.email.charAt(0).toUpperCase();
  return "?";
});

function closeDropdown(e) {
  if (dropdownWrapRef.value && !dropdownWrapRef.value.contains(e.target)) {
    dropdownOpen.value = false;
  }
}

onMounted(async () => {
  await fetchUser();
  document.addEventListener("click", closeDropdown);
});

onUnmounted(() => {
  document.removeEventListener("click", closeDropdown);
});

function logout() {
  dropdownOpen.value = false;
  doLogout();
  router.push("/login");
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-page);
  color: var(--text);
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
  background: var(--topbar-bg);
  border-bottom: 1px solid var(--topbar-border);
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
  color: var(--text);
  text-decoration: none;
}

.brand:hover {
  color: var(--text-strong);
}

.topbar-nav {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-left: 0.5rem;
}

.nav-link {
  padding: 0.4rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-muted);
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
}

.nav-link:hover {
  color: var(--text-strong);
  background: var(--hover-bg);
}

.nav-link.active {
  color: var(--text-strong);
  background: var(--hover-bg);
}

.topbar-right {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  border: none;
  border-radius: 0.5rem;
  background: transparent;
  color: var(--text);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.theme-toggle:hover {
  background: var(--hover-bg);
  color: var(--text-strong);
}

.theme-icon {
  font-size: 1.25rem;
  line-height: 1;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.6rem;
  border-radius: 0.5rem;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text);
  cursor: pointer;
  font-size: 0.9rem;
  max-width: 220px;
}

.user-trigger:hover {
  background: var(--hover-bg);
  border-color: var(--hover-border);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--avatar-gradient);
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
  color: var(--text-muted);
}

.dropdown-chevron {
  font-size: 0.7rem;
  color: var(--input-placeholder);
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
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 0.75rem;
  box-shadow: var(--shadow-modal);
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
  color: var(--text-strong);
}

.dropdown-email {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.dropdown-divider {
  height: 1px;
  background: var(--topbar-border);
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
  color: var(--text);
  font-size: 0.9rem;
  text-align: left;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s;
}

.dropdown-item:hover {
  background: var(--hover-bg);
}

.dropdown-item.danger {
  color: var(--danger);
}

.dropdown-item.danger:hover {
  background: var(--danger-bg);
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem;
  width: 100%;
}
</style>
