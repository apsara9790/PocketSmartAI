import json

from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/api",
    tags=["Saved Plans"]
)


@router.post("/save-plan")
def save_plan(
    payload: dict,
    user=Depends(get_current_user)
):
    recommendation_id = payload.get("recommendation_id")

    if not recommendation_id:
        raise HTTPException(
            status_code=400,
            detail="Recommendation ID is required"
        )

    with get_db() as db:

        # Check whether this recommendation belongs to this user
        row = db.execute(
            """
            SELECT id
            FROM recommendations
            WHERE id = ? AND user_id = ?
            """,
            (recommendation_id, user["id"])
        ).fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Recommendation not found"
            )

        # Mark the recommendation as saved
        db.execute(
            """
            UPDATE recommendations
            SET saved = 1
            WHERE id = ? AND user_id = ?
            """,
            (recommendation_id, user["id"])
        )

    return {
        "message": "Plan saved successfully!",
        "id": recommendation_id
    }


@router.get("/saved-plans")
def get_saved_plans(
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
            AND saved = 1
            ORDER BY id DESC
            """,
            (user["id"],)
        ).fetchall()

    return [
        {
            "id": row["id"],
            "planner_type": row["planner_type"],
            "request": json.loads(row["request_json"]),
            "response": json.loads(row["response_json"]),
            "created_at": row["created_at"]
        }
        for row in rows
    ]


@router.delete("/saved-plans/{recommendation_id}")
def delete_saved_plan(
    recommendation_id: int,
    user=Depends(get_current_user)
):
    with get_db() as db:

        cursor = db.execute(
            """
            UPDATE recommendations
            SET saved = 0
            WHERE id = ? AND user_id = ?
            """,
            (recommendation_id, user["id"])
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Saved plan not found"
            )

    return {
        "message": "Saved plan removed successfully"
    }