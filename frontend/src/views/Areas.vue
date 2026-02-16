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
          <!-- Proyectos pineados: sección fija arriba -->
          <section
            v-if="pinnedProjects.length > 0"
            class="area-section area-section-pinned"
          >
            <div class="area-header">
              <h2 class="area-title"><Pin :size="20" class="area-title-icon" aria-hidden="true" /> Proyectos pineados</h2>
            </div>
            <div class="projects-row">
              <div
                v-for="project in pinnedProjects"
                :key="project.id"
                class="project-card"
                role="button"
                tabindex="0"
                @click="
                  editingProjectId === project.id ? null : openModal(project)
                "
                @keydown.enter.space.prevent="
                  editingProjectId !== project.id && openModal(project)
                "
              >
                <button
                  type="button"
                  class="project-card-pin"
                  :class="{ 'project-card-pin--pinned': project.pinned }"
                  :aria-label="project.pinned ? 'Despinear' : 'Pinear'"
                  @click.stop="togglePin(project)"
                >
                  <Pin :size="14" aria-hidden="true" />
                </button>
                <template v-if="editingProjectId === project.id">
                  <AppIcon
                    :name="project.icon || DEFAULT_ICON"
                    :size="28"
                    class="project-card-icon"
                  />
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
                  <AppIcon
                    :name="project.icon || DEFAULT_ICON"
                    :size="28"
                    class="project-card-icon"
                  />
                  <h3 class="project-name">{{ project.name }}</h3>
                </template>
              </div>
            </div>
          </section>
          <section
            v-for="area in orderedAreas"
            :key="area.id"
            class="area-section"
            :style="areaSectionStyle(area)"
          >
            <div class="area-header">
              <div class="area-header-text">
                <h2 class="area-title">{{ area.name }}</h2>
                <p v-if="area.description" class="area-desc">
                  {{ area.description }}
                </p>
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
                @click="
                  editingProjectId === project.id ? null : openModal(project)
                "
                @keydown.enter.space.prevent="
                  editingProjectId !== project.id && openModal(project)
                "
              >
                <button
                  type="button"
                  class="project-card-pin"
                  :class="{ 'project-card-pin--pinned': project.pinned }"
                  :aria-label="project.pinned ? 'Despinear' : 'Pinear'"
                  @click.stop="togglePin(project)"
                >
                  <Pin :size="14" aria-hidden="true" />
                </button>
                <template v-if="editingProjectId === project.id">
                  <AppIcon
                    :name="project.icon || DEFAULT_ICON"
                    :size="28"
                    class="project-card-icon"
                  />
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
                  <AppIcon
                    :name="project.icon || DEFAULT_ICON"
                    :size="28"
                    class="project-card-icon"
                  />
                  <h3 class="project-name">{{ project.name }}</h3>
                </template>
              </div>
              <div v-if="!projectsByArea[area.id]?.length" class="no-projects">
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
          <div
            class="modal-card"
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
          >
            <div class="modal-header">
              <div class="modal-title-row">
                <div class="modal-icon-display" aria-hidden="true">
                  <AppIcon
                    :name="modalIcon || DEFAULT_ICON"
                    :size="28"
                  />
                </div>
                <input
                  id="modal-title"
                  v-model="modalTitle"
                  type="text"
                  class="modal-title-input"
                  placeholder="Título del proyecto"
                  @keydown.enter.prevent="saveModalProject"
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
              <div class="modal-next-actions-block">
                <label class="modal-label">Siguientes acciones</label>
                <div class="modal-next-actions-list">
                  <div
                    v-for="na in (selectedProject?.next_actions || [])"
                    :key="na.id"
                    class="modal-next-action-row"
                    :class="{ done: na.done }"
                  >
                    <input
                      type="checkbox"
                      :checked="na.done"
                      class="modal-next-action-checkbox"
                      @change="toggleModalNextAction(na)"
                    />
                    <span class="modal-next-action-title">{{ na.title }}</span>
                    <button
                      type="button"
                      class="modal-next-action-delete"
                      aria-label="Eliminar"
                      @click="deleteModalNextAction(na)"
                    >
                      ×
                    </button>
                  </div>
                </div>
                <div class="modal-next-action-add">
                  <input
                    v-model="newNextActionTitle"
                    type="text"
                    class="modal-next-action-input"
                    placeholder="Añadir siguiente acción…"
                    @keydown.enter.prevent="addModalNextAction"
                  />
                  <button
                    type="button"
                    class="modal-btn modal-btn-add"
                    :disabled="modalSaving || !newNextActionTitle.trim()"
                    @click="addModalNextAction"
                  >
                    Añadir
                  </button>
                </div>
              </div>
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
              <div class="modal-pinned-row">
                <button
                  type="button"
                  class="modal-pin-btn"
                  :class="{ 'modal-pin-btn--pinned': modalPinned }"
                  :aria-label="modalPinned ? 'Despinear' : 'Pinear'"
                  :title="modalPinned ? 'Despinear (quitar de arriba)' : 'Pinear (mostrar arriba en Áreas)'"
                  @click="modalPinned = !modalPinned"
                >
                  <Pin :size="18" aria-hidden="true" />
                </button>
                <span class="modal-pin-label">Proyecto pineado (aparece arriba en Áreas)</span>
              </div>
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
                <button
                  type="button"
                  class="modal-btn modal-btn-secondary"
                  @click="closeModal"
                >
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
import { ref, computed, onMounted, nextTick } from "vue";
import { Pin } from "lucide-vue-next";
import AppIcon from "../components/AppIcon.vue";
import {
  DEFAULT_PROJECT_ICON,
  PROJECT_ICON_NAMES,
} from "../components/projectIcons.js";
import { useAuth } from "../composables/useAuth";
import { useApi } from "../composables/useApi";

const { fetchUser } = useAuth();
const { get, post, patch, delete: del } = useApi();

const DEFAULT_ICON = DEFAULT_PROJECT_ICON;

const loading = ref(true);
const error = ref("");
const areas = ref([]);
const projects = ref([]);
const addingAreaId = ref(null);
const editingProjectId = ref(null);
const editingTitle = ref("");
const selectedProject = ref(null);
const projectTitleInputRef = ref(null);
const modalTitle = ref("");
const modalDescription = ref("");
const newNextActionTitle = ref("");
const modalIcon = ref("");
const modalPinned = ref(false);
const modalSaving = ref(false);

const AREA_ORDER_KEY = "lifehub_area_order";

/** Acento por defecto cuando el área no tiene color. */
const DEFAULT_AREA_ACCENT = "#64748b";

function areaSectionStyle(area) {
  const color = area.color || DEFAULT_AREA_ACCENT;
  return {
    "--area-accent": color,
    borderLeftColor: color,
  };
}

function getStoredAreaOrder() {
  try {
    const raw = localStorage.getItem(AREA_ORDER_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr.filter(Number.isInteger) : [];
  } catch {
    return [];
  }
}

const orderedAreas = computed(() => {
  const order = getStoredAreaOrder();
  const byId = Object.fromEntries(areas.value.map((a) => [a.id, a]));
  const result = [];
  for (const id of order) {
    if (byId[id]) {
      result.push(byId[id]);
      delete byId[id];
    }
  }
  result.push(
    ...Object.values(byId).sort((a, b) => a.name.localeCompare(b.name))
  );
  return result;
});

const pinnedProjects = computed(() => {
  return projects.value
    .filter((p) => p.pinned)
    .sort((a, b) => a.name.localeCompare(b.name));
});

const projectsByArea = computed(() => {
  const byId = {};
  for (const a of areas.value) byId[a.id] = [];
  for (const p of projects.value) {
    if (byId[p.area_id]) byId[p.area_id].push(p);
  }
  return byId;
});

function areaNameFor(project) {
  if (!project) return "";
  return areas.value.find((a) => a.id === project.area_id)?.name ?? "";
}

async function addProject(area) {
  if (addingAreaId.value) return;
  addingAreaId.value = area.id;
  try {
    const created = await post("projects", {
      area_id: area.id,
      name: "Nuevo proyecto",
      icon: DEFAULT_PROJECT_ICON,
    });
    projects.value = [...projects.value, created];
    editingProjectId.value = created.id;
    editingTitle.value = created.name;
    await nextTick();
    const el = Array.isArray(projectTitleInputRef.value)
      ? projectTitleInputRef.value[0]
      : projectTitleInputRef.value;
    el?.focus();
  } catch (e) {
    error.value = e.message || "Error al crear proyecto";
  } finally {
    addingAreaId.value = null;
  }
}

function openModal(project) {
  selectedProject.value = project;
  modalTitle.value = project.name;
  modalDescription.value = project.description ?? "";
  newNextActionTitle.value = "";
  const rawIcon = project.icon ?? "";
  modalIcon.value =
    PROJECT_ICON_NAMES.includes(rawIcon) ? rawIcon : DEFAULT_PROJECT_ICON;
  modalPinned.value = !!project.pinned;
}

function closeModal() {
  selectedProject.value = null;
}

async function addModalNextAction() {
  if (!selectedProject.value || modalSaving.value || !newNextActionTitle.value.trim()) return;
  modalSaving.value = true;
  try {
    const created = await post(`projects/${selectedProject.value.id}/next-actions`, {
      title: newNextActionTitle.value.trim(),
    });
    if (!selectedProject.value.next_actions) selectedProject.value.next_actions = [];
    selectedProject.value.next_actions = [...selectedProject.value.next_actions, created];
    const i = projects.value.findIndex((p) => p.id === selectedProject.value.id);
    if (i !== -1) {
      const nextActions = projects.value[i].next_actions || [];
      projects.value[i] = { ...projects.value[i], next_actions: [...nextActions, created] };
    }
    newNextActionTitle.value = "";
  } catch (e) {
    error.value = e.message || "Error al crear";
  } finally {
    modalSaving.value = false;
  }
}

async function toggleModalNextAction(na) {
  try {
    const updated = await patch(`project-next-actions/${na.id}`, { done: !na.done });
    const list = selectedProject.value?.next_actions;
    if (list) {
      const j = list.findIndex((a) => a.id === na.id);
      if (j !== -1) list[j] = { ...list[j], ...updated };
    }
    const proj = projects.value.find((p) => p.id === na.project_id);
    if (proj?.next_actions) {
      const k = proj.next_actions.findIndex((a) => a.id === na.id);
      if (k !== -1) proj.next_actions[k] = { ...proj.next_actions[k], ...updated };
    }
  } catch (e) {
    error.value = e.message || "Error al actualizar";
  }
}

async function deleteModalNextAction(na) {
  if (!confirm("¿Eliminar esta siguiente acción?")) return;
  try {
    await del(`project-next-actions/${na.id}`);
    if (selectedProject.value?.next_actions) {
      selectedProject.value.next_actions = selectedProject.value.next_actions.filter(
        (a) => a.id !== na.id
      );
    }
    const proj = projects.value.find((p) => p.id === na.project_id);
    if (proj?.next_actions) {
      proj.next_actions = proj.next_actions.filter((a) => a.id !== na.id);
    }
  } catch (e) {
    error.value = e.message || "Error al eliminar";
  }
}

async function saveModalProject() {
  if (!selectedProject.value || modalSaving.value) return;
  const name = (modalTitle.value || "").trim() || selectedProject.value.name;
  const description = (modalDescription.value || "").trim() || null;
  const icon = (modalIcon.value || DEFAULT_PROJECT_ICON) || null;
  const pinned = modalPinned.value;
  modalSaving.value = true;
  try {
    const updated = await patch(`projects/${selectedProject.value.id}`, {
      name,
      description,
      icon,
      pinned,
    });
    const i = projects.value.findIndex(
      (p) => p.id === selectedProject.value.id
    );
    if (i !== -1) projects.value[i] = { ...projects.value[i], ...updated };
    selectedProject.value = { ...selectedProject.value, ...updated };
    closeModal();
  } catch (e) {
    error.value = e.message || "Error al guardar";
  } finally {
    modalSaving.value = false;
  }
}

async function deleteProject() {
  if (!selectedProject.value || modalSaving.value) return;
  if (!confirm("¿Borrar este proyecto? Esta acción no se puede deshacer."))
    return;
  modalSaving.value = true;
  try {
    await del(`projects/${selectedProject.value.id}`);
    projects.value = projects.value.filter(
      (p) => p.id !== selectedProject.value.id
    );
    closeModal();
  } catch (e) {
    error.value = e.message || "Error al borrar";
  } finally {
    modalSaving.value = false;
  }
}

async function togglePin(project) {
  const nextPinned = !project.pinned;
  try {
    const updated = await patch(`projects/${project.id}`, { pinned: nextPinned });
    const i = projects.value.findIndex((p) => p.id === project.id);
    if (i !== -1) projects.value[i] = { ...projects.value[i], ...updated };
    if (selectedProject.value?.id === project.id) {
      selectedProject.value = { ...selectedProject.value, pinned: nextPinned };
      modalPinned.value = nextPinned;
    }
  } catch (e) {
    error.value = e.message || "Error al actualizar pineado";
  }
}

async function saveProjectTitle(project) {
  if (editingProjectId.value !== project.id) return;
  const name = (editingTitle.value || "").trim() || "Nuevo proyecto";
  try {
    const updated = await patch(`projects/${project.id}`, { name });
    const i = projects.value.findIndex((p) => p.id === project.id);
    if (i !== -1) projects.value[i] = { ...projects.value[i], ...updated };
    editingProjectId.value = null;
    editingTitle.value = "";
  } catch (e) {
    error.value = e.message || "Error al guardar";
  }
}

async function loadData() {
  loading.value = true;
  error.value = "";
  try {
    const [areasData, projectsData] = await Promise.all([
      get("areas"),
      get("projects"),
    ]);
    areas.value = areasData;
    projects.value = projectsData;
  } catch (e) {
    error.value = e.message || "Error al cargar datos";
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await fetchUser();
  await loadData();
});
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
  max-width: 1200px;
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
  background: var(--hover-bg);
  border-radius: 1rem;
  border: 1px dashed var(--card-border-subtle);
}

.areas-scroll {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.area-section {
  background: var(--hover-bg);
  border: 1px solid var(--card-border-subtle);
  border-left: 8px solid var(--area-accent, var(--default-accent));
  border-radius: 1rem;
  padding: 1.25rem;
}

.area-section-pinned {
  --area-accent: var(--primary, #6366f1);
  --pin-tint: color-mix(in srgb, var(--primary) 10%, transparent);
  --pin-border: color-mix(in srgb, var(--primary) 35%, var(--card-border-subtle));
  --pin-shadow: color-mix(in srgb, var(--primary) 18%, transparent);
  background: linear-gradient(135deg, var(--pin-tint) 0%, var(--hover-bg) 100%);
  border: 1px solid var(--pin-border);
  border-left: 6px solid var(--area-accent);
  box-shadow: 0 2px 12px var(--pin-shadow);
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
  color: var(--text-muted);
  background: var(--hover-bg);
  border: 1px solid var(--card-border);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.btn-add-project:hover:not(:disabled) {
  background: var(--hover-bg);
  border-color: var(--hover-border);
  color: var(--text);
}

.btn-add-project:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.area-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-strong);
  margin: 0 0 0.25rem 0;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.area-title-icon {
  flex-shrink: 0;
  color: var(--text-strong);
}

.area-desc {
  font-size: 0.9rem;
  color: var(--text-muted);
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
  position: relative;
  min-height: 100px;
  padding: 1rem;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 0.4rem;
  background: var(--hover-bg);
  border: 1px solid var(--card-border);
  border-radius: 0.75rem;
  transition: border-color 0.2s, background 0.2s;
}

.project-card-pin {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  line-height: 1;
  background: var(--card-bg, var(--hover-bg));
  border: 1px solid var(--card-border);
  border-radius: 0.35rem;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s, background 0.2s, border-color 0.2s;
}

.project-card:hover .project-card-pin {
  opacity: 1;
}

.project-card-pin:hover {
  background: var(--hover-bg);
  border-color: var(--hover-border);
}

.project-card-pin--pinned {
  border-color: var(--primary);
  background: var(--primary-bg, rgba(99, 102, 241, 0.15));
}

.project-card:hover {
  background: var(--hover-bg);
  border-color: var(--hover-border);
}

.project-card:focus-visible {
  outline: 2px solid var(--focus-ring);
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
  color: var(--text);
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: 0.35rem;
  padding: 0.35rem 0.5rem;
  margin: 0;
  outline: none;
}

.project-name-input:focus {
  border-color: var(--primary);
}

.project-name-input::placeholder {
  color: var(--input-placeholder);
}

.project-name {
  flex: 1;
  min-width: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 0.35rem 0;
}

.no-projects {
  grid-column: 1 / -1;
  padding: 1rem 1.5rem;
  color: var(--input-placeholder);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: var(--overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  backdrop-filter: blur(4px);
}

.modal-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 1rem;
  max-width: 420px;
  width: 100%;
  box-shadow: var(--shadow-modal-lg);
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

.modal-icon-display {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  color: var(--text);
}

.modal-title-input {
  flex: 1;
  min-width: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-strong);
  background: var(--input-bg);
  border: 1px solid var(--card-border);
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  outline: none;
}

.modal-title-input:focus {
  border-color: var(--primary);
}

.modal-title-input::placeholder {
  color: var(--input-placeholder);
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
  color: var(--text-muted);
  background: none;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: color 0.2s, background 0.2s;
}

.modal-close:hover {
  color: var(--text);
  background: var(--hover-bg);
}

.modal-body {
  padding: 0.5rem 1.25rem 1rem;
}

.modal-next-actions-block {
  margin-bottom: 1rem;
}

.modal-next-actions-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
}

.modal-next-action-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  padding: 0.4rem 0.5rem;
  background: var(--input-bg);
  border-radius: 0.5rem;
  border: 1px solid var(--card-border-subtle);
}

.modal-next-action-row.done .modal-next-action-title {
  text-decoration: line-through;
  color: var(--text-muted);
}

.modal-next-action-checkbox {
  flex-shrink: 0;
  width: 1.1rem;
  height: 1.1rem;
  cursor: pointer;
}

.modal-next-action-title {
  flex: 1;
  min-width: 0;
  font-size: 1rem;
  color: var(--text-strong);
  overflow: hidden;
  text-overflow: ellipsis;
}

.modal-next-action-delete {
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

.modal-next-action-delete:hover {
  color: var(--danger);
  background: var(--danger-bg);
}

.modal-next-action-add {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.modal-next-action-input {
  flex: 1;
  min-width: 0;
  font-size: 1rem;
  color: var(--text-strong);
  background: var(--input-bg);
  border: 1px solid var(--card-border);
  border-radius: 0.5rem;
  padding: 0.5rem 0.75rem;
  outline: none;
}

.modal-next-action-input:focus {
  border-color: var(--primary);
}

.modal-next-action-input::placeholder {
  color: var(--input-placeholder);
}

.modal-btn-add {
  flex-shrink: 0;
  background: var(--hover-bg);
  color: var(--text);
  border: 1px solid var(--card-border);
}

.modal-btn-add:hover:not(:disabled) {
  background: var(--hover-bg);
  border-color: var(--hover-border);
}

.modal-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-muted);
  margin: 0 0 0.35rem 0;
}

.modal-desc-input {
  width: 100%;
  font-size: 0.95rem;
  color: var(--text);
  line-height: 1.5;
  background: var(--input-bg);
  border: 1px solid var(--card-border);
  border-radius: 0.5rem;
  padding: 0.6rem 0.75rem;
  margin-bottom: 1rem;
  outline: none;
  resize: vertical;
  min-height: 80px;
}

.modal-desc-input:focus {
  border-color: var(--primary);
}

.modal-desc-input::placeholder {
  color: var(--input-placeholder);
}

.modal-area {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin: 0;
}

.modal-area .modal-label {
  display: inline;
  margin: 0;
}

.modal-pinned-row {
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.modal-pin-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  line-height: 1;
  background: var(--hover-bg);
  border: 1px solid var(--card-border);
  border-radius: 0.5rem;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.2s, background 0.2s, border-color 0.2s;
}

.modal-pin-btn:hover {
  opacity: 1;
  background: var(--hover-bg);
  border-color: var(--hover-border);
}

.modal-pin-btn--pinned {
  opacity: 1;
  border-color: var(--primary);
  background: var(--primary-bg, rgba(99, 102, 241, 0.15));
}

.modal-pin-label {
  font-size: 0.9rem;
  color: var(--text-muted);
}

.modal-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 1rem 1.25rem 1.25rem;
  border-top: 1px solid var(--topbar-border);
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
  background: var(--primary);
  color: #fff;
}

.modal-btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
}

.modal-btn-secondary {
  background: var(--hover-bg);
  color: var(--text);
  border: 1px solid var(--input-border);
}

.modal-btn-secondary:hover:not(:disabled) {
  background: var(--hover-bg);
}

.modal-btn-danger {
  background: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger-border);
}

.modal-btn-danger:hover:not(:disabled) {
  background: var(--danger-bg);
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
