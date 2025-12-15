import face_recognition
import numpy as np
from fastapi import UploadFile, HTTPException

async def validate_face(file: UploadFile):
    """
    Reads an uploaded image and returns the 128-dimension face encoding.
    """
    try:
        # 1. Read the file into a numpy array (face_recognition needs this format)
        image = face_recognition.load_image_file(file.file)
        
        # 2. Detect faces
        # 'hog' is faster (CPU), 'cnn' is more accurate (GPU required usually)
        face_locations = face_recognition.face_locations(image, model="hog")
        
        if len(face_locations) == 0:
            return None # No face found
            
        if len(face_locations) > 1:
            # For an attendance system, we usually want strictly one face
            raise HTTPException(status_code=400, detail="Multiple faces detected. Please pose one person at a time.")

        # 3. Get the encoding (the "fingerprint" of the face)
        # We take the first face found
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        # Return the 128 float values
        return face_encodings[0]

    except Exception as e:
        print(f"Error processing face: {e}")
        return None