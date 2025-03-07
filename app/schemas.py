from pydantic import BaseModel

# --------------- USERS --------------- #
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: str

    class Config:
        # For Pydantic v2:
        from_attributes = True

# --------------- DATA --------------- #
class DataBase(BaseModel):
    content: str
    format: str
    user_id: int

class DataCreate(DataBase):
    pass

class DataResponse(DataBase):
    id: int

    class Config:
        # For Pydantic v2:
        from_attributes = True

# -------------- AUTH --------------- #
class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str
