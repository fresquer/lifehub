<template>
  <div class="page">
    <main class="main">
      <p v-if="loading" class="status">Cargando…</p>
      <p v-else-if="loadError" class="status error">{{ loadError }}</p>
      <template v-else>
        <section class="config-section">
          <h2 class="section-title">Áreas principales del proyecto</h2>
          <p class="section-desc">Crea, reordena y edita las áreas que organizan tu vida. El orden aquí se usa en la vista de Áreas y proyectos.</p>

          <div class="add-area-card">
            <h3 class="card-title">Nueva área</h3>
            <form class="add-form" @submit.prevent="createArea">
              <input
                v-model="newName"
                type="text"
                class="input"
                placeholder="Nombre del área"
                required
              />
              <textarea
                v-model="newDescription"
                class="textarea"
                placeholder="Descripción (opcional)"
                rows="2"
              />
              <div class="color-picker-wrap">
                <span class="color-label">Color</span>
                <div class="color-palette" role="group" aria-label="Elegir color del área">
                  <button
                    v-for="c in AREA_PALETTE"
                    :key="c"
                    type="button"
                    class="color-swatch"
                    :class="{ selected: newColor === c }"
                    :style="{ background: c }"
                    :title="c"
                    :aria-pressed="newColor === c"
                    @click="newColor = newColor === c ? null : c"
                  />
                  <button
                    v-if="newColor !== null"
                    type="button"
                    class="color-swatch color-swatch-none"
                    title="Sin color (acento por defecto)"
                    aria-label="Quitar color"
                    @click="newColor = null"
                  >
                    —
                  </button>
                </div>
              </div>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                {{ saving ? 'Guardando…' : 'Crear área' }}
              </button>
            </form>
          </div>

          <div class="areas-list-wrap">
            <h3 class="card-title">Reordenar y gestionar</h3>
            <div v-if="orderedAreas.length === 0" class="empty-list">
              Aún no hay áreas. Crea una arriba.
            </div>
            <ul v-else class="areas-list" role="list">
              <li
                v-for="(area, index) in orderedAreas"
                :key="area.id"
                class="area-row"
                :class="{ editing: editingId === area.id }"
              >
                <div class="area-row-drag">
                  <button
                    type="button"
                    class="btn-icon"
                    title="Subir"
                    :disabled="index === 0"
                    @click="moveUp(index)"
                  >
                    ↑
                  </button>
                  <button
                    type="button"
                    class="btn-icon"
                    title="Bajar"
                    :disabled="index === orderedAreas.length - 1"
                    @click="moveDown(index)"
                  >
                    ↓
                  </button>
                </div>
                <div v-if="editingId === area.id" class="area-row-edit">
                  <input
                    ref="editNameRef"
                    v-model="editName"
                    type="text"
                    class="input input-inline"
                    placeholder="Nombre"
                    @keydown.enter.prevent="saveEdit(area)"
                    @keydown.esc="cancelEdit"
                  />
                  <textarea
                    v-model="editDescription"
                    class="textarea textarea-inline"
                    placeholder="Descripción"
                    rows="2"
                  />
                  <div class="color-picker-wrap">
                    <span class="color-label">Color</span>
                    <div class="color-palette" role="group" aria-label="Elegir color del área">
                      <button
                        v-for="c in AREA_PALETTE"
                        :key="c"
                        type="button"
                        class="color-swatch"
                        :class="{ selected: editColor === c }"
                        :style="{ background: c }"
                        :title="c"
                        :aria-pressed="editColor === c"
                        @click="editColor = editColor === c ? null : c"
                      />
                      <button
                        v-if="editColor !== null"
                        type="button"
                        class="color-swatch color-swatch-none"
                        title="Sin color (acento por defecto)"
                        aria-label="Quitar color"
                        @click="editColor = null"
                      >
                        —
                      </button>
                    </div>
                  </div>
                  <div class="edit-actions">
                    <button type="button" class="btn btn-sm" @click="cancelEdit">Cancelar</button>
                    <button type="button" class="btn btn-sm btn-primary" :disabled="saving" @click="saveEdit(area)">
                      Guardar
                    </button>
                  </div>
                </div>
                <template v-else>
                  <div
                    v-if="area.color"
                    class="area-row-color-dot"
                    :style="{ background: area.color }"
                    :title="'Color: ' + area.color"
                  />
                  <div class="area-row-info">
                    <span class="area-name">{{ area.name }}</span>
                    <span v-if="area.description" class="area-desc">{{ area.description }}</span>
                  </div>
                  <div class="area-row-actions">
                    <button type="button" class="btn-icon" title="Editar" @click="startEdit(area)" aria-label="Editar">
                      <Pencil :size="18" aria-hidden="true" />
                    </button>
                    <button
                      type="button"
                      class="btn-icon danger"
                      title="Eliminar"
                      :disabled="saving"
                      aria-label="Eliminar"
                      @click="confirmDelete(area)"
                    >
                      <Trash2 :size="18" aria-hidden="true" />
                    </button>
                  </div>
                </template>
              </li>
            </ul>
          </div>
        </section>
      </template>
    </main>

    <!-- Confirmación eliminar -->
    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="areaToDelete"
          class="modal-backdrop"
          @click.self="areaToDelete = null"
        >
          <div class="modal-card modal-sm" role="dialog" aria-modal="true">
            <div class="modal-header">
              <h2 class="modal-title">Eliminar área</h2>
              <button type="button" class="modal-close" aria-label="Cerrar" @click="areaToDelete = null">×</button>
            </div>
            <div class="modal-body">
              <p>¿Eliminar «{{ areaToDelete?.name }}»? Se eliminarán también todos los proyectos de esta área.</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn" @click="areaToDelete = null">Cancelar</button>
              <button type="button" class="btn btn-danger" :disabled="saving" @click="doDelete(areaToDelete)">
                {{ saving ? 'Eliminando…' : 'Eliminar' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { Pencil, Trash2 } from 'lucide-vue-next'
import { useAuth } from '../composables/useAuth'
import { useApi } from '../composables/useApi'

const STORAGE_KEY = 'lifehub_area_order'

/** 16 colores diferenciados y agradables para las áreas (hex). */
const AREA_PALETTE = [
  '#f97316', '#eab308', '#84cc16', '#22c55e', '#14b8a6', '#06b6d4', '#0ea5e9', '#3b82f6',
  '#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e', '#64748b', '#94a3b8',
]

const { fetchUser } = useAuth()
const { get, post, patch, delete: apiDelete } = useApi()

const loading = ref(true)
const loadError = ref('')
const areas = ref([])
const saving = ref(false)
const newName = ref('')
const newDescription = ref('')
const newColor = ref(null)
const editingId = ref(null)
const editName = ref('')
const editDescription = ref('')
const editColor = ref(null)
const editNameRef = ref(null)
const areaToDelete = ref(null)

function getStoredOrder() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const arr = JSON.parse(raw)
    return Array.isArray(arr) ? arr.filter(Number.isInteger) : []
  } catch {
    return []
  }
}

function setStoredOrder(ids) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(ids))
}

const orderedAreas = computed(() => {
  const order = getStoredOrder()
  const byId = Object.fromEntries(areas.value.map((a) => [a.id, a]))
  const result = []
  for (const id of order) {
    if (byId[id]) {
      result.push(byId[id])
      delete byId[id]
    }
  }
  const rest = Object.values(byId)
  rest.sort((a, b) => a.name.localeCompare(b.name))
  return result.concat(rest)
})

async function loadAreas() {
  loading.value = true
  loadError.value = ''
  try {
    areas.value = await get('areas')
    const order = getStoredOrder()
    const ids = new Set(areas.value.map((a) => a.id))
    const validOrder = order.filter((id) => ids.has(id))
    const newIds = areas.value.map((a) => a.id).filter((id) => !validOrder.includes(id))
    if (validOrder.length !== order.length || newIds.length) {
      setStoredOrder([...validOrder, ...newIds])
    }
  } catch (e) {
    loadError.value = e.message || 'Error al cargar áreas'
  } finally {
    loading.value = false
  }
}

function moveUp(index) {
  if (index <= 0) return
  const order = orderedAreas.value.map((a) => a.id)
  ;[order[index - 1], order[index]] = [order[index], order[index - 1]]
  setStoredOrder(order)
}

function moveDown(index) {
  if (index >= orderedAreas.value.length - 1) return
  const order = orderedAreas.value.map((a) => a.id)
  ;[order[index], order[index + 1]] = [order[index + 1], order[index]]
  setStoredOrder(order)
}

async function createArea() {
  if (!newName.value.trim()) return
  saving.value = true
  try {
    const created = await post('areas', {
      name: newName.value.trim(),
      description: newDescription.value.trim() || null,
      color: newColor.value || null,
    })
    areas.value = [...areas.value, created]
    const order = getStoredOrder()
    if (!order.includes(created.id)) {
      setStoredOrder([...order, created.id])
    }
    newName.value = ''
    newDescription.value = ''
    newColor.value = null
  } catch (e) {
    loadError.value = e.message || 'Error al crear área'
  } finally {
    saving.value = false
  }
}

function startEdit(area) {
  editingId.value = area.id
  editName.value = area.name
  editDescription.value = area.description || ''
  editColor.value = area.color ?? null
  nextTick(() => editNameRef.value?.focus())
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit(area) {
  saving.value = true
  try {
    const updated = await patch(`areas/${area.id}`, {
      name: editName.value.trim(),
      description: editDescription.value.trim() || null,
      color: editColor.value || null,
    })
    const i = areas.value.findIndex((a) => a.id === area.id)
    if (i >= 0) areas.value[i] = updated
    editingId.value = null
  } catch (e) {
    loadError.value = e.message || 'Error al guardar'
  } finally {
    saving.value = false
  }
}

function confirmDelete(area) {
  areaToDelete.value = area
}

async function doDelete(area) {
  if (!area) return
  saving.value = true
  try {
    await apiDelete(`areas/${area.id}`)
    areas.value = areas.value.filter((a) => a.id !== area.id)
    const order = getStoredOrder().filter((id) => id !== area.id)
    setStoredOrder(order)
    areaToDelete.value = null
  } catch (e) {
    loadError.value = e.message || 'Error al eliminar'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await fetchUser()
  await loadAreas()
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
  max-width: 640px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem;
  width: 100%;
}

.status { text-align: center; color: var(--text-muted); padding: 2rem; }
.status.error { color: var(--danger); }

.config-section { display: flex; flex-direction: column; gap: 1.5rem; }
.section-title { font-size: 1.35rem; font-weight: 600; margin: 0 0 0.25rem 0; color: var(--text-strong); }
.section-desc { font-size: 0.9rem; color: var(--text-muted); margin: 0; line-height: 1.45; }

.add-area-card,
.areas-list-wrap {
  background: var(--hover-bg);
  border: 1px solid var(--card-border-subtle);
  border-radius: 1rem;
  padding: 1.25rem;
}

.card-title { font-size: 1rem; font-weight: 600; color: var(--text); margin: 0 0 0.75rem 0; }

.add-form { display: flex; flex-direction: column; gap: 0.75rem; }

.color-picker-wrap { display: flex; flex-direction: column; gap: 0.35rem; }
.color-label { font-size: 0.85rem; font-weight: 500; color: var(--text-muted); }
.color-palette { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.color-swatch {
  width: 28px;
  height: 28px;
  border-radius: 0.5rem;
  border: 2px solid transparent;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
.color-swatch:hover { transform: scale(1.1); box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3); }
.color-swatch.selected { border-color: var(--text-strong); box-shadow: 0 0 0 1px var(--card-border); }
.color-swatch-none {
  background: var(--hover-bg) !important;
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1;
}

.area-row-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 0.2rem;
}

.input, .textarea {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: var(--text);
  font-size: 0.95rem;
}

.input::placeholder,
.textarea::placeholder { color: var(--input-placeholder); }
.textarea { resize: vertical; min-height: 56px; }

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid transparent;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-primary { background: var(--primary); color: #fff; border-color: var(--primary); }
.btn-primary:hover:not(:disabled) { background: var(--primary-hover); border-color: var(--primary-hover); }
.btn-sm { padding: 0.35rem 0.75rem; font-size: 0.85rem; }
.btn-danger { background: var(--danger); color: #fff; border-color: var(--danger); }
.btn-danger:hover:not(:disabled) { background: var(--danger-hover); border-color: var(--danger-hover); }

.empty-list {
  text-align: center;
  color: var(--input-placeholder);
  padding: 1.5rem;
  font-size: 0.95rem;
}

.areas-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.area-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--input-bg);
  border: 1px solid var(--card-border-subtle);
  border-radius: 0.75rem;
  flex-wrap: wrap;
}

.area-row-drag { display: flex; gap: 0.25rem; flex-shrink: 0; }
.btn-icon {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 0.4rem;
  background: var(--hover-bg);
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-icon:hover:not(:disabled) { background: var(--hover-bg); color: var(--text); }
.btn-icon:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-icon.danger:hover:not(:disabled) { background: var(--danger-bg); color: var(--danger); }

.area-row-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.15rem; }
.area-name { font-weight: 600; color: var(--text-strong); }
.area-desc { font-size: 0.85rem; color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 280px; }
.area-row-actions { display: flex; gap: 0.25rem; }

.area-row-edit { flex: 1; display: flex; flex-direction: column; gap: 0.5rem; min-width: 0; }
.input-inline, .textarea-inline { width: 100%; }
.edit-actions { display: flex; gap: 0.5rem; }

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: var(--overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 1rem;
  max-width: 420px;
  width: 100%;
  box-shadow: var(--shadow-modal-lg);
}
.modal-card.modal-sm { max-width: 360px; }

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--topbar-border);
}
.modal-title { font-size: 1.1rem; font-weight: 600; margin: 0; color: var(--text-strong); }
.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 0.5rem;
  background: transparent;
  color: var(--text-muted);
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
}
.modal-close:hover { background: var(--hover-bg); color: var(--text); }

.modal-body { padding: 1.25rem; color: var(--text-muted); font-size: 0.95rem; line-height: 1.5; }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--topbar-border);
}

.modal-enter-active,
.modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from,
.modal-leave-to { opacity: 0; }
</style>
