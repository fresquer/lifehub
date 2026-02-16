<template>
  <div class="page">
    <main class="main">
      <p v-if="loading" class="status">Cargando tareas…</p>
      <p v-else-if="error" class="status error">{{ error }}</p>
      <template v-else>
        <!-- Creador de tareas arriba -->
        <section class="creator-section">
          <form class="add-task-form" @submit.prevent="addTask">
            <input
              v-model="newTaskTitle"
              type="text"
              class="input"
              placeholder="Título de la tarea"
            />
            <select v-model="selectedAreaId" class="select-area" aria-label="Área">
              <option :value="null">One shot</option>
              <option
                v-for="area in orderedAreas"
                :key="area.id"
                :value="area.id"
              >
                {{ area.name }}
              </option>
            </select>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="savingTask || !newTaskTitle.trim()"
            >
              Añadir
            </button>
          </form>
        </section>

        <!-- Toggle vista lista / agrupado -->
        <div class="view-toggle-row">
          <button
            type="button"
            class="view-toggle-btn"
            :class="{ active: viewMode === 'list' }"
            @click="viewMode = 'list'"
          >
            Lista
          </button>
          <button
            type="button"
            class="view-toggle-btn"
            :class="{ active: viewMode === 'grouped' }"
            @click="viewMode = 'grouped'"
          >
            Agrupado por área
          </button>
        </div>

        <div v-if="hasNoTasks" class="empty">
          <p>No hay tareas. Crea una arriba o añade siguientes acciones en un proyecto.</p>
        </div>

        <!-- Vista lista: una lista con área a la derecha -->
        <div v-else-if="viewMode === 'list'" class="tareas-scroll">
          <div class="task-list">
            <div
              v-for="item in flatTaskList"
              :key="item.type + '-' + item.id"
              class="task-row"
              :class="{ done: item.done }"
            >
              <input
                type="checkbox"
                :checked="item.done"
                class="task-checkbox"
                @change="toggleTask(item)"
              />
              <span class="task-title">{{ item.title }}</span>
              <span class="task-area-badge">{{ item.areaName }}</span>
              <button
                v-if="item.type === 'oneshot'"
                type="button"
                class="btn-delete"
                aria-label="Eliminar"
                @click="deleteOneShot(item.raw)"
              >
                ×
              </button>
              <button
                v-else
                type="button"
                class="btn-delete"
                aria-label="Eliminar"
                @click="deleteNextAction(item.raw)"
              >
                ×
              </button>
            </div>
          </div>
        </div>

        <!-- Vista agrupada por área -->
        <div v-else class="tareas-scroll">
          <section
            v-for="group in groupedTaskList"
            :key="group.areaKey"
            class="area-section"
            :style="group.area ? areaSectionStyle(group.area) : areaSectionStyleOneshot()"
          >
            <h2 class="area-title">{{ group.areaName }}</h2>
            <div class="task-list">
              <div
                v-for="item in group.items"
                :key="item.type + '-' + item.id"
                class="task-row"
                :class="{ done: item.done }"
              >
                <input
                  type="checkbox"
                  :checked="item.done"
                  class="task-checkbox"
                  @change="toggleTask(item)"
                />
                <span v-if="item.project" class="task-project-meta">
                  <AppIcon
                    :name="item.project.icon || 'FileText'"
                    :size="20"
                    class="task-project-icon"
                  />
                  <span class="task-project-name">{{ item.project.name }}</span>
                </span>
                <span class="task-title">{{ item.title }}</span>
                <button
                  v-if="item.type === 'oneshot'"
                  type="button"
                  class="btn-delete"
                  aria-label="Eliminar"
                  @click="deleteOneShot(item.raw)"
                >
                  ×
                </button>
                <button
                  v-else
                  type="button"
                  class="btn-delete"
                  aria-label="Eliminar"
                  @click="deleteNextAction(item.raw)"
                >
                  ×
                </button>
              </div>
              <p v-if="group.items.length === 0" class="no-tasks">Sin tareas en esta área</p>
            </div>
          </section>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from '../components/AppIcon.vue'
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
const newTaskTitle = ref('')
const selectedAreaId = ref(null) // null = One shot
const savingTask = ref(false)
const viewMode = ref('grouped') // 'list' | 'grouped'

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

function areaNameById(areaId) {
  if (areaId == null) return 'One shot'
  const a = areas.value.find((x) => x.id === areaId)
  return a ? a.name : 'One shot'
}

function areaSectionStyle(area) {
  const color = area?.color || DEFAULT_AREA_ACCENT
  return { '--area-accent': color, borderLeftColor: color }
}

function areaSectionStyleOneshot() {
  return { '--area-accent': 'var(--text-muted)', borderLeftColor: 'var(--text-muted)' }
}

/** Lista plana para vista lista: one-shots + next actions con areaName */
const flatTaskList = computed(() => {
  const list = []
  for (const task of oneShotTasks.value) {
    list.push({
      type: 'oneshot',
      id: task.id,
      title: task.title,
      done: task.done,
      areaName: areaNameById(task.area_id),
      raw: task,
    })
  }
  for (const project of projects.value) {
    const areaName = areaNameById(project.area_id)
    for (const na of project.next_actions || []) {
      list.push({
        type: 'nextaction',
        id: na.id,
        title: na.title,
        done: na.done,
        areaName,
        project,
        raw: na,
      })
    }
  }
  return list.sort((a, b) => (a.done === b.done ? 0 : a.done ? 1 : -1))
})

/** Agrupado por área: One shot primero, luego áreas ordenadas; cada grupo con items */
const groupedTaskList = computed(() => {
  const groups = []
  const areaIds = [...new Set(orderedAreas.value.map((a) => a.id))]
  // One shot
  const oneShotItems = oneShotTasks.value
    .filter((t) => t.area_id == null)
    .map((t) => ({
      type: 'oneshot',
      id: t.id,
      title: t.title,
      done: t.done,
      raw: t,
      project: null,
    }))
  groups.push({
    areaKey: 'oneshot',
    areaName: 'One shot',
    area: null,
    items: oneShotItems,
  })
  // Por área: one-shots de esa área + next actions de proyectos de esa área
  for (const area of orderedAreas.value) {
    const items = []
    for (const t of oneShotTasks.value) {
      if (t.area_id === area.id) {
        items.push({
          type: 'oneshot',
          id: t.id,
          title: t.title,
          done: t.done,
          raw: t,
          project: null,
        })
      }
    }
    for (const p of projects.value) {
      if (p.area_id !== area.id) continue
      for (const na of p.next_actions || []) {
        items.push({
          type: 'nextaction',
          id: na.id,
          title: na.title,
          done: na.done,
          raw: na,
          project: p,
        })
      }
    }
    groups.push({
      areaKey: 'area-' + area.id,
      areaName: area.name,
      area,
      items,
    })
  }
  return groups
})

const hasNoTasks = computed(() => {
  const hasOneShots = oneShotTasks.value.length > 0
  const hasNextActions = projects.value.some(
    (p) => Array.isArray(p.next_actions) && p.next_actions.length > 0
  )
  return !hasOneShots && !hasNextActions
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

async function addTask() {
  const title = newTaskTitle.value.trim()
  if (!title || savingTask.value) return
  savingTask.value = true
  try {
    const created = await post('one-shot-tasks', {
      title,
      area_id: selectedAreaId.value ?? null,
    })
    oneShotTasks.value = [...oneShotTasks.value, created]
    newTaskTitle.value = ''
  } catch (e) {
    error.value = e.message || 'Error al crear'
  } finally {
    savingTask.value = false
  }
}

function toggleTask(item) {
  if (item.type === 'oneshot') {
    toggleOneShotDone(item.raw)
  } else {
    toggleNextActionDone(item.raw)
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

async function toggleNextActionDone(na) {
  try {
    const updated = await patch(`project-next-actions/${na.id}`, { done: !na.done })
    const proj = projects.value.find((p) => p.id === na.project_id)
    if (proj?.next_actions) {
      const j = proj.next_actions.findIndex((a) => a.id === na.id)
      if (j !== -1) proj.next_actions[j] = { ...proj.next_actions[j], ...updated }
    }
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

async function deleteNextAction(na) {
  if (!confirm('¿Eliminar esta siguiente acción?')) return
  try {
    await del(`project-next-actions/${na.id}`)
    const proj = projects.value.find((p) => p.id === na.project_id)
    if (proj?.next_actions) {
      proj.next_actions = proj.next_actions.filter((a) => a.id !== na.id)
    }
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

.creator-section {
  margin-bottom: 1rem;
}

.add-task-form {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  align-items: center;
}

.add-task-form .input {
  flex: 1;
  min-width: 120px;
}

.select-area {
  padding: 0.5rem 0.75rem;
  font-size: 0.95rem;
  color: var(--text);
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: 0.5rem;
  outline: none;
  min-width: 140px;
}

.view-toggle-row {
  display: flex;
  gap: 0.25rem;
  margin-bottom: 1rem;
}

.view-toggle-btn {
  padding: 0.4rem 0.75rem;
  font-size: 0.9rem;
  background: var(--hover-bg);
  color: var(--text-muted);
  border: 1px solid var(--card-border);
  border-radius: 0.5rem;
  cursor: pointer;
}

.view-toggle-btn.active {
  background: var(--primary-bg, rgba(99, 102, 241, 0.15));
  color: var(--primary);
  border-color: var(--primary);
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

.area-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-strong);
  margin: 0 0 0.5rem 0;
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

.task-row.done .task-title {
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

.task-area-badge {
  flex-shrink: 0;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.task-checkbox {
  flex-shrink: 0;
  width: 1.1rem;
  height: 1.1rem;
  cursor: pointer;
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

.input {
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
