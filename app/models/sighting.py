from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint
from app.core.database import Base

class ClassSighting(Base):
    """
    Stores raw sightings: "I saw Student X at the Start of class on 2025-12-16"
    """
    __tablename__ = "class_sightings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, index=True) # e.g., 2025-12-16
    
    # Can be 'start', 'mid', 'end'
    session_type = Column(String) 

    # Ensure a student can't be scanned twice for "start" on the same day
    __table_args__ = (
        UniqueConstraint('user_id', 'date', 'session_type', name='unique_sighting'),
    )