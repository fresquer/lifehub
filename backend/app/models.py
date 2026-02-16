from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    areas = relationship("Area", back_populates="user", cascade="all, delete-orphan")
    one_shot_tasks = relationship("OneShotTask", back_populates="user", cascade="all, delete-orphan")


class Area(Base):
    """Área de vida (ej: Salud, Trabajo, Familia). Pertenece a un usuario."""

    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    color = Column(String(7), nullable=True)  # hex #rrggbb para la paleta del área
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="areas")
    projects = relationship("Project", back_populates="area", cascade="all, delete-orphan")
    one_shot_tasks = relationship("OneShotTask", back_populates="area")


class Project(Base):
    """Proyecto dentro de un área. Jerarquía: Area -> Project."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="CASCADE"), nullable=False, index=True)
    icon = Column(String(20), nullable=True)  # emoji para mostrar junto al título (estilo Notion)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    pinned = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    area = relationship("Area", back_populates="projects")
    next_actions = relationship(
        "ProjectNextAction",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectNextAction.id",
    )


class ProjectNextAction(Base):
    """Siguiente acción GTD de un proyecto. Un proyecto tiene varias."""

    __tablename__ = "project_next_actions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    done = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="next_actions")


class OneShotTask(Base):
    """Tarea sin proyecto (one-shot). Pertenece a un usuario. Opcionalmente ligada a un área (area_id null = One shot)."""

    __tablename__ = "one_shot_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    done = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="one_shot_tasks")
    area = relationship("Area", back_populates="one_shot_tasks")
