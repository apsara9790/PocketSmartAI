from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response
)

from app.database import get_db
from app.dependencies import get_current_user

from app.models.schemas import (
    RegisterRequest,
    LoginRequest
)

from app.services.security import (
    hash_password,
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(payload: RegisterRequest):

    with get_db() as db:

        existing = db.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (payload.email,)
        ).fetchone()

        if existing:

            raise HTTPException(
                status_code=409,
                detail="Email already registered"
            )

        cursor = db.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password_hash
            )
            VALUES (?, ?, ?)
            """,
            (
                payload.name.strip(),
                payload.email,
                hash_password(payload.password)
            )
        )

        return {
            "message": "Registration successful",
            "user_id": cursor.lastrowid
        }


@router.post("/login")
def login(
    payload: LoginRequest,
    response: Response
):

    email = payload.email.strip().lower()

    with get_db() as db:

        user = db.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

    if (
        not user
        or not verify_password(
            payload.password,
            user["password_hash"]
        )
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(
        user["id"]
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 120
    )

    return {
        "message": "Login successful",

        "access_token": token,

        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }


@router.post("/token")
def token(payload: LoginRequest):

    email = payload.email.strip().lower()

    with get_db() as db:

        user = db.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

    if (
        not user
        or not verify_password(
            payload.password,
            user["password_hash"]
        )
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    return {
        "access_token": create_access_token(
            user["id"]
        ),
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(response: Response):

    response.delete_cookie(
        "access_token"
    )

    return {
        "message": "Logged out"
    }


@router.get("/session-info")
def session_info(
    user=Depends(get_current_user)
):

    return {
        "logged_in": True,
        "user_id": user["id"],
        "name": user["name"],
        "email": user["email"]
    }


@router.get("/session-data")
def session_data(
    user=Depends(get_current_user)
):

    with get_db() as db:

        count = db.execute(
            """
            SELECT COUNT(*) AS count
            FROM recommendations
            WHERE user_id = ?
            """,
            (user["id"],)
        ).fetchone()["count"]

    return {
        "user_id": user["id"],
        "recommendation_count": count
    }