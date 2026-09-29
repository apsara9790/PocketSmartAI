import json


def home_prompt(
    payload: dict,
    catalog: list[dict]
) -> str:

    return f"""
You are PocketSmart AI,
a budget planning assistant.

Create a practical home-interior
recommendation plan.

USER INPUT:

{json.dumps(
    payload,
    indent=2
)}

LOCAL CATALOG:

{json.dumps(
    catalog,
    indent=2
)}

Rules:

1. Never exceed the user's total budget.

2. Prefer products from the supplied catalog.

3. Do not invent unrealistic prices.

4. Balance functionality, style and price.

5. Return valid JSON only.

JSON structure:

{{
  "title": "...",
  "summary": "...",
  "allocation": {{
    "category": 1000
  }},
  "recommendations": [
    {{
      "name": "...",
      "category": "...",
      "platform": "...",
      "estimated_price": 1000,
      "quantity": 1,
      "reason": "...",
      "link": "..."
    }}
  ]
}}
"""


def party_prompt(
    payload: dict,
    catalog: list[dict]
) -> str:

    return f"""
You are PocketSmart AI,
a party budget planning assistant.

Create a practical and event-specific
party planning recommendation.

The selected event type is very important.
All recommendations must match the
selected event type.

USER INPUT:

{json.dumps(
    payload,
    indent=2
)}

LOCAL CATALOG:

{json.dumps(
    catalog,
    indent=2
)}

EVENT-SPECIFIC RULES:

1. If the event type is "Birthday",
   recommend birthday-appropriate
   food, decoration, venue and
   entertainment.

2. If the event type is "Wedding",
   recommend wedding-appropriate
   food, decoration, venue and
   entertainment.
   Do not give birthday-party
   recommendations.

3. If the event type is "Corporate",
   recommend corporate-event
   appropriate food, venue,
   decoration and entertainment.

4. If the event type is "Family function",
   recommend family-function
   appropriate food, venue,
   decoration and entertainment.

5. Never mix recommendations from
   another event type.

6. Keep the plan within the total budget.

7. Account for the guest count.

8. Cover food/catering, venue,
   decoration and entertainment
   where possible.

9. Prefer the supplied catalog.

10. Do not invent unrealistic prices.

11. Use the user's venue, city and
    preferences when provided.

12. Return valid JSON only.

JSON structure:

{{
  "title": "...",
  "summary": "...",
  "allocation": {{
    "food": 1000,
    "venue": 1000,
    "decoration": 1000,
    "entertainment": 1000
  }},
  "recommendations": [
    {{
      "name": "...",
      "category": "...",
      "platform": "...",
      "estimated_price": 1000,
      "quantity": 1,
      "reason": "...",
      "link": "..."
    }}
  ]
}}
"""


def jewelry_prompt(
    payload: dict,
    catalog: list[dict],
    has_image: bool
) -> str:

    image_status = (
        "available"
        if has_image
        else "not available"
    )

    return f"""
You are PocketSmart AI,
a jewelry recommendation assistant.

Analyze the user's occasion,
style and budget.

An outfit image is
{image_status}.

USER INPUT:

{json.dumps(
    payload,
    indent=2
)}

LOCAL CATALOG:

{json.dumps(
    catalog,
    indent=2
)}

Rules:

1. Stay within the budget.

2. Recommend jewelry suitable
   for the occasion.

3. Match the requested style.

4. If an image is available,
   use it only for broad
   color/style coordination.

5. Do not identify the person
   in the image.

6. Return valid JSON only.

JSON keys:

title,
summary,
allocation,
recommendations
"""