from fastapi import HTTPException, Request, status

from app.database import get_db
from app.services.security import decode_access_token


def _find_user(user_id: int):

    with get_db() as db:

        return db.execute(
            """
            SELECT
                id,
                name,
                email,
                password_hash,
                created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()


def get_current_user(request: Request):

    token = request.cookies.get("access_token")

    if not token:

        authorization = request.headers.get("Authorization", "")

        if authorization.startswith("Bearer "):
            token = authorization[7:]

    if not token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login required"
        )

    try:

        user_id = decode_access_token(token)

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = _find_user(user_id)

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user