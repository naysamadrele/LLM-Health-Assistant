from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import Symptom
from backend.app.schemas.schemas import SymptomResponse
from backend.app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[SymptomResponse])
def get_symptoms(
    search: Optional[str] = Query(None, description="Search term for symptom code or name"),
    category: Optional[str] = Query(None, description="Filter symptoms by category"),
    red_flags_only: Optional[bool] = Query(False, description="Retrieve only critical red flags"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Retrieve clinical symptoms from database with search, category filtering, and red flag options.
    """
    query = db.query(Symptom)
    
    if red_flags_only:
        query = query.filter(Symptom.is_red_flag == True)
        
    if category:
        query = query.filter(Symptom.category.ilike(category))
        
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Symptom.name.ilike(search_filter)) | 
            (Symptom.code.ilike(search_filter)) |
            (Symptom.category.ilike(search_filter))
        )
        
    return query.order_by(Symptom.category, Symptom.name).all()
