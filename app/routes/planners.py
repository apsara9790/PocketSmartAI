import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.schemas import HomeRequest, PartyRequest
from app.services.ai_service import (
    generate_home,
    generate_party,
    generate_jewelry
)


router = APIRouter(
    prefix="/api",
    tags=["Planners"]
)


def save_history(
    user_id: int,
    planner: str,
    request_data: dict,
    response_data: dict
):
    with get_db() as db:

        cursor = db.execute(
            """
            INSERT INTO recommendations
            (
                user_id,
                planner_type,
                request_json,
                response_json,
                saved
            )
            VALUES (?, ?, ?, ?, 0)
            """,
            (
                user_id,
                planner,
                json.dumps(request_data),
                json.dumps(response_data)
            )
        )

        return cursor.lastrowid


@router.post("/generate-home")
def generate_home_route(
    payload: HomeRequest,
    user=Depends(get_current_user)
):
    result = generate_home(payload.model_dump())

    recommendation_id = save_history(
        user["id"],
        "home",
        payload.model_dump(),
        result
    )

    return {
        **result,
        "recommendation_id": recommendation_id
    }


@router.post("/generate-party")
def generate_party_route(
    payload: PartyRequest,
    user=Depends(get_current_user)
):
    result = generate_party(payload.model_dump())

    recommendation_id = save_history(
        user["id"],
        "party",
        payload.model_dump(),
        result
    )

    return {
        **result,
        "recommendation_id": recommendation_id
    }


@router.post("/generate-jewelry")
async def generate_jewelry_route(
    budget: float = Form(...),
    occasion: str = Form(...),
    style: str = Form("modern"),
    notes: str = Form(""),
    outfit_image: UploadFile | None = File(None),
    user=Depends(get_current_user)
):
    if budget <= 0:
        raise HTTPException(
            status_code=422,
            detail="Budget must be greater than zero"
        )

    image_bytes = None
    mime_type = None

    if outfit_image and outfit_image.filename:

        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp"
        }

        if outfit_image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, PNG and WEBP images are supported"
            )

        image_bytes = await outfit_image.read()

        if len(image_bytes) > settings.max_upload_mb * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=f"Image must be <= {settings.max_upload_mb} MB"
            )

        mime_type = outfit_image.content_type

    payload = {
        "budget": budget,
        "occasion": occasion.strip(),
        "style": style.strip(),
        "notes": notes.strip()
    }

    result = generate_jewelry(
        payload,
        image_bytes,
        mime_type
    )

    recommendation_id = save_history(
        user["id"],
        "jewelry",
        payload,
        result
    )

    return {
        **result,
        "recommendation_id": recommendation_id
    }