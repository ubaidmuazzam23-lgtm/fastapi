from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.config.database import init_database, close_database
from app.api.routes.auth import router as auth_router
from app.api.routes.debts import router as debt_router
# from app.api.routes.credit import router as credit_router  # Commented out temporarily
from app.api.routes import plans
from app.api.routes import scenarios
from app.api.routes.documents import router as documents_router
from app.api.routes import credit
from app.api.routes import education





app = FastAPI(title="Fintech Advisor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(debt_router, prefix="/api/v1")
# app.include_router(credit_router, prefix="/api/v1")  # Commented out temporarily
app.include_router(plans.router, prefix="/api/v1")
app.include_router(scenarios.router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(credit.router, prefix="/api/v1")
# Then add this line with your other routers:
app.include_router(education.router, prefix="/api/v1")




@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    await init_database()

@app.on_event("shutdown")
async def shutdown_event():
    await close_database()