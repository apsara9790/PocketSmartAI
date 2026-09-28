import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.database import get_db
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/api",
    tags=["History"]
)


@router.get("/history")
def history(
    user=Depends(get_current_user)
):

    with get_db() as db:

        rows = db.execute(
            """
            SELECT
                id,
                planner_type,
                request_json,
                response_json,
                created_at

            FROM recommendations

            WHERE user_id = ?

            ORDER BY id DESC
            """,
            (user["id"],)
        ).fetchall()

    return [

        {
            "id": row["id"],

            "planner_type":
                row["planner_type"],

            "request":
                json.loads(
                    row["request_json"]
                ),

            "response":
                json.loads(
                    row["response_json"]
                ),

            "created_at":
                row["created_at"]
        }

        for row in rows
    ]


@router.get(
    "/history/{recommendation_id}"
)
def history_detail(
    recommendation_id: int,
    user=Depends(get_current_user)
):

    with get_db() as db:

        row = db.execute(
            """
            SELECT
                id,
                planner_type,
                request_json,
                response_json,
                created_at

            FROM recommendations

            WHERE id = ?
            AND user_id = ?
            """,
            (
                recommendation_id,
                user["id"]
            )
        ).fetchone()

    if not row:

        raise HTTPException(
            status_code=404,
            detail="Recommendation not found"
        )

    return {

        "id": row["id"],

        "planner_type":
            row["planner_type"],

        "request":
            json.loads(
                row["request_json"]
            ),

        "response":
            json.loads(
                row["response_json"]
            ),

        "created_at":
            row["created_at"]
    }


@router.delete(
    "/history/{recommendation_id}"
)
def delete_history(
    recommendation_id: int,
    user=Depends(get_current_user)
):

    with get_db() as db:

        cursor = db.execute(
            """
            DELETE FROM recommendations

            WHERE id = ?
            AND user_id = ?
            """,
            (
                recommendation_id,
                user["id"]
            )
        )

        if cursor.rowcount == 0:

            raise HTTPException(
                status_code=404,
                detail="Recommendation not found"
            )

    return {
        "message": "Deleted"
    }