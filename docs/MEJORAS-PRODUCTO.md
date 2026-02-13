# LifeHub – Análisis de producto y mejoras

Visión de producto y priorización de mejoras para LifeHub (perspectiva PO/gestión).

---

## Qué tienes hoy

- **Auth:** registro, login, JWT, perfil (email, nombre).
- **Modelo:** Usuario → Áreas → Proyectos. Áreas con nombre, descripción, color; proyectos con nombre, descripción, icono (emoji).
- **UX:** landing, dashboard de áreas/proyectos (tarjetas, modal edición/borrado), configuración de áreas (CRUD, reordenar, colores), perfil básico. Tema oscuro, orden de áreas en `localStorage`.

LifeHub hoy es sobre todo un **organizador visual** (áreas + proyectos). Falta la capa de "qué hago con esto" y varias cosas que un buen PO priorizaría.

---

## 1. Dar valor más allá de la estructura (core)

**Problema:** El usuario organiza áreas y proyectos pero no hay "siguiente paso" claro: no hay tareas, fechas ni progreso. El valor se queda en "tengo todo ordenado", no en "avanzar".

**Propuestas:**

- **Tareas (o "acciones") por proyecto:** Una entidad `Task` bajo `Project` (título, opcional: vencimiento, hecho/pendiente). Con eso el flujo es: Área → Proyecto → Tareas. Es el siguiente paso lógico para que LifeHub sea un "hub" de vida real.
- **Siguiente acción (GTD):** Un único campo "siguiente acción" por proyecto, visible en tarjeta y modal, centrando la experiencia en "¿qué hago ahora con este proyecto?".
- **Estado o progreso en proyecto:** Aunque sea un campo simple (`status`: planificado / en curso / pausado / completado) o un % manual, da sensación de avance y motivo para volver.

**Prioridad:** Alta. Sin esto, el producto se parece más a un "tablero de carpetas" que a un centro de vida.

---

## 2. Primer uso y activación

**Problema:** Usuario nuevo llega al dashboard vacío y solo ve "Aún no tienes áreas. Crea una…". La fricción es alta.

**Propuestas:**

- **Onboarding guiado:** Tras registro, un flujo corto: "Estas son áreas típicas: Salud, Trabajo, Familia, Finanzas, Crecimiento" con botón "Usar estas áreas" (crear todas de una vez) y luego "Añade tu primer proyecto en una de ellas".
- **Empty state por pasos:** En "Configuración áreas", si no hay áreas, un CTA grande "Crear mi primera área" con sugerencias de nombre.
- **Un solo lugar para "empezar":** Que desde el dashboard vacío se pueda ir directo a "configuración áreas" o a "crear área" sin tener que descubrir el menú.

**Prioridad:** Alta. Mejora retención día 1 y percepción de "esto me sirve".

---

## 3. Configuración y cuenta (confianza)

**Problema:** La pantalla "Configuración" dice "(Próximamente)". El usuario no puede cambiar contraseña ni gestionar su cuenta dentro de la app.

**Propuestas:**

- **Configuración mínima útil:** Cambio de contraseña, edición de nombre (y quizá avatar/iniciales). Quitar el "Próximamente" y dejar algo real.
- **Recuperación de contraseña:** "¿Olvidaste tu contraseña?" con flujo email (token o link). Necesita backend (envío de email) y posiblemente rate limiting en `/auth/forgot-password`.
- **Exportar mis datos:** Opción "Descargar mis datos" (áreas, proyectos, y en el futuro tareas) en JSON o CSV. Da confianza y cumple expectativas de privacidad.

**Prioridad:** Alta para cambio de contraseña y perfil; media para "olvidé contraseña" y exportación.

---

## 4. Experiencia en el dashboard (cuando crece)

**Problema:** Con muchas áreas y proyectos, la vista puede ser larga y difícil de escanear. El orden de proyectos dentro de un área no se persiste en backend.

**Propuestas:**

- **Orden de proyectos persistido:** Guardar `position` o `sort_order` en `Project` y ordenar por eso (y por nombre como respaldo). Dejar de depender solo del orden de llegada.
- **Colapsar/expandir áreas:** Poder colapsar una área para ver solo el título y el número de proyectos, y expandir al hacer clic.
- **Búsqueda:** Campo "Buscar en proyectos/áreas" que filtre por nombre (y luego por descripción si quieres).
- **Filtro por área en lista plana (opcional):** Si añades una vista "todos los proyectos", poder filtrar por área.

**Prioridad:** Media cuando el usuario tenga ya bastantes áreas/proyectos; orden de proyectos tiene más impacto rápido.

---

## 5. Engagement y hábito

**Problema:** No hay motivo explícito para volver cada día más allá de "ver mis proyectos".

**Propuestas:**

- **"¿En qué quieres trabajar hoy?":** En el dashboard, un bloque o botón que permita elegir un proyecto (o área) y llevarte a su detalle o a sus tareas. Reduce la parálisis de "tengo muchos proyectos".
- **Vista "proyecto activo" o "favoritos":** Marcar 1–3 proyectos como "activos" o "favoritos" y mostrarlos arriba o en una sección "Sigue con…".
- **Pequeña señal de actividad:** Por ejemplo "Última actualización: hace X" en proyecto o "Editado hoy". Sin ser invasivo, da sensación de vida.
- **(Futuro)** Recordatorios o revisión semanal por email: "Esta semana no has tocado Salud – ¿quieres planificar algo?". Requiere colas/emails.

**Prioridad:** Media; "trabajar hoy" y "favoritos/activos" son los de mayor impacto con menos esfuerzo.

---

## 6. Borrado y recuperación

**Problema:** Borrar proyecto (o área) es irreversible y con `confirm()` genérico. No hay archivo ni papelera.

**Propuestas:**

- **Confirmación más clara:** Modal con nombre del proyecto/área y texto del tipo "Se eliminarán también las X tareas. Esta acción no se puede deshacer."
- **Soft delete (archivo):** En lugar de borrar físicamente, marcar `deleted_at` y mover a "Archivo". Vista "Archivo" para restaurar o borrar definitivamente. Aumenta sensación de seguridad.
- Si no quieres soft delete aún, al menos **"Deshacer" breve (toast)** tras borrar: "Proyecto eliminado [Deshacer]" y deshacer con una llamada al backend en una ventana de unos segundos.

**Prioridad:** Media; muy valorado por usuarios que borran por error.

---

## 7. Móvil y accesibilidad

**Problema:** Hay diseño responsive pero no está claro si hay PWA, gestos o teclado/lectores de pantalla pensados.

**Propuestas:**

- **PWA básica:** `manifest.json`, service worker para caché de assets (y modo offline de solo lectura si quieres). "Añadir a la pantalla de inicio" mejora uso en móvil.
- **Accesibilidad:** Revisar contraste, foco en modales y flujos (Tab, Enter, Escape), `aria-labels` en iconos y botones, y que el emoji picker sea usable por teclado y lectores de pantalla.
- **Gestos en listas (opcional):** En móvil, deslizar para editar/borrar en áreas o proyectos (no bloqueante).

**Prioridad:** Media; PWA y a11y mejoran inclusión y uso en móvil.

---

## 8. Seguridad y robustez (producto técnico)

**Problema:** No se ven tests ni límites de uso ni refresh de sesión en el análisis rápido.

**Propuestas:**

- **Rate limiting:** Sobre todo en `POST /auth/login` y `POST /auth/register` (y futuro "olvidé contraseña") para evitar abuso y fuerza bruta.
- **Refresh token (opcional):** Si el access token es corto (ej. 15 min), usar refresh token para alargar sesión sin tener que hacer login cada semana. Si el token es largo (7 días), es menos urgente.
- **Tests:** E2E para flujos críticos: registro → login → crear área → crear proyecto → editar → cerrar sesión. Aunque sea un solo smoke test, da confianza en despliegues.
- **Manejo de errores en UI:** Mensajes claros cuando la API falla (red, 401, 500) y retry o "Reintentar" donde tenga sentido.

**Prioridad:** Alta para rate limiting y mensajes de error; media para tests y refresh token.

---

## Resumen de priorización sugerida

| Prioridad | Tema                    | Acción principal                                              |
|----------|--------------------------|----------------------------------------------------------------|
| **P0**   | Valor central            | Añadir tareas (o acciones) por proyecto; "siguiente acción" GTD; opcionalmente estado/progreso. |
| **P0**   | Activación               | Onboarding con áreas sugeridas y primer proyecto.             |
| **P0**   | Cuenta                   | Configuración real: cambiar contraseña, editar nombre; quitar "Próximamente". |
| **P1**   | Confianza                | Exportar datos; después "olvidé contraseña".                   |
| **P1**   | Escalabilidad UX         | Orden de proyectos persistido, colapsar áreas, búsqueda.      |
| **P1**   | Engagement               | "¿En qué trabajar hoy?" o proyectos destacados/activos.        |
| **P1**   | Seguridad                | Rate limiting en auth, mensajes de error claros.               |
| **P2**   | Borrado                  | Mejor confirmación + "Deshacer" o soft delete/archivo.         |
| **P2**   | Móvil / PWA / a11y       | PWA básica y revisión de accesibilidad.                       |
| **P2**   | Calidad                  | E2E de flujos críticos.                                       |

---

En resumen: LifeHub tiene buena base (auth, áreas, proyectos, UI clara). Como PO/manager priorizaría: **(1)** que el producto permita "hacer" algo con los proyectos (siguiente acción GTD, tareas, algo de progreso), **(2)** que el primer uso sea guiado y **(3)** que la cuenta y la confianza (contraseña, exportar datos) estén resueltas. A partir de ahí, orden, búsqueda, engagement y seguridad técnica cierran un roadmap muy sólido para un "centro de vida" personal.
