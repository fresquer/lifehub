<template>
  <div class="usuario-content">
    <div v-if="user" class="card">
      <p><strong>Email:</strong> {{ user.email }}</p>
      <p v-if="user.full_name"><strong>Nombre:</strong> {{ user.full_name }}</p>
    </div>
    <nav class="nav">
      <router-link to="/dashboard" class="btn btn-secondary">Inicio</router-link>
    </nav>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'

const { user, fetchUser } = useAuth()

onMounted(async () => {
  await fetchUser()
})
</script>

<style scoped>
.usuario-content {
  padding: 0.5rem 0;
}

.card {
  background: var(--hover-bg);
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid var(--card-border-subtle);
  margin-bottom: 1.5rem;
}

.card p {
  margin: 0.5rem 0;
}

.nav {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.6rem 1rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 500;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-secondary {
  background: var(--hover-bg);
  color: var(--text);
  border: 1px solid var(--input-border);
}
</style>
