from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserFace(Base):
    __tablename__ = "user_faces"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    encoding = Column(ARRAY(FLOAT)) # The 128 numbers representing the face
    
    user = relationship("User", back_populates="faces")