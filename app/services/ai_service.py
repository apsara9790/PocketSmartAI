import json
import re

from typing import Any

from app.config import settings

from app.services.catalog_service import (
    search_catalog
)

from app.services.prompts import (
    home_prompt,
    party_prompt,
    jewelry_prompt
)


def _money(value: Any) -> float:

    try:
        return round(
            float(value),
            2
        )

    except Exception:

        return 0.0


def _extract_json(
    text: str
) -> dict:

    text = text.strip()

    if text.startswith("```"):

        text = re.sub(
            r"^```(?:json)?",
            "",
            text
        ).strip()

        text = re.sub(
            r"```$",
            "",
            text
        ).strip()

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:

        raise ValueError(
            "No JSON object in AI response"
        )

    return json.loads(
        text[start:end + 1]
    )


def _normalize(
    raw: dict,
    planner: str,
    budget: float,
    fallback: list[dict],
    ai_powered: bool
) -> dict:

    recommendations = (
        raw.get("recommendations")
        if isinstance(raw, dict)
        else None
    )

    clean = []

    if isinstance(
        recommendations,
        list
    ):

        for item in recommendations:

            if not isinstance(
                item,
                dict
            ):
                continue

            price = _money(
                item.get(
                    "estimated_price",
                    item.get(
                        "price",
                        0
                    )
                )
            )

            try:

                quantity = int(
                    item.get(
                        "quantity",
                        1
                    ) or 1
                )

            except Exception:

                quantity = 1

            quantity = max(
                1,
                quantity
            )

            clean.append(
                {
                    "name":
                        str(
                            item.get(
                                "name",
                                "Recommended item"
                            )
                        ),

                    "category":
                        str(
                            item.get(
                                "category",
                                "General"
                            )
                        ),

                    "platform":
                        str(
                            item.get(
                                "platform",
                                "Local catalog"
                            )
                        ),

                    "estimated_price":
                        price,

                    "quantity":
                        quantity,

                    "reason":
                        str(
                            item.get(
                                "reason",
                                "Fits the requested budget and preferences."
                            )
                        ),

                    "link":
                        str(
                            item.get(
                                "link",
                                ""
                            )
                        )
                }
            )

    if not clean:

        clean = [

            {
                "name":
                    item["name"],

                "category":
                    item["category"],

                "platform":
                    item["platform"],

                "estimated_price":
                    _money(
                        item["price"]
                    ),

                "quantity":
                    1,

                "reason":
                    "Fallback catalog match selected for price and category.",

                "link":
                    item["link"]
            }

            for item in fallback[:8]
        ]

    total = round(
        sum(
            item["estimated_price"]
            * item["quantity"]
            for item in clean
        ),
        2
    )

    while (
        total > budget
        and len(clean) > 1
    ):

        clean.pop()

        total = round(
            sum(
                item["estimated_price"]
                * item["quantity"]
                for item in clean
            ),
            2
        )

    allocation = (
        raw.get("allocation", {})
        if isinstance(raw, dict)
        else {}
    )

    if not isinstance(
        allocation,
        dict
    ):
        allocation = {}

    return {

        "planner":
            planner,

        "title":
            str(
                raw.get(
                    "title",
                    f"{planner.title()} Budget Plan"
                )
            ),

        "budget":
            budget,

        "estimated_total":
            total,

        "budget_remaining":
            round(
                budget - total,
                2
            ),

        "summary":
            str(
                raw.get(
                    "summary",
                    "A budget-aware recommendation plan was created."
                )
            ),

        "allocation":
            {
                str(key):
                    _money(value)

                for key, value
                in allocation.items()
            },

        "recommendations":
            clean,

        "ai_powered":
            ai_powered,

        "disclaimer":
            (
                "Prices and availability are estimates "
                "from the configured catalog. Verify the "
                "final price on the linked platform before purchasing."
            )
    }


def _gemini_generate(
    prompt: str,
    image_bytes: bytes | None = None,
    mime_type: str | None = None
) -> dict:

    if not settings.gemini_api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is not configured"
        )

    from google import genai

    from google.genai import types

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    contents: list[Any] = [
        prompt
    ]

    if (
        image_bytes
        and mime_type
    ):

        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
        )

    response = client.models.generate_content(

        model=settings.gemini_model,

        contents=contents,

        config=types.GenerateContentConfig(

            temperature=0.3,

            response_mime_type="application/json"
        )
    )

    return _extract_json(
        response.text
    )


def generate_home(
    payload: dict
) -> dict:

    budget = float(
        payload["budget"]
    )

    categories = [
        item["category"]
        for item in payload["items"]
    ]

    fallback = search_catalog(
        "home",
        categories,
        budget * 0.45,
        [
            "Amazon",
            "IKEA"
        ]
    )

    try:

        raw = _gemini_generate(
            home_prompt(
                payload,
                fallback
            )
        )

        return _normalize(
            raw,
            "home",
            budget,
            fallback,
            True
        )

    except Exception:

        return _normalize(
            {},
            "home",
            budget,
            fallback,
            False
        )


def generate_party(
    payload: dict
) -> dict:

    budget = float(
        payload["budget"]
    )

    fallback = search_catalog(

        "party",

        [
            "catering",
            "decoration",
            "venue",
            "entertainment"
        ],

        budget * 0.50,

        [
            "Swiggy",
            "Zomato",
            "OYO"
        ]
    )

    try:

        raw = _gemini_generate(
            party_prompt(
                payload,
                fallback
            )
        )

        return _normalize(
            raw,
            "party",
            budget,
            fallback,
            True
        )

    except Exception:

        return _normalize(
            {},
            "party",
            budget,
            fallback,
            False
        )


def generate_jewelry(
    payload: dict,
    image_bytes: bytes | None = None,
    mime_type: str | None = None
) -> dict:

    budget = float(
        payload["budget"]
    )

    fallback = search_catalog(

        "jewelry",

        [
            payload.get(
                "style",
                ""
            ),

            payload.get(
                "occasion",
                ""
            )
        ],

        budget * 0.8,

        [
            "Amazon",
            "Flipkart"
        ]
    )

    try:

        raw = _gemini_generate(

            jewelry_prompt(
                payload,
                fallback,
                bool(image_bytes)
            ),

            image_bytes=image_bytes,

            mime_type=mime_type
        )

        return _normalize(
            raw,
            "jewelry",
            budget,
            fallback,
            True
        )

    except Exception:

        return _normalize(
            {},
            "jewelry",
            budget,
            fallback,
            False
        )