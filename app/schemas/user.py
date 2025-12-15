from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# 1. Base Schema (Shared properties)
class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    is_active: Optional[bool] = True

# 2. Create Schema (What we receive from the API to create a user)
class UserCreate(UserBase):
    # We will accept a list of floats (face encoding) or handle it via file upload later
    # For now, let's keep it simple
    pass

# 3. Response Schema (What we send back to the client)
class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        # This tells Pydantic to read data even if it's not a dict, but an ORM model
        from_attributes = True