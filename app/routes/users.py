import io
import matplotlib.pyplot as plt
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.utils import get_password_hash, decode_access_token, convert_to_csv
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter(prefix="/users", tags=["Users"])


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    username = payload.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    return current_user


@router.get("/", summary="Get all users in JSON (default) or CSV")
def get_all_users(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        response_format: Optional[str] = Query("json", description="Set to 'csv' for CSV output"),
):
    """
    Retrieve all users.
    - Default returns JSON
    - Use ?response_format=csv for CSV
    """
    users = db.query(User).all()

    if response_format.lower() == "csv":
        if not users:
            return PlainTextResponse("", media_type="text/csv")

        dict_list = []
        for u in users:
            dict_list.append({
                "id": u.id,
                "username": u.username,
                "role": u.role,
            })

        csv_data = convert_to_csv(dict_list)
        return PlainTextResponse(csv_data, media_type="text/csv")
    else:
        return [UserResponse.from_orm(u) for u in users]


@router.get("/roles-chart")
def get_roles_chart(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """
    Returns a bar chart (as PNG) showing how many users have 'admin' vs. 'user' roles.
    You must be authenticated to view this chart.
    """
    role_counts = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    if not role_counts:
        # If no data, return an image stating "No user data"
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No user data", ha="center", va="center")
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        return Response(content=buf.getvalue(), media_type="image/png")

    roles = [rc[0] for rc in role_counts]
    counts = [rc[1] for rc in role_counts]

    # Create the bar chart
    fig, ax = plt.subplots()
    ax.bar(roles, counts)
    ax.set_xlabel("Role")
    ax.set_ylabel("Number of Users")
    ax.set_title("User Roles Distribution")

    # Save to an in-memory buffer
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return Response(content=buf.getvalue(), media_type="image/png")


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
        user_id: int,
        info: UserCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = info.username
    user.hashed_password = get_password_hash(info.password)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(admin_required)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}
