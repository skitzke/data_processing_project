from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from app.database import Base

class User(Base):
    __tablename__ = "users"

    # Enforce that 'role' must be either 'user' or 'admin'
    __table_args__ = (
        CheckConstraint("role IN ('user','admin')", name="check_user_role"),
    )

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")  # must be 'user' or 'admin'


class DataEntry(Base):
    __tablename__ = "data_entries"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    format = Column(String)  # e.g., JSON, XML, CSV
    user_id = Column(Integer, ForeignKey("users.id"))
