from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Area
from app.schemas import AreaCreate, AreaUpdate, AreaResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/areas", tags=["areas"])


@router.get("", response_model=list[AreaResponse])
def list_areas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todas las áreas del usuario."""
    return db.query(Area).filter(Area.user_id == current_user.id).order_by(Area.name).all()


@router.post("", response_model=AreaResponse, status_code=status.HTTP_201_CREATED)
def create_area(
    data: AreaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea una nueva área para el usuario."""
    area = Area(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
    )
    db.add(area)
    db.commit()
    db.refresh(area)
    return area


@router.get("/{area_id}", response_model=AreaResponse)
def get_area(
    area_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene un área por id (solo si pertenece al usuario)."""
    area = db.query(Area).filter(Area.id == area_id, Area.user_id == current_user.id).first()
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área no encontrada",
        )
    return area


@router.patch("/{area_id}", response_model=AreaResponse)
def update_area(
    area_id: int,
    data: AreaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza un área (solo si pertenece al usuario)."""
    area = db.query(Area).filter(Area.id == area_id, Area.user_id == current_user.id).first()
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área no encontrada",
        )
    if data.name is not None:
        area.name = data.name
    if data.description is not None:
        area.description = data.description
    db.commit()
    db.refresh(area)
    return area


@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_area(
    area_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un área y sus proyectos (solo si pertenece al usuario)."""
    area = db.query(Area).filter(Area.id == area_id, Area.user_id == current_user.id).first()
    if not area:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Área no encontrada",
        )
    db.delete(area)
    db.commit()
    return None
