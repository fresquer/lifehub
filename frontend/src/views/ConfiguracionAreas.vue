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
                  <div class="edit-actions">
                    <button type="button" class="btn btn-sm" @click="cancelEdit">Cancelar</button>
                    <button type="button" class="btn btn-sm btn-primary" :disabled="saving" @click="saveEdit(area)">
                      Guardar
                    </button>
                  </div>
                </div>
                <template v-else>
                  <div class="area-row-info">
                    <span class="area-name">{{ area.name }}</span>
                    <span v-if="area.description" class="area-desc">{{ area.description }}</span>
                  </div>
                  <div class="area-row-actions">
                    <button type="button" class="btn-icon" title="Editar" @click="startEdit(area)">✎</button>
                    <button
                      type="button"
                      class="btn-icon danger"
                      title="Eliminar"
                      :disabled="saving"
                      @click="confirmDelete(area)"
                    >
                      🗑
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
import { useAuth } from '../composables/useAuth'
import { useApi } from '../composables/useApi'

const STORAGE_KEY = 'lifehub_area_order'

const { fetchUser } = useAuth()
const { get, post, patch, delete: apiDelete } = useApi()

const loading = ref(true)
const loadError = ref('')
const areas = ref([])
const saving = ref(false)
const newName = ref('')
const newDescription = ref('')
const editingId = ref(null)
const editName = ref('')
const editDescription = ref('')
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
    })
    areas.value = [...areas.value, created]
    const order = getStoredOrder()
    if (!order.includes(created.id)) {
      setStoredOrder([...order, created.id])
    }
    newName.value = ''
    newDescription.value = ''
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
  background: var(--bg-page, #0f172a);
  color: var(--text, #e2e8f0);
}

.main {
  flex: 1;
  max-width: 640px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem;
  width: 100%;
}

.status { text-align: center; color: #94a3b8; padding: 2rem; }
.status.error { color: #f87171; }

.config-section { display: flex; flex-direction: column; gap: 1.5rem; }
.section-title { font-size: 1.35rem; font-weight: 600; margin: 0 0 0.25rem 0; color: #f1f5f9; }
.section-desc { font-size: 0.9rem; color: #94a3b8; margin: 0; line-height: 1.45; }

.add-area-card,
.areas-list-wrap {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
  padding: 1.25rem;
}

.card-title { font-size: 1rem; font-weight: 600; color: #e2e8f0; margin: 0 0 0.75rem 0; }

.add-form { display: flex; flex-direction: column; gap: 0.75rem; }
.input, .textarea {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(0, 0, 0, 0.2);
  color: #e2e8f0;
  font-size: 0.95rem;
}

.input::placeholder,
.textarea::placeholder { color: #64748b; }
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
.btn-primary { background: #3b82f6; color: #fff; border-color: #3b82f6; }
.btn-primary:hover:not(:disabled) { background: #2563eb; border-color: #2563eb; }
.btn-sm { padding: 0.35rem 0.75rem; font-size: 0.85rem; }
.btn-danger { background: #dc2626; color: #fff; border-color: #dc2626; }
.btn-danger:hover:not(:disabled) { background: #b91c1c; border-color: #b91c1c; }

.empty-list {
  text-align: center;
  color: #64748b;
  padding: 1.5rem;
  font-size: 0.95rem;
}

.areas-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.area-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.08);
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
  background: rgba(255, 255, 255, 0.08);
  color: #94a3b8;
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-icon:hover:not(:disabled) { background: rgba(255, 255, 255, 0.12); color: #e2e8f0; }
.btn-icon:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-icon.danger:hover:not(:disabled) { background: rgba(248, 113, 113, 0.15); color: #f87171; }

.area-row-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.15rem; }
.area-name { font-weight: 600; color: #f1f5f9; }
.area-desc { font-size: 0.85rem; color: #94a3b8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 280px; }
.area-row-actions { display: flex; gap: 0.25rem; }

.area-row-edit { flex: 1; display: flex; flex-direction: column; gap: 0.5rem; min-width: 0; }
.input-inline, .textarea-inline { width: 100%; }
.edit-actions { display: flex; gap: 0.5rem; }

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-card {
  background: #1e293b;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  max-width: 420px;
  width: 100%;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
}
.modal-card.modal-sm { max-width: 360px; }

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.modal-title { font-size: 1.1rem; font-weight: 600; margin: 0; color: #f1f5f9; }
.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 0.5rem;
  background: transparent;
  color: #94a3b8;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
}
.modal-close:hover { background: rgba(255, 255, 255, 0.08); color: #e2e8f0; }

.modal-body { padding: 1.25rem; color: #94a3b8; font-size: 0.95rem; line-height: 1.5; }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.modal-enter-active,
.modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-from,
.modal-leave-to { opacity: 0; }
</style>
