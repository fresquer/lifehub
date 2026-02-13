# LifeHub – Referencia de API (para IA y desarrolladores)

Documentación de referencia del backend LifeHub. Usar este archivo para conocer endpoints, modelos y flujo de autenticación.

---

## Base URL

- **Con Docker:** `http://localhost:8000` (o vía frontend: `http://localhost/api` si Nginx hace proxy)
- **Desarrollo local backend:** `http://localhost:8000`

---

## Autenticación (JWT)

La API usa **JWT Bearer**. Tras hacer login, enviar el token en el header:

```
Authorization: Bearer <access_token>
```

- Contraseñas: hasheadas con **bcrypt** (passlib).
- Token: **HS256**, expira en 7 días. Clave por defecto en `SECRET_KEY` (cambiar en producción).

### Endpoints de auth

| Método | Ruta             | Auth        | Descripción                  |
| ------ | ---------------- | ----------- | ---------------------------- |
| POST   | `/auth/register` | No          | Registrar usuario            |
| POST   | `/auth/login`    | No          | Iniciar sesión, devuelve JWT |
| GET    | `/auth/me`       | Sí (Bearer) | Usuario actual               |

---

### POST `/auth/register`

Registra un nuevo usuario.

**Request (JSON):**

```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña_segura",
  "full_name": "Nombre Opcional"
}
```

- `email`: string, obligatorio. Se guarda en minúsculas; debe ser único.
- `password`: string, obligatorio. Se hashea con bcrypt.
- `full_name`: string, opcional.

**Response 200:** Usuario creado (sin contraseña).

```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "full_name": "Nombre Opcional",
  "created_at": "2025-02-10T12:00:00Z"
}
```

**Errores:** `400` si ya existe un usuario con ese email.

---

### POST `/auth/login`

Inicia sesión y devuelve un token JWT.

**Request (JSON):**

```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña_segura"
}
```

**Response 200:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errores:** `401` si email o contraseña incorrectos.

---

### GET `/auth/me`

Devuelve el usuario autenticado. Requiere header `Authorization: Bearer <access_token>`.

**Response 200:**

```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "full_name": "Nombre Opcional",
  "created_at": "2025-02-10T12:00:00Z"
}
```

**Errores:** `401` si no hay token, token inválido o expirado.

---

## Modelo de datos (User)

- **id:** int, PK.
- **email:** string, único, indexado.
- **password_hash:** string (bcrypt), no se expone en la API.
- **full_name:** string, nullable.
- **created_at:** datetime con timezone, servidor.

Tabla: `users`. Código: `backend/app/models.py`.

---

## Jerarquía: Áreas y Proyectos

- **Área (Area):** Área de vida del usuario (ej. Salud, Trabajo, Familia). Pertenece a un usuario (`user_id`).
- **Proyecto (Project):** Proyecto dentro de un área. Pertenece a un área (`area_id`). Jerarquía: **Area → Project**.

Tablas: `areas`, `projects`. Modelos en `backend/app/models.py`. Todos los endpoints de áreas y proyectos requieren **Bearer JWT** y solo devuelven/modifican datos del usuario autenticado.

### Áreas

| Método | Ruta          | Descripción                 |
| ------ | ------------- | --------------------------- |
| GET    | `/areas`      | Listar áreas del usuario    |
| POST   | `/areas`      | Crear área                  |
| GET    | `/areas/{id}` | Obtener área                |
| PATCH  | `/areas/{id}` | Actualizar área             |
| DELETE | `/areas/{id}` | Eliminar área (y proyectos) |

- **POST body:** `{ "name": "string", "description": "string | null", "color": "string | null" }` — `color` es opcional, hex `#rrggbb` (paleta del área).
- **PATCH body:** `{ "name": "string | null", "description": "string | null", "color": "string | null" }`
- **Respuesta área:** incluye `id`, `user_id`, `name`, `description`, `color`, `created_at`, `updated_at`.

### Proyectos

| Método | Ruta             | Descripción                                   |
| ------ | ---------------- | --------------------------------------------- |
| GET    | `/projects`      | Listar proyectos (query `?area_id=` opcional) |
| POST   | `/projects`      | Crear proyecto en un área                     |
| GET    | `/projects/{id}` | Obtener proyecto                              |
| PATCH  | `/projects/{id}` | Actualizar proyecto                           |
| DELETE | `/projects/{id}` | Eliminar proyecto                             |

- **POST body:** `{ "area_id": int, "name": "string", "description": "string | null", "icon": "string | null", "next_action": "string | null" }` — `icon` (emoji) y `next_action` (siguiente acción GTD) son opcionales.
- **PATCH body:** `{ "name": "string | null", "description": "string | null", "area_id": int | null, "icon": "string | null", "next_action": "string | null" }` — enviar `next_action` vacío o null para borrar la siguiente acción.
- **Respuesta proyecto:** incluye `id`, `area_id`, `icon`, `name`, `description`, `next_action`, `created_at`, `updated_at`.

Modelo **Project**: además de los campos anteriores, el campo `next_action` (string, opcional, máx. 500 caracteres) es la "siguiente acción" al estilo GTD. No hay endpoints nuevos; se gestiona con GET/POST/PATCH de proyectos.

### One-shot tasks (tareas sin proyecto)

Tareas que no pertenecen a ningún proyecto ("one shots"). Requieren **Bearer JWT** y solo devuelven/modifican datos del usuario autenticado.

| Método | Ruta                    | Descripción           |
| ------ | ----------------------- | --------------------- |
| GET    | `/one-shot-tasks`       | Listar one-shots      |
| POST   | `/one-shot-tasks`      | Crear one-shot        |
| GET    | `/one-shot-tasks/{id}` | Obtener one-shot      |
| PATCH  | `/one-shot-tasks/{id}` | Actualizar (title, done) |
| DELETE | `/one-shot-tasks/{id}` | Eliminar              |

- **POST body:** `{ "title": "string" }`
- **PATCH body:** `{ "title": "string | null", "done": "boolean | null" }`
- **Respuesta:** `id`, `user_id`, `title`, `done`, `created_at`, `updated_at`.

Tabla: `one_shot_tasks`. Modelo: `backend/app/models.py` (OneShotTask).

---

## Otros endpoints

- `GET /` – Mensaje de bienvenida.
- `GET /health` – Health check (`{"status": "healthy"}`).

---

## Ubicación del código (backend)

| Qué                                                           | Archivo                           |
| ------------------------------------------------------------- | --------------------------------- |
| App FastAPI, CORS, registro de routers                        | `backend/app/main.py`             |
| Conexión DB, sesión, `get_db`                                 | `backend/app/database.py`         |
| Modelo User                                                   | `backend/app/models.py`           |
| Schemas Pydantic (UserCreate, UserLogin, UserResponse, Token) | `backend/app/schemas.py`          |
| Hash de contraseña, JWT (crear/decodificar)                   | `backend/app/security.py`         |
| Rutas register, login, me y dependencia get_current_user      | `backend/app/routers/auth.py`     |
| CRUD de áreas (por usuario)                                   | `backend/app/routers/areas.py`    |
| CRUD de proyectos (por área/usuario)                          | `backend/app/routers/projects.py` |
| CRUD de one-shot tasks (tareas sin proyecto)                  | `backend/app/routers/one_shot_tasks.py` |

Base de datos: PostgreSQL. URL por defecto: `postgresql://lifehub:lifehub_secret@.../lifehub` (ver `docker-compose.yml` y `DATABASE_URL`).

---

## Resumen para IA

- **Registro:** `POST /auth/register` con `email`, `password`, `full_name` (opcional). Respuesta: usuario (id, email, full_name, created_at).
- **Login:** `POST /auth/login` con `email`, `password`. Respuesta: `access_token` y `token_type: "bearer"`.
- **Usuario actual:** `GET /auth/me` con header `Authorization: Bearer <access_token>`.
- Endpoints protegidos: usar la dependencia `get_current_user` (devuelve `User` o 401).
