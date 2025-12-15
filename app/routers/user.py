from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User as UserModel
from app.models.face import UserFace 
from app.schemas.user import UserResponse
from app.services.face import validate_face

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    full_name: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Check if email exists
    db_user = db.query(UserModel).filter(UserModel.email == email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Detect Face
    face_encoding = await validate_face(file)
    if face_encoding is None:
        raise HTTPException(status_code=400, detail="No face detected.")
    
    # 3. Create User (Without face data initially)
    new_user = UserModel(full_name=full_name, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 4. Save Face to the NEW table
    new_face = UserFace(user_id=new_user.id, encoding=face_encoding.tolist())
    db.add(new_face)
    db.commit()
    
    return new_user

@router.get("/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users