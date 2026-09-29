from fastapi import (
    APIRouter,
    Request,
    Depends
)

from fastapi.responses import HTMLResponse

from app.dependencies import get_current_user


router = APIRouter(
    tags=["Pages"]
)


# =========================================
# TEMPLATE CONFIGURATION
# =========================================

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(
    directory="templates"
)


# =========================================
# HOME
# =========================================

@router.get(
    "/",
    response_class=HTMLResponse
)
def index(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


# =========================================
# LOGIN
# =========================================

@router.get(
    "/login",
    response_class=HTMLResponse
)
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request
        }
    )


# =========================================
# REGISTER
# =========================================

@router.get(
    "/register",
    response_class=HTMLResponse
)
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "request": request
        }
    )


# =========================================
# DASHBOARD
# LOGIN REQUIRED
# =========================================

@router.get(
    "/dashboard",
    response_class=HTMLResponse
)
def dashboard(
    request: Request,
    user=Depends(get_current_user)
):

    response = templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "user": user
        }
    )

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# =========================================
# HOME PLANNER
# LOGIN REQUIRED
# =========================================

@router.get(
    "/home-planner",
    response_class=HTMLResponse
)
def home_planner(
    request: Request,
    user=Depends(get_current_user)
):

    response = templates.TemplateResponse(
        request=request,
        name="home_planner.html",
        context={
            "request": request,
            "user": user
        }
    )

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# =========================================
# PARTY PLANNER
# LOGIN REQUIRED
# =========================================

@router.get(
    "/party-planner",
    response_class=HTMLResponse
)
def party_planner(
    request: Request,
    user=Depends(get_current_user)
):

    response = templates.TemplateResponse(
        request=request,
        name="party_planner.html",
        context={
            "request": request,
            "user": user
        }
    )

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# =========================================
# JEWELRY PLANNER
# LOGIN REQUIRED
# =========================================

@router.get(
    "/jewelry-planner",
    response_class=HTMLResponse
)
def jewelry_planner(
    request: Request,
    user=Depends(get_current_user)
):

    response = templates.TemplateResponse(
        request=request,
        name="jewelry_planner.html",
        context={
            "request": request,
            "user": user
        }
    )

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# =========================================
# HISTORY
# LOGIN REQUIRED
# =========================================

@router.get(
    "/history",
    response_class=HTMLResponse
)
def history_page(
    request: Request,
    user=Depends(get_current_user)
):

    response = templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "request": request,
            "user": user
        }
    )

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# =========================================
# SAVED PLANS
# LOGIN REQUIRED
# =========================================

@router.get(
    "/saved-plans",
    response_class=HTMLResponse
)
def saved_plans_page(
    request: Request,
    user=Depends(get_current_user)
):

    response = templates.TemplateResponse(
        request=request,
        name="saved_plans.html",
        context={
            "request": request,
            "user": user
        }
    )

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response