from fastapi import FastAPI
from app.routers import user, auth, classroom 

app = FastAPI(title="Classroom Surveillance System")

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(classroom.router) 

@app.get("/")
def read_root():
    return {"message": "System Active", "mode": "Surveillance"}