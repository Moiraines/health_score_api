from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Health Score API",
    description="API for managing user health scores and fitness activities",
    version="1.0.0",
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers for different API modules
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.health_score import router as health_score_router
from app.api.v1.activities import router as activities_router

# Include API routers with version prefix
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(health_score_router, prefix="/api")
app.include_router(activities_router, prefix="/api")

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Health Score API is running!"}
