import face_recognition
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.services.face import validate_face
from app.models.user import User
from app.models.attendance import Attendance

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)

@router.post("/punch")
async def mark_attendance(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. Get the face encoding from the uploaded photo
    unknown_encoding = await validate_face(file)
    if unknown_encoding is None:
        raise HTTPException(status_code=400, detail="No face detected. Please try again.")

    # 2. Fetch all users from DB (In a large system, we'd use a Vector DB, but this works for <1000 users)
    users = db.query(User).all()
    
    known_encodings = []
    user_map = {} # Map index to user object

    # Prepare data for comparison
    for index, user in enumerate(users):
        if user.face_encoding:
            # Convert list back to numpy array
            known_encodings.append(np.array(user.face_encoding))
            user_map[index] = user

    if not known_encodings:
        raise HTTPException(status_code=404, detail="No registered users found in database.")

    # 3. Compare faces (The Magic Part)
    # compare_faces returns a list of True/False [False, True, False...]
    matches = face_recognition.compare_faces(known_encodings, unknown_encoding, tolerance=0.5)
    
    if True in matches:
        # Find the index of the first match
        first_match_index = matches.index(True)
        matched_user = user_map[first_match_index]
        
        # 4. Log the attendance
        new_entry = Attendance(user_id=matched_user.id)
        db.add(new_entry)
        db.commit()
        
        return {
            "message": f"Welcome, {matched_user.full_name}!",
            "status": "Marked Present",
            "time": datetime.now()
        }
    else:
        raise HTTPException(status_code=401, detail="Face not recognized. Access Denied.")