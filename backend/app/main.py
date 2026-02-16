from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, SessionLocal
from app.models import Base, User
from app.routers import auth, areas, projects, one_shot_tasks, project_next_actions
from app.security import get_password_hash


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crear tablas y usuario test al arrancar la aplicación."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        test_user = db.query(User).filter(User.email == "test@lifehub.local").first()
        if not test_user:
            db.add(
                User(
                    email="test@lifehub.local",
                    password_hash=get_password_hash("test123"),
                    full_name="Usuario Test",
                )
            )
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(
    title="LifeHub API",
    description="API del proyecto LifeHub",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(areas.router)
app.include_router(projects.router)
app.include_router(one_shot_tasks.router)
app.include_router(project_next_actions.router)


@app.get("/")
async def root():
    """Endpoint raíz de ejemplo."""
    return {"message": "Bienvenido a LifeHub API", "status": "ok"}


@app.get("/health")
async def health():
    """Health check para Docker y orquestación."""
    return {"status": "healthy"}
