from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db

from app.routes import (
    auth,
    history,
    pages,
    planners,
    saved_plans
)


# ==========================================
# CREATE FASTAPI APP
# ==========================================

app = FastAPI(
    title="PocketSmart AI",
    description="Smart Budget & Recommendation Assistant",
    version="1.0.0"
)


# ==========================================
# STATIC FILES
# ==========================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ==========================================
# DATABASE
# ==========================================

@app.on_event("startup")
def startup():

    init_db()


# ==========================================
# ROUTERS
# ==========================================

# Website pages
app.include_router(
    pages.router
)


# Authentication
app.include_router(
    auth.router
)


# Home / Party / Jewelry planners
app.include_router(
    planners.router
)


# History
app.include_router(
    history.router
)


# Saved Plans
app.include_router(
    saved_plans.router
)


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health_check():

    return {
        "status": "ok",
        "message": "PocketSmart AI is running"
    }


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )