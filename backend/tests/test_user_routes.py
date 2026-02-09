from fastapi import status
from unittest.mock import patch
from core.config import settings

PREFIX = f"/api/{settings.VERSION or 'v1.1'}/user"


def test_signup_successful(client):
    """
    Test user registration sends verification email.
    """
    payload = {"email": "newuser@example.com", "password": "securepassword123"}

    with patch("routers.user.send_email.delay") as mock_send_email:
        response = client.post(f"{PREFIX}/signup", json=payload)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user"]["email"] == payload["email"]
        assert mock_send_email.called


def test_login_successful(client, test_user):
    """
    Test login with correct credentials returns token.
    """
    # test_user fixture creates user with password "testpassword"
    payload = {
        "username": test_user.email,  # OAuth2PasswordRequestForm uses 'username' field for email usually
        "password": "testpassword",
    }

    response = client.post(f"{PREFIX}/login", data=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user):
    payload = {"username": test_user.email, "password": "wrongpassword"}
    response = client.post(f"{PREFIX}/login", data=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_verify_email(client, unverified_user):
    """
    Test verifying an email with a valid token.
    """
    # We need to generate a valid token manually
    from core.oauth2 import create_url_safe_token

    token = create_url_safe_token(
        {"user_id": unverified_user.user_id, "email": unverified_user.email}
    )

    response = client.get(f"{PREFIX}/verify_email", params={"token": token})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Account verified successfully."

    # Verify DB update
    # Refetch user? Or rely on response if it returned user status (it returns message)
