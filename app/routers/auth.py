from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.face import validate_face

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/test-face-scan")
async def test_face_scan(file: UploadFile = File(...)):
    """
    Upload an image to see if the AI can detect a face.
    """
    encoding = await validate_face(file)
    
    if encoding is None:
        raise HTTPException(status_code=400, detail="No face detected in the image")
    
    # Convert numpy array to list so it can be sent as JSON
    return {
        "message": "Face detected successfully!",
        "encoding_length": len(encoding), # Should be 128
        "encoding_sample": encoding.tolist()[:5] # Show first 5 numbers
    }