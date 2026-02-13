from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, OneShotTask
from app.schemas import OneShotTaskCreate, OneShotTaskUpdate, OneShotTaskResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/one-shot-tasks", tags=["one-shot-tasks"])


@router.get("", response_model=list[OneShotTaskResponse])
def list_one_shot_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista las tareas one-shot del usuario (sin proyecto)."""
    return (
        db.query(OneShotTask)
        .filter(OneShotTask.user_id == current_user.id)
        .order_by(OneShotTask.done.asc(), OneShotTask.created_at.desc())
        .all()
    )


@router.post("", response_model=OneShotTaskResponse, status_code=status.HTTP_201_CREATED)
def create_one_shot_task(
    data: OneShotTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea una tarea one-shot (sin proyecto)."""
    task = OneShotTask(
        user_id=current_user.id,
        title=data.title.strip(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=OneShotTaskResponse)
def get_one_shot_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene una tarea one-shot por id."""
    task = (
        db.query(OneShotTask)
        .filter(OneShotTask.id == task_id, OneShotTask.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    return task


@router.patch("/{task_id}", response_model=OneShotTaskResponse)
def update_one_shot_task(
    task_id: int,
    data: OneShotTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza una tarea one-shot."""
    task = (
        db.query(OneShotTask)
        .filter(OneShotTask.id == task_id, OneShotTask.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    if data.title is not None:
        task.title = data.title.strip()
    if data.done is not None:
        task.done = data.done
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_one_shot_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una tarea one-shot."""
    task = (
        db.query(OneShotTask)
        .filter(OneShotTask.id == task_id, OneShotTask.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    db.delete(task)
    db.commit()
    return None
