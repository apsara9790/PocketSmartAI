import os

os.environ["DATABASE_URL"] = (
    "sqlite:///./test_pocketsmart.db"
)

os.environ["SECRET_KEY"] = (
    "test-secret"
)


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/api/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "ok"
    )


def test_register_login_and_home():

    email = (
        "test@example.com"
    )

    client.post(
        "/api/auth/register",

        json={
            "name": "Test User",
            "email": email,
            "password": "password123"
        }
    )


    response = client.post(

        "/api/auth/login",

        json={
            "email": email,
            "password": "password123"
        }
    )


    assert response.status_code == 200


    response = client.post(

        "/api/generate-home",

        json={

            "budget": 50000,

            "rooms": [
                "Living Room"
            ],

            "items": [

                {
                    "category":
                        "ceiling fan",

                    "quantity": 1
                }

            ],

            "style": "modern",

            "notes": ""
        }
    )


    assert response.status_code == 200


    data = response.json()


    assert (
        data["planner"]
        == "home"
    )


    assert (
        data["estimated_total"]
        <= data["budget"]
    )


def test_unauthorized_planner():

    unauthenticated_client =
        TestClient(app)


    response = (
        unauthenticated_client
        .post(
            "/api/generate-party",

            json={
                "budget": 10000,
                "guests": 10,
                "event_type": "Birthday"
            }
        )
    )


    assert (
        response.status_code
        == 401
    )