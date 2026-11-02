import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.api.routes import router
from backend.auth.routes import router as auth_router
from backend.api.designs_routes import router as designs_router
from backend.db.database import engine, Base
import backend.db.models  # Ensures models are registered before create_all
app = FastAPI(title="AI Text-to-3D House API")

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local beta development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount renders directory
os.makedirs("renders", exist_ok=True)
app.mount("/renders", StaticFiles(directory="renders"), name="renders")

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(designs_router, prefix="/api/designs", tags=["designs"])
app.include_router(router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"status": "ok"}
