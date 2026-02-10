# LifeHub – Monorepo

Monorepo con backend FastAPI, frontend Vue y PostgreSQL, orquestado con Docker Compose.

## Estructura

- **backend/** – API en FastAPI (Python)
- **frontend/** – SPA en Vue 3 + Vite, servida en producción por Nginx
- **docker-compose.yml** – Postgres, backend y frontend (Nginx)

## Home server / despliegue completo (todo en Docker)

Para montar todo en el home server o en cualquier máquina sin tocar código en local:

```bash
docker compose up --build -d
```

- **Frontend:** puerto 3000 – Nginx sirve Vue y hace proxy de `/api` al backend
- **Backend:** puerto 8000 – FastAPI
- **PostgreSQL:** puerto 5432 – usuario `lifehub`, contraseña `lifehub_secret`, base de datos `lifehub`

La base de datos persiste en el volumen `postgres_data`. En producción, define `SECRET_KEY` en el entorno (o en un `.env`).

## Subir a tu servidor personal

### 1. Requisitos en el servidor

- **Docker** y **Docker Compose** instalados.
- Puertos **3000** (frontend) y, si quieres acceder directo al backend, **8000** (opcional).

### 2. Llevar el código al servidor

**Opción A – Con Git (recomendado)**  
Si el proyecto está en GitHub/GitLab:

```bash
# En el servidor (Linux)
git clone https://github.com/TU_USUARIO/LifeHub.git
cd LifeHub
```

**Opción B – Copiar la carpeta**  
Desde tu PC con SCP, rsync o el método que uses:

```bash
# Desde tu PC (PowerShell), ejemplo con SCP
scp -r C:\Users\ferna\_dev\LifeHub usuario@TU_SERVIDOR_IP:/home/usuario/
```

Asegúrate de copiar la raíz del proyecto (con `docker-compose.yml`, `backend/`, `frontend/`). No hace falta subir `node_modules`, `.venv` ni `frontend/dist` si vas a usar solo Docker.

### 3. Configurar producción (recomendado)

En la raíz del proyecto en el servidor crea un `.env`:

```bash
# En el servidor, dentro de LifeHub
nano .env
```

Contenido mínimo:

```env
SECRET_KEY=una-clave-secreta-muy-larga-y-aleatoria-para-produccion
```

Opcional: si quieres cambiar la contraseña de la base de datos, define también las variables que use el backend y ajusta `docker-compose.yml` para usarlas (o edita ahí `POSTGRES_PASSWORD` y `DATABASE_URL`).

### 4. Levantar la app

En el servidor, en la carpeta del proyecto:

```bash
docker compose up --build -d
```

- **Frontend (la app):** `http://TU_IP_SERVIDOR:3000`
- **Backend API:** `http://TU_IP_SERVIDOR:8000` (solo si expones el puerto; el frontend ya usa `/api` vía Nginx).

### 5. (Opcional) Dominio y HTTPS

Para usar un dominio (ej. `lifehub.midominio.com`) y HTTPS:

1. Instala un **reverse proxy** en el servidor (Nginx o Caddy).
2. Apunta el dominio al servidor (DNS A record).
3. Configura el proxy para que:
   - escuche en el puerto 80/443,
   - haga proxy hacia `http://127.0.0.1:3000` (contenedor frontend),
   - y opcionalmente gestione el certificado SSL (Let's Encrypt con Caddy es automático).

Con eso accederías a la app por `https://lifehub.midominio.com` sin abrir el puerto 3000 al exterior.

### Resumen rápido

| Paso | Acción                                             |
| ---- | -------------------------------------------------- |
| 1    | En el servidor: `git clone` o copiar el proyecto   |
| 2    | Crear `.env` con `SECRET_KEY` (y opcionalmente DB) |
| 3    | `docker compose up --build -d`                     |
| 4    | Abrir en el navegador: `http://IP_SERVIDOR:3000`   |

## Desarrollo con recarga automática (recomendado)

Así no tienes que hacer `docker compose up --build` cada vez: solo la DB corre en Docker y backend/frontend en local; cualquier cambio en código se refleja al instante.

**Todo de una vez (PowerShell):**

```powershell
.\dev.ps1
```

Levanta la DB en Docker y abre dos ventanas (backend y frontend). App en http://localhost:5173

**O paso a paso:**

**1. Levanta solo la base de datos**

```bash
docker compose -f docker-compose.dev.yml up -d
```

**2. Backend (recarga solo al guardar)**

```bash
cd backend
.venv\Scripts\activate   # o: python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
.\run_dev.bat             # Windows PowerShell (usa ./run_dev.sh en Linux/Mac)
```

O manualmente con la URL de la DB en localhost:

```bash
set DATABASE_URL=postgresql://lifehub:lifehub_secret@localhost:5432/lifehub
uvicorn app.main:app --reload --host 0.0.0.0
```

**3. Frontend (Vite recarga al instante)**

```bash
cd frontend
npm run dev
```

- **App:** http://localhost:5173 (Vite hace proxy de `/api` a http://localhost:8000)
- **Backend:** http://localhost:8000

Cualquier cambio en backend reinicia uvicorn; cualquier cambio en frontend recarga el navegador. No hace falta volver a levantar Docker.

## Documentación de referencia

- **`docs/API-REFERENCIA.md`** – Referencia completa de la API (auth, modelos, endpoints y ubicación del código). Útil para IA y desarrolladores.

## Endpoints de ejemplo

- `GET /` – Mensaje de bienvenida
- `GET /health` – Health check
- **Auth:** `POST /auth/register`, `POST /auth/login`, `GET /auth/me` (ver `docs/API-REFERENCIA.md`)
