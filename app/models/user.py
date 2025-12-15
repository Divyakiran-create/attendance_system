from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship # <--- Make sure this is imported
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to faces (One User -> Many Faces)
    faces = relationship("UserFace", back_populates="user")