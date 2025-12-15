import face_recognition
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.models.user import User
from app.models.face import UserFace
from app.models.sighting import ClassSighting
from app.models.attendance import Attendance

router = APIRouter(prefix="/classroom", tags=["Classroom Surveillance"])

@router.post("/upload-group-photo")
async def process_class_photo(
    check_type: str = Form(...), # 'start', 'mid', or 'end'
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate input
    if check_type not in ['start', 'mid', 'end']:
        raise HTTPException(status_code=400, detail="check_type must be start, mid, or end")

    # 1. Load image & Find ALL faces
    image = face_recognition.load_image_file(file.file)
    
    # Upsample=2 helps find smaller faces in group photos
    face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=2)
    unknown_encodings = face_recognition.face_encodings(image, face_locations)

    if not unknown_encodings:
        return {"message": "No faces found in this photo.", "faces_found": 0}

    # 2. Get all Student Faces from DB
    known_faces_db = db.query(UserFace).all()
    if not known_faces_db:
         return {"message": "No registered students in database."}

    known_encodings = [np.array(f.encoding) for f in known_faces_db]
    known_user_ids = [f.user_id for f in known_faces_db]

    found_student_ids = set()

    # 3. Compare Every Face found vs Every Student
    for unknown_face in unknown_encodings:
        # Lower tolerance = Strict match. 0.6 is default.
        matches = face_recognition.compare_faces(known_encodings, unknown_face, tolerance=0.55)
        
        if True in matches:
            first_match_index = matches.index(True)
            student_id = known_user_ids[first_match_index]
            found_student_ids.add(student_id)

    # 4. Log Sightings (Avoid duplicates for same session)
    today = date.today()
    log_count = 0
    
    for sid in found_student_ids:
        exists = db.query(ClassSighting).filter_by(
            user_id=sid, date=today, session_type=check_type
        ).first()
        
        if not exists:
            db.add(ClassSighting(user_id=sid, date=today, session_type=check_type))
            log_count += 1
    
    db.commit()

    return {
        "message": f"Processed {check_type} photo.",
        "faces_detected": len(unknown_encodings),
        "students_identified": log_count,
        "ids_found": list(found_student_ids)
    }

@router.post("/finalize-day")
def finalize_daily_attendance(db: Session = Depends(get_db)):
    """
    Checks who was present in Start AND Mid AND End.
    """
    today = date.today()
    all_users = db.query(User).filter(User.is_active == True).all()
    results = []

    for user in all_users:
        # Find unique sightings for today
        sightings = db.query(ClassSighting).filter_by(user_id=user.id, date=today).all()
        sessions = {s.session_type for s in sightings} # Set: {'start', 'mid', 'end'}
        
        status = "Absent"
        if len(sessions) == 3:
            status = "Present"
            # Mark final attendance if not already marked
            exists = db.query(Attendance).filter_by(user_id=user.id).filter(Attendance.timestamp >= today).first()
            if not exists:
                db.add(Attendance(user_id=user.id))
        
        results.append({
            "student": user.full_name,
            "sessions": list(sessions),
            "status": status
        })

    db.commit()
    return {"date": today, "report": results}