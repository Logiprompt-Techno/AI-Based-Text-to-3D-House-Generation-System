from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.db.database import get_db
from backend.db.models import Design, User
from backend.auth.security import get_current_user
from .designs_schemas import DesignCreate, DesignUpdate, DesignResponse

router = APIRouter()

@router.post("", response_model=DesignResponse, status_code=status.HTTP_201_CREATED)
def create_design(
    design_in: DesignCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    new_design = Design(
        user_id=current_user.id,
        name=design_in.name,
        prompt=design_in.prompt,
        requirements_json=design_in.requirements_json,
        layout_json=design_in.layout_json,
        floorplan_json=design_in.floorplan_json,
        house3d_json=design_in.house3d_json
    )
    db.add(new_design)
    db.commit()
    db.refresh(new_design)
    return new_design

@router.get("", response_model=List[DesignResponse])
def get_designs(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    designs = db.query(Design).filter(Design.user_id == current_user.id).order_by(Design.created_at.desc()).all()
    return designs

@router.get("/{design_id}", response_model=DesignResponse)
def get_design(
    design_id: str,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    design = db.query(Design).filter(Design.id == design_id, Design.user_id == current_user.id).first()
    if not design:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Design not found")
    return design

@router.put("/{design_id}", response_model=DesignResponse)
def update_design(
    design_id: str,
    design_in: DesignUpdate,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    design = db.query(Design).filter(Design.id == design_id, Design.user_id == current_user.id).first()
    if not design:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Design not found")
        
    update_data = design_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(design, key, value)
        
    db.commit()
    db.refresh(design)
    return design

@router.delete("/{design_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_design(
    design_id: str,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    design = db.query(Design).filter(Design.id == design_id, Design.user_id == current_user.id).first()
    if not design:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Design not found")
        
    db.delete(design)
    db.commit()
    return None
