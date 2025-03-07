from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import DataEntry
from app.schemas import DataCreate, DataResponse
from app.utils import decode_access_token, convert_to_csv
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter(prefix="/data", tags=["Data"])

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    username = payload.get("username")
    role = payload.get("role")
    return {"username": username, "role": role}

@router.post("/", response_model=DataResponse)
def create_data_entry(data: DataCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_data = DataEntry(content=data.content, format=data.format, user_id=data.user_id)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

@router.get("/")
def get_data_entries(
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user),
        response_format: Optional[str] = Query("json", description="Choose 'json' or 'csv'")
):
    entries = db.query(DataEntry).all()
    # Convert to dict for CSV if needed
    if response_format == "csv":
        # Turn DB objects into dict
        dict_list = [
            {
                "id": e.id,
                "content": e.content,
                "format": e.format,
                "user_id": e.user_id
            }
            for e in entries
        ]
        csv_data = convert_to_csv(dict_list)
        return {"csv": csv_data}
    else:
        # Return JSON by default
        return [DataResponse.from_orm(e) for e in entries]

@router.get("/{data_id}", response_model=DataResponse)
def get_data_entry(data_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    data = db.query(DataEntry).filter(DataEntry.id == data_id).first()
    if not data:
        raise HTTPException(status_code=404, detail="Data entry not found")
    return data

@router.put("/{data_id}", response_model=DataResponse)
def update_data_entry(data_id: int, updated: DataCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    entry = db.query(DataEntry).filter(DataEntry.id == data_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Data entry not found")
    entry.content = updated.content
    entry.format = updated.format
    entry.user_id = updated.user_id
    db.commit()
    db.refresh(entry)
    return entry

@router.delete("/{data_id}")
def delete_data_entry(data_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    entry = db.query(DataEntry).filter(DataEntry.id == data_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Data entry not found")
    db.delete(entry)
    db.commit()
    return {"detail": "Data entry deleted"}
