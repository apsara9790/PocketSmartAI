import json

from pathlib import Path
from urllib.parse import quote_plus


CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "catalog.json"
)


def load_catalog() -> list[dict]:

    with CATALOG_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def search_catalog(
    planner: str,
    categories: list[str],
    max_price: float,
    preferred_platforms: list[str] | None = None,
    limit: int = 12
) -> list[dict]:

    catalog = load_catalog()

    category_words = {
        value.lower()
        for value in categories
        if value
    }

    preferred = {
        value.lower()
        for value in (
            preferred_platforms or []
        )
    }

    matches = []

    for item in catalog:

        if item["planner"] != planner:
            continue

        if float(item["price"]) > max_price:
            continue

        text = (
            f'{item["name"]} '
            f'{item["category"]} '
            f'{item.get("tags", "")}'
        ).lower()

        category_match = (
            any(
                word in text
                for word in category_words
            )
            if category_words
            else True
        )

        platform_bonus = (
            1
            if item["platform"].lower()
            in preferred
            else 0
        )

        if category_match or not category_words:

            candidate = dict(item)

            candidate["_score"] = (
                platform_bonus
            )

            candidate["link"] = (
                item.get("link")
                or
                (
                    "https://www.google.com/search?q="
                    +
                    quote_plus(
                        item["name"]
                        + " "
                        + item["platform"]
                    )
                )
            )

            matches.append(candidate)

    matches.sort(
        key=lambda item: (
            -item["_score"],
            float(item["price"])
        )
    )

    return matches[:limit]