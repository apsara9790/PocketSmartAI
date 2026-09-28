from typing import Literal

from pydantic import BaseModel, Field, field_validator


PlannerType = Literal[
    "home",
    "party",
    "jewelry"
]


class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=80
    )

    email: str = Field(
        min_length=5,
        max_length=160
    )

    password: str = Field(
        min_length=6,
        max_length=128
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:

        return value.strip().lower()


class LoginRequest(BaseModel):

    email: str

    password: str


class HomeItem(BaseModel):

    category: str = Field(
        min_length=2,
        max_length=60
    )

    quantity: int = Field(
        default=1,
        ge=1,
        le=50
    )


class HomeRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000
    )

    rooms: list[str] = Field(
        min_length=1,
        max_length=10
    )

    items: list[HomeItem] = Field(
        min_length=1,
        max_length=30
    )

    style: str = Field(
        default="modern",
        max_length=80
    )

    notes: str = Field(
        default="",
        max_length=500
    )


class PartyRequest(BaseModel):

    budget: float = Field(
        gt=0,
        le=10_000_000
    )

    guests: int = Field(
        gt=0,
        le=10_000
    )

    event_type: str = Field(
        min_length=2,
        max_length=80
    )

    venue: str = Field(
        default="Not decided",
        max_length=150
    )

    city: str = Field(
        default="Chennai",
        max_length=100
    )

    preferences: str = Field(
        default="",
        max_length=500
    )


class RecommendationItem(BaseModel):

    name: str

    category: str

    platform: str

    estimated_price: float = Field(
        ge=0
    )

    quantity: int = Field(
        default=1,
        ge=1
    )

    reason: str

    link: str = ""


class RecommendationResponse(BaseModel):

    planner: PlannerType

    title: str

    budget: float

    estimated_total: float

    budget_remaining: float

    summary: str

    allocation: dict[str, float]

    recommendations: list[
        RecommendationItem
    ]

    ai_powered: bool

    disclaimer: str