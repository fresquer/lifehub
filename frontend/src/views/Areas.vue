<template>
  <div class="page">
    <main class="main">
      <p v-if="loading" class="status">Cargando áreas y proyectos…</p>
      <p v-else-if="error" class="status error">{{ error }}</p>
      <template v-else>
        <div v-if="areas.length === 0" class="empty">
          <p>Aún no tienes áreas. Crea una para organizar tus proyectos.</p>
        </div>
        <div v-else class="areas-scroll">
          <section
            v-for="area in orderedAreas"
            :key="area.id"
            class="area-section"
            :style="areaSectionStyle(area)"
          >
            <div class="area-header">
              <div class="area-header-text">
                <h2 class="area-title">{{ area.name }}</h2>
                <p v-if="area.description" class="area-desc">{{ area.description }}</p>
              </div>
              <button
                type="button"
                class="btn-add-project"
                :disabled="addingAreaId === area.id"
                @click="addProject(area)"
              >
                + Añadir proyecto
              </button>
            </div>
            <div class="projects-row">
              <div
                v-for="project in projectsByArea[area.id]"
                :key="project.id"
                class="project-card"
                role="button"
                tabindex="0"
                @click="editingProjectId === project.id ? null : openModal(project)"
                @keydown.enter.space.prevent="editingProjectId !== project.id && openModal(project)"
              >
                <template v-if="editingProjectId === project.id">
                  <span class="project-card-icon">{{ project.icon || DEFAULT_ICON }}</span>
                  <input
                    ref="projectTitleInputRef"
                    v-model="editingTitle"
                    type="text"
                    class="project-name-input"
                    placeholder="Título del proyecto"
                    @click.stop
                    @keydown.space.stop
                    @blur="saveProjectTitle(project)"
                    @keydown.enter.stop="saveProjectTitle(project)"
                  />
                </template>
                <template v-else>
                  <span class="project-card-icon">{{ project.icon || DEFAULT_ICON }}</span>
                  <h3 class="project-name">{{ project.name }}</h3>
                  <p v-if="project.description" class="project-desc">{{ project.description }}</p>
                </template>
              </div>
              <div v-if="!(projectsByArea[area.id]?.length)" class="no-projects">
                Sin proyectos en esta área
              </div>
            </div>
          </section>
        </div>
      </template>
    </main>

    <!-- Modal detalles proyecto (edición + borrar) -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="selectedProject"
          class="modal-backdrop"
          @click.self="closeModal"
        >
          <div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="modal-title">
            <div class="modal-header">
              <div class="modal-title-row">
                <div class="emoji-wrap" ref="emojiPickerWrapRef">
                  <button
                    type="button"
                    class="emoji-trigger"
                    aria-label="Cambiar icono"
                    @click.stop="emojiPickerOpen = !emojiPickerOpen"
                  >
                    {{ modalIcon || DEFAULT_ICON }}
                  </button>
                  <Transition name="picker">
                    <div v-if="emojiPickerOpen" class="emoji-picker-wrap" @click.stop>
                      <EmojiPicker
                        :native="true"
                        theme="dark"
                        :hide-search="false"
                        :static-texts="{ placeholder: 'Buscar emoji…' }"
                        @select="pickEmoji"
                      />
                    </div>
                  </Transition>
                </div>
                <input
                  id="modal-title"
                  v-model="modalTitle"
                  type="text"
                  class="modal-title-input"
                  placeholder="Título del proyecto"
                />
              </div>
              <button
                type="button"
                class="modal-close"
                aria-label="Cerrar"
                @click="closeModal"
              >
                ×
              </button>
            </div>
            <div class="modal-body">
              <label class="modal-label">Descripción</label>
              <textarea
                v-model="modalDescription"
                class="modal-desc-input"
                placeholder="Añade una descripción…"
                rows="4"
              />
              <p class="modal-area">
                <span class="modal-label">Área:</span>
                {{ areaNameFor(selectedProject) }}
              </p>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="modal-btn modal-btn-danger"
                :disabled="modalSaving"
                @click="deleteProject"
              >
                Borrar proyecto
              </button>
              <div class="modal-footer-right">
                <button type="button" class="modal-btn modal-btn-secondary" @click="closeModal">
                  Cancelar
                </button>
                <button
                  type="button"
                  class="modal-btn modal-btn-primary"
                  :disabled="modalSaving"
                  @click="saveModalProject"
                >
                  Guardar
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useAuth } from '../composables/useAuth'
import { useApi } from '../composables/useApi'
import EmojiPicker from 'vue3-emoji-picker'
import 'vue3-emoji-picker/css'

const { fetchUser } = useAuth()
const { get, post, patch, delete: del } = useApi()

const DEFAULT_ICON = '📄'

const loading = ref(true)
const error = ref('')
const areas = ref([])
const projects = ref([])
const addingAreaId = ref(null)
const editingProjectId = ref(null)
const editingTitle = ref('')
const selectedProject = ref(null)
const projectTitleInputRef = ref(null)
const modalTitle = ref('')
const modalDescription = ref('')
const modalIcon = ref('')
const modalSaving = ref(false)
const emojiPickerOpen = ref(false)
const emojiPickerWrapRef = ref(null)

const AREA_ORDER_KEY = 'lifehub_area_order'

/** Acento por defecto cuando el área no tiene color. */
const DEFAULT_AREA_ACCENT = '#64748b'

function areaSectionStyle(area) {
  const color = area.color || DEFAULT_AREA_ACCENT
  return {
    '--area-accent': color,
    borderLeftColor: color,
  }
}

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

const projectsByArea = computed(() => {
  const byId = {}
  for (const a of areas.value) byId[a.id] = []
  for (const p of projects.value) {
    if (byId[p.area_id]) byId[p.area_id].push(p)
  }
  return byId
})

function areaNameFor(project) {
  if (!project) return ''
  return areas.value.find((a) => a.id === project.area_id)?.name ?? ''
}

async function addProject(area) {
  if (addingAreaId.value) return
  addingAreaId.value = area.id
  try {
    const created = await post('projects', {
      area_id: area.id,
      name: 'Nuevo proyecto',
      icon: DEFAULT_ICON,
    })
    projects.value = [...projects.value, created]
    editingProjectId.value = created.id
    editingTitle.value = created.name
    await nextTick()
    const el = Array.isArray(projectTitleInputRef.value)
      ? projectTitleInputRef.value[0]
      : projectTitleInputRef.value
    el?.focus()
  } catch (e) {
    error.value = e.message || 'Error al crear proyecto'
  } finally {
    addingAreaId.value = null
  }
}

function openModal(project) {
  selectedProject.value = project
  modalTitle.value = project.name
  modalDescription.value = project.description ?? ''
  modalIcon.value = project.icon ?? ''
  emojiPickerOpen.value = false
}

function pickEmoji(emoji) {
  if (emoji?.i) modalIcon.value = emoji.i
  emojiPickerOpen.value = false
}

function closeModal() {
  selectedProject.value = null
}

async function saveModalProject() {
  if (!selectedProject.value || modalSaving.value) return
  const name = (modalTitle.value || '').trim() || selectedProject.value.name
  const description = (modalDescription.value || '').trim() || null
  const icon = modalIcon.value || null
  modalSaving.value = true
  try {
    const updated = await patch(`projects/${selectedProject.value.id}`, { name, description, icon })
    const i = projects.value.findIndex((p) => p.id === selectedProject.value.id)
    if (i !== -1) projects.value[i] = { ...projects.value[i], ...updated }
    selectedProject.value = { ...selectedProject.value, ...updated }
  } catch (e) {
    error.value = e.message || 'Error al guardar'
  } finally {
    modalSaving.value = false
  }
}

async function deleteProject() {
  if (!selectedProject.value || modalSaving.value) return
  if (!confirm('¿Borrar este proyecto? Esta acción no se puede deshacer.')) return
  modalSaving.value = true
  try {
    await del(`projects/${selectedProject.value.id}`)
    projects.value = projects.value.filter((p) => p.id !== selectedProject.value.id)
    closeModal()
  } catch (e) {
    error.value = e.message || 'Error al borrar'
  } finally {
    modalSaving.value = false
  }
}

async function saveProjectTitle(project) {
  if (editingProjectId.value !== project.id) return
  const name = (editingTitle.value || '').trim() || 'Nuevo proyecto'
  try {
    const updated = await patch(`projects/${project.id}`, { name })
    const i = projects.value.findIndex((p) => p.id === project.id)
    if (i !== -1) projects.value[i] = { ...projects.value[i], ...updated }
    editingProjectId.value = null
    editingTitle.value = ''
  } catch (e) {
    error.value = e.message || 'Error al guardar'
  }
}

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [areasData, projectsData] = await Promise.all([
      get('areas'),
      get('projects'),
    ])
    areas.value = areasData
    projects.value = projectsData
  } catch (e) {
    error.value = e.message || 'Error al cargar datos'
  } finally {
    loading.value = false
  }
}

function closeEmojiPicker(e) {
  if (emojiPickerOpen.value && emojiPickerWrapRef.value && !emojiPickerWrapRef.value.contains(e.target)) {
    emojiPickerOpen.value = false
  }
}

onMounted(async () => {
  await fetchUser()
  await loadData()
  document.addEventListener('click', closeEmojiPicker)
})

onUnmounted(() => {
  document.removeEventListener('click', closeEmojiPicker)
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-page, #0f172a);
  color: var(--text, #e2e8f0);
}

.main {
  flex: 1;
  padding: 1.5rem 1.25rem;
  overflow-y: auto;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.status {
  text-align: center;
  color: #94a3b8;
  padding: 2rem;
}

.status.error {
  color: #f87171;
}

.empty {
  text-align: center;
  color: #94a3b8;
  padding: 3rem 1.5rem;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 1rem;
  border: 1px dashed rgba(255, 255, 255, 0.12);
}

.areas-scroll {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.area-section {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-left: 8px solid var(--area-accent, var(--default-accent, #64748b));
  border-radius: 1rem;
  padding: 1.25rem;
}

.area-header {
  margin-bottom: 1rem;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.area-header-text {
  flex: 1;
  min-width: 0;
}

.btn-add-project {
  margin-left: auto;
  padding: 0.4rem 0.75rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--area-accent, #3b82f6);
  background: color-mix(in srgb, var(--area-accent, #3b82f6) 15%, transparent);
  border: 1px solid color-mix(in srgb, var(--area-accent, #3b82f6) 35%, transparent);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.btn-add-project:hover:not(:disabled) {
  background: color-mix(in srgb, var(--area-accent, #3b82f6) 25%, transparent);
  border-color: color-mix(in srgb, var(--area-accent, #3b82f6) 50%, transparent);
}

.btn-add-project:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.area-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0 0 0.25rem 0;
}

.area-desc {
  font-size: 0.9rem;
  color: #94a3b8;
  margin: 0;
  line-height: 1.4;
}

/* Grid de tarjetas de proyectos: 3 columnas que crece */
.projects-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

@media (max-width: 640px) {
  .projects-row {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 641px) and (max-width: 900px) {
  .projects-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

.project-card {
  min-height: 100px;
  padding: 1rem;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 0.4rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  transition: border-color 0.2s, background 0.2s;
}

.project-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.project-card:focus-visible {
  outline: 2px solid rgba(59, 130, 246, 0.6);
  outline-offset: 2px;
}

.project-card-icon {
  font-size: 1.4rem;
  line-height: 1;
  flex-shrink: 0;
}

.project-name-input {
  flex: 1;
  min-width: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.35rem;
  padding: 0.35rem 0.5rem;
  margin: 0;
  outline: none;
}

.project-name-input:focus {
  border-color: #3b82f6;
}

.project-name-input::placeholder {
  color: #64748b;
}

.project-name {
  flex: 1;
  min-width: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 0.35rem 0;
}

.project-desc {
  font-size: 0.85rem;
  color: #94a3b8;
  margin: 0;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.no-projects {
  grid-column: 1 / -1;
  padding: 1rem 1.5rem;
  color: #64748b;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  backdrop-filter: blur(4px);
}

.modal-card {
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 1rem;
  max-width: 420px;
  width: 100%;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.25rem 1.25rem 0.5rem;
}

.modal-title-row {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.emoji-wrap {
  position: relative;
  flex-shrink: 0;
}

.emoji-trigger {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.75rem;
  line-height: 1;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.emoji-trigger:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.18);
}

.emoji-picker-wrap {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  z-index: 10;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
}

.emoji-picker-wrap :deep(.VueEmojiPicker) {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.75rem;
}

.picker-enter-active,
.picker-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.picker-enter-from,
.picker-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.modal-title-input {
  flex: 1;
  min-width: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #f1f5f9;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  outline: none;
}

.modal-title-input:focus {
  border-color: #3b82f6;
}

.modal-title-input::placeholder {
  color: #64748b;
}

.modal-close {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  line-height: 1;
  color: #94a3b8;
  background: none;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: color 0.2s, background 0.2s;
}

.modal-close:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.08);
}

.modal-body {
  padding: 0.5rem 1.25rem 1rem;
}

.modal-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: #94a3b8;
  margin: 0 0 0.35rem 0;
}

.modal-desc-input {
  width: 100%;
  font-size: 0.95rem;
  color: #cbd5e1;
  line-height: 1.5;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 0.5rem;
  padding: 0.6rem 0.75rem;
  margin-bottom: 1rem;
  outline: none;
  resize: vertical;
  min-height: 80px;
}

.modal-desc-input:focus {
  border-color: #3b82f6;
}

.modal-desc-input::placeholder {
  color: #64748b;
}

.modal-area {
  font-size: 0.9rem;
  color: #94a3b8;
  margin: 0;
}

.modal-area .modal-label {
  display: inline;
  margin: 0;
}

.modal-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 1rem 1.25rem 1.25rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.modal-footer-right {
  display: flex;
  gap: 0.5rem;
}

.modal-btn {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s, background 0.2s;
}

.modal-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-btn-primary {
  background: #3b82f6;
  color: #fff;
}

.modal-btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.modal-btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.modal-btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
}

.modal-btn-danger {
  background: rgba(248, 113, 113, 0.15);
  color: #f87171;
  border: 1px solid rgba(248, 113, 113, 0.35);
}

.modal-btn-danger:hover:not(:disabled) {
  background: rgba(248, 113, 113, 0.25);
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
