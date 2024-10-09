import face_recognition
import numpy as np
import io
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from PIL import Image
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel

URL_BANCO = "sqlite:///./banco.db"
engine = create_engine(URL_BANCO, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    face_encoding = Column(LargeBinary)

Base.metadata.create_all(bind=engine)

class UserResponse(BaseModel):
    username: str
    message: str

    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

def numpy_to_binary(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return out.read()

def binary_to_numpy(binary):
    out = io.BytesIO(binary)
    out.seek(0)
    return np.load(out)

@app.post("/register/{username}", response_model=UserResponse)
async def register(username: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    image_array = np.array(image)
    
    face_locations = face_recognition.face_locations(image_array)
    if not face_locations:
        raise HTTPException(status_code=400, detail="No face detected in the image")
    
    face_encoding = face_recognition.face_encodings(image_array, face_locations)[0]
    
    db_user = User(
        username=username,
        face_encoding=numpy_to_binary(face_encoding)
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return UserResponse(username=username, message=f"User {username} registered successfully")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/authenticate", response_model=UserResponse)
async def authenticate(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    image_array = np.array(image)
    
    face_locations = face_recognition.face_locations(image_array)
    if not face_locations:
        raise HTTPException(status_code=400, detail="No face detected in the image")
    
    face_encoding = face_recognition.face_encodings(image_array, face_locations)[0]
    
    users = db.query(User).all()
    
    for user in users:
        stored_encoding = binary_to_numpy(user.face_encoding)
        matches = face_recognition.compare_faces([stored_encoding], face_encoding, tolerance=0.6)
        
        if matches[0]:
            return UserResponse(
                username=user.username,
                message="Authentication successful"
            )
    
    raise HTTPException(status_code=401, detail="Authentication failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)