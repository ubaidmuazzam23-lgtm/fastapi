from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.config.database import init_database, close_database
from app.api.routes.auth import router as auth_router
from app.api.routes.debts import router as debt_router
from app.api.routes import plans
from app.api.routes import scenarios
from app.api.routes.documents import router as documents_router
from app.api.routes import credit
from app.api.routes import education
from app.api.routes.loans import router as loans_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes import saved_plans

app = FastAPI(
    title="Fintech Advisor API",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS Middleware - MUST be added before routes
# TEMPORARY: Allow all origins for debugging
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow ALL origins temporarily
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(debt_router, prefix="/api/v1")
app.include_router(plans.router, prefix="/api/v1")
app.include_router(scenarios.router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(credit.router, prefix="/api/v1")
app.include_router(education.router, prefix="/api/v1")
app.include_router(loans_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")
app.include_router(saved_plans.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Fintech Advisor API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting Fintech Advisor API...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🌐 CORS Origins: {settings.CORS_ORIGINS}")
    await init_database()
    print("✅ Database connected")

@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Shutting down Fintech Advisor API...")
    await close_database()
    print("✅ Database disconnected")