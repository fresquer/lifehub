from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Area, Project, ProjectNextAction
from app.schemas import (
    ProjectNextActionCreate,
    ProjectNextActionUpdate,
    ProjectNextActionResponse,
)
from app.routers.auth import get_current_user

router = APIRouter(tags=["project-next-actions"])


def _get_project_for_user(db: Session, project_id: int, user_id: int) -> Project:
    """Devuelve el proyecto si existe y su área pertenece al usuario; si no, 404."""
    project = (
        db.query(Project)
        .join(Area)
        .filter(Project.id == project_id, Area.user_id == user_id)
        .first()
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proyecto no encontrado",
        )
    return project


def _get_next_action_for_user(
    db: Session, next_action_id: int, user_id: int
) -> ProjectNextAction:
    """Devuelve la siguiente acción si existe y el proyecto es del usuario; si no, 404."""
    na = (
        db.query(ProjectNextAction)
        .join(Project)
        .join(Area)
        .filter(
            ProjectNextAction.id == next_action_id,
            Area.user_id == user_id,
        )
        .first()
    )
    if not na:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Siguiente acción no encontrada",
        )
    return na


@router.get(
    "/projects/{project_id}/next-actions",
    response_model=list[ProjectNextActionResponse],
)
def list_project_next_actions(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista las siguientes acciones de un proyecto."""
    _get_project_for_user(db, project_id, current_user.id)
    return (
        db.query(ProjectNextAction)
        .filter(ProjectNextAction.project_id == project_id)
        .order_by(ProjectNextAction.id)
        .all()
    )


@router.post(
    "/projects/{project_id}/next-actions",
    response_model=ProjectNextActionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project_next_action(
    project_id: int,
    data: ProjectNextActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Añade una siguiente acción a un proyecto."""
    project = _get_project_for_user(db, project_id, current_user.id)
    na = ProjectNextAction(
        project_id=project.id,
        title=data.title.strip(),
    )
    db.add(na)
    db.commit()
    db.refresh(na)
    return na


@router.patch(
    "/project-next-actions/{next_action_id}",
    response_model=ProjectNextActionResponse,
)
def update_project_next_action(
    next_action_id: int,
    data: ProjectNextActionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza una siguiente acción (título o hecho)."""
    na = _get_next_action_for_user(db, next_action_id, current_user.id)
    if data.title is not None:
        na.title = data.title.strip()
    if data.done is not None:
        na.done = data.done
    db.commit()
    db.refresh(na)
    return na


@router.delete(
    "/project-next-actions/{next_action_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project_next_action(
    next_action_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una siguiente acción."""
    na = _get_next_action_for_user(db, next_action_id, current_user.id)
    db.delete(na)
    db.commit()
    return None
