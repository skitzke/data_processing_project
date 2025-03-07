# app/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

# NEW IMPORT FOR OAUTH2 FORMS
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, Token
from app.utils import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a user using JSON body."""
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username is taken")

    hashed_pw = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_pw, role="user")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create token for the newly registered user
    token_data = {"username": new_user.username, "role": new_user.role}
    access_token = create_access_token(data=token_data, expires_delta=timedelta(minutes=60))
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(),  # CHANGED HERE
        db: Session = Depends(get_db),
):
    """
    Login endpoint using OAuth2 'password' flow form fields.
    Swagger automatically sends username & password as form data.
    """
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create token
    token_data = {"username": db_user.username, "role": db_user.role}
    access_token = create_access_token(data=token_data, expires_delta=timedelta(minutes=60))
    return {"access_token": access_token, "token_type": "bearer"}
