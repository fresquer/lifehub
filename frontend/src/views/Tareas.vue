<template>
  <div class="page">
    <main class="main">
      <p v-if="loading" class="status">Cargando tareas…</p>
      <p v-else-if="error" class="status error">{{ error }}</p>
      <template v-else>
        <div v-if="hasNoTasks" class="empty">
          <p>No hay tareas. Añade una siguiente acción en un proyecto o crea una one-shot abajo.</p>
        </div>
        <div v-else class="tareas-scroll">
          <!-- Por área y proyecto (siguiente acción de cada proyecto) -->
          <section
            v-for="area in orderedAreas"
            :key="area.id"
            class="area-section"
            :style="areaSectionStyle(area)"
          >
            <h2 class="area-title">{{ area.name }}</h2>
            <div class="task-list">
              <div
                v-for="project in projectTasksInArea(area.id)"
                :key="'p-' + project.id"
                class="task-row task-row-project"
              >
                <span class="task-project-meta">
                  <span class="task-project-icon">{{ project.icon || '📄' }}</span>
                  <span class="task-project-name">{{ project.name }}</span>
                </span>
                <span class="task-title">{{ project.next_action }}</span>
                <button
                  type="button"
                  class="btn-completada"
                  :disabled="completingProjectId === project.id"
                  @click="markProjectNextActionComplete(project)"
                >
                  Completada
                </button>
              </div>
              <p v-if="projectTasksInArea(area.id).length === 0" class="no-tasks">Sin tareas en esta área</p>
            </div>
          </section>

          <!-- One shots (sin proyecto) -->
          <section class="area-section area-section-oneshots">
            <h2 class="area-title">One shots</h2>
            <p class="area-desc">Tareas sin proyecto</p>
            <form class="add-oneshot-form" @submit.prevent="addOneShot">
              <input
                v-model="newOneShotTitle"
                type="text"
                class="input"
                placeholder="Nueva tarea one-shot…"
              />
              <button type="submit" class="btn btn-primary" :disabled="savingOneShot || !newOneShotTitle.trim()">
                Añadir
              </button>
            </form>
            <div class="task-list">
              <div
                v-for="task in oneShotTasks"
                :key="'o-' + task.id"
                class="task-row task-row-oneshot"
                :class="{ done: task.done }"
              >
                <input
                  type="checkbox"
                  :checked="task.done"
                  class="task-checkbox"
                  @change="toggleOneShotDone(task)"
                />
                <span class="task-title">{{ task.title }}</span>
                <button
                  type="button"
                  class="btn-delete"
                  aria-label="Eliminar"
                  @click="deleteOneShot(task)"
                >
                  ×
                </button>
              </div>
              <p v-if="oneShotTasks.length === 0" class="no-tasks">Aún no hay one-shots</p>
            </div>
          </section>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useApi } from '../composables/useApi'

const AREA_ORDER_KEY = 'lifehub_area_order'
const DEFAULT_AREA_ACCENT = '#64748b'

const { fetchUser } = useAuth()
const { get, post, patch, delete: del } = useApi()

const loading = ref(true)
const error = ref('')
const areas = ref([])
const projects = ref([])
const oneShotTasks = ref([])
const newOneShotTitle = ref('')
const savingOneShot = ref(false)
const completingProjectId = ref(null)

function getStoredAreaOrder() {
  try {
    const raw = localStorage.getItem(AREA_ORDER_KEY)
    if (!raw) return []
    const arr = JSON.parse(raw)
    return Array.isArray(arr) ? arr.filter(Number.isInteger) : []
  } catch {
    return []
  }
}

const orderedAreas = computed(() => {
  const order = getStoredAreaOrder()
  const byId = Object.fromEntries(areas.value.map((a) => [a.id, a]))
  const result = []
  for (const id of order) {
    if (byId[id]) {
      result.push(byId[id])
      delete byId[id]
    }
  }
  result.push(...Object.values(byId).sort((a, b) => a.name.localeCompare(b.name)))
  return result
})

function areaSectionStyle(area) {
  const color = area.color || DEFAULT_AREA_ACCENT
  return { '--area-accent': color, borderLeftColor: color }
}

/** Proyectos de un área que tienen next_action (para mostrar como tarea). */
function projectTasksInArea(areaId) {
  return projects.value.filter((p) => p.area_id === areaId && p.next_action && p.next_action.trim())
}

const hasNoTasks = computed(() => {
  const hasProjectTasks = projects.value.some((p) => p.next_action && p.next_action.trim())
  return !hasProjectTasks && oneShotTasks.value.length === 0
})

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [areasData, projectsData, tasksData] = await Promise.all([
      get('areas'),
      get('projects'),
      get('one-shot-tasks'),
    ])
    areas.value = areasData
    projects.value = projectsData
    oneShotTasks.value = tasksData
  } catch (e) {
    error.value = e.message || 'Error al cargar datos'
  } finally {
    loading.value = false
  }
}

async function markProjectNextActionComplete(project) {
  if (completingProjectId.value) return
  completingProjectId.value = project.id
  try {
    const updated = await patch(`projects/${project.id}`, { next_action: '' })
    const i = projects.value.findIndex((p) => p.id === project.id)
    if (i !== -1) projects.value[i] = { ...projects.value[i], ...updated }
  } catch (e) {
    error.value = e.message || 'Error al guardar'
  } finally {
    completingProjectId.value = null
  }
}

async function addOneShot() {
  const title = newOneShotTitle.value.trim()
  if (!title || savingOneShot.value) return
  savingOneShot.value = true
  try {
    const created = await post('one-shot-tasks', { title })
    oneShotTasks.value = [...oneShotTasks.value, created]
    newOneShotTitle.value = ''
  } catch (e) {
    error.value = e.message || 'Error al crear'
  } finally {
    savingOneShot.value = false
  }
}

async function toggleOneShotDone(task) {
  try {
    const updated = await patch(`one-shot-tasks/${task.id}`, { done: !task.done })
    const i = oneShotTasks.value.findIndex((t) => t.id === task.id)
    if (i !== -1) oneShotTasks.value[i] = { ...oneShotTasks.value[i], ...updated }
  } catch (e) {
    error.value = e.message || 'Error al actualizar'
  }
}

async function deleteOneShot(task) {
  if (!confirm('¿Eliminar esta tarea?')) return
  try {
    await del(`one-shot-tasks/${task.id}`)
    oneShotTasks.value = oneShotTasks.value.filter((t) => t.id !== task.id)
  } catch (e) {
    error.value = e.message || 'Error al eliminar'
  }
}

onMounted(async () => {
  await fetchUser()
  await loadData()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-page);
  color: var(--text);
}

.main {
  flex: 1;
  padding: 1.5rem 1.25rem;
  overflow-y: auto;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.status {
  text-align: center;
  color: var(--text-muted);
  padding: 2rem;
}

.status.error {
  color: var(--danger);
}

.empty {
  text-align: center;
  color: var(--text-muted);
  padding: 3rem 1.5rem;
  background: var(--card-bg);
  border-radius: 1rem;
  border: 1px dashed var(--card-border-subtle);
}

.tareas-scroll {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.area-section {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-left: 8px solid var(--area-accent, var(--default-accent));
  border-radius: 1rem;
  padding: 1.25rem;
}

.area-section-oneshots {
  border-left-color: var(--text-muted);
}

.area-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-strong);
  margin: 0 0 0.5rem 0;
}

.area-desc {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin: 0 0 0.75rem 0;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.task-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  background: var(--input-bg);
  border-radius: 0.5rem;
  border: 1px solid var(--card-border-subtle);
}

.task-row-oneshot.done .task-title {
  text-decoration: line-through;
  color: var(--text-muted);
}

.task-project-meta {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-width: 0;
}

.task-project-icon {
  font-size: 1.1rem;
}

.task-project-name {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-title {
  flex: 1;
  min-width: 0;
  font-size: 0.95rem;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-checkbox {
  flex-shrink: 0;
  width: 1.1rem;
  height: 1.1rem;
  cursor: pointer;
}

.btn-completada {
  flex-shrink: 0;
  padding: 0.35rem 0.6rem;
  font-size: 0.85rem;
  background: var(--success-bg);
  color: var(--success);
  border: 1px solid var(--success-border);
  border-radius: 0.4rem;
  cursor: pointer;
}

.btn-completada:hover:not(:disabled) {
  filter: brightness(1.05);
  opacity: 0.95;
}

.btn-completada:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-delete {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  line-height: 1;
  color: var(--text-muted);
  background: none;
  border: none;
  border-radius: 0.4rem;
  cursor: pointer;
}

.btn-delete:hover {
  color: var(--danger);
  background: var(--danger-bg);
}

.add-oneshot-form {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.input {
  flex: 1;
  min-width: 0;
  padding: 0.5rem 0.75rem;
  font-size: 0.95rem;
  color: var(--text);
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: 0.5rem;
  outline: none;
}

.input::placeholder {
  color: var(--input-placeholder);
}

.input:focus {
  border-color: var(--primary);
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary);
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.no-tasks {
  margin: 0;
  padding: 0.5rem 0;
  font-size: 0.9rem;
  color: var(--input-placeholder);
}
</style>
