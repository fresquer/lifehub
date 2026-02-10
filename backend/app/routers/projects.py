from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Area, Project
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


def _ensure_area_belongs_to_user(db: Session, area_id: int, user_id: int) -> Area:
    """Devuelve el área si existe y pertenece al usuario; si no, lanza 404."""
    area = db.query(Area).filter(Area.id == area_id, Area.user_id == user_id).first()
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área no encontrada",
        )
    return area


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    area_id: int | None = Query(None, description="Filtrar por área"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista proyectos del usuario. Opcionalmente filtrados por área."""
    q = db.query(Project).join(Area).filter(Area.user_id == current_user.id)
    if area_id is not None:
        q = q.filter(Project.area_id == area_id)
    return q.order_by(Project.name).all()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea un proyecto dentro de un área (el área debe ser del usuario)."""
    _ensure_area_belongs_to_user(db, data.area_id, current_user.id)
    project = Project(
        area_id=data.area_id,
        icon=data.icon,
        name=data.name,
        description=data.description,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene un proyecto por id (solo si su área pertenece al usuario)."""
    project = (
        db.query(Project)
        .join(Area)
        .filter(Project.id == project_id, Area.user_id == current_user.id)
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado",
        )
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza un proyecto (solo si su área pertenece al usuario)."""
    project = (
        db.query(Project)
        .join(Area)
        .filter(Project.id == project_id, Area.user_id == current_user.id)
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado",
        )
    if data.name is not None:
        project.name = data.name
    if data.icon is not None:
        project.icon = data.icon
    if data.description is not None:
        project.description = data.description
    if data.area_id is not None:
        _ensure_area_belongs_to_user(db, data.area_id, current_user.id)
        project.area_id = data.area_id
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un proyecto (solo si su área pertenece al usuario)."""
    project = (
        db.query(Project)
        .join(Area)
        .filter(Project.id == project_id, Area.user_id == current_user.id)
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado",
        )
    db.delete(project)
    db.commit()
    return None
