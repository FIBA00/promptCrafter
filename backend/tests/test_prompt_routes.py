from fastapi import status
from unittest.mock import patch, MagicMock
from core.config import settings

# Prefix for the API
PREFIX = f"/api/{settings.VERSION or 'v1.1'}/pcrafter/"


def test_create_prompt_verified_user_uses_ai(client, test_user_token):
    """
    Test that a verified user triggers the AI flow (mocked).
    """
    payload = {
        "task": "Explain quantum computing",
        "title": "Quantum",
        "role": "Physicist",
        "output": "Simple text",
    }
    headers = {"Authorization": f"Bearer {test_user_token}"}

    # We mock OllamaClient inside the service module
    with patch("services.st_prompt_service.OllamaClient") as MockOllama:
        mock_instance = MockOllama.return_value
        mock_instance.generate_chat_completion.return_value = {
            "choices": [{"message": {"content": "AI Generated Prompt Content"}}]
        }

        response = client.post(PREFIX, json=payload, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify AI content was returned
        assert data["structured_prompt"] == "AI Generated Prompt Content"
        # Verify mock was called
        MockOllama.assert_called_once()
        mock_instance.generate_chat_completion.assert_called_once()


def test_create_prompt_unverified_user_normal_flow(client, unverified_user_token):
    """
    Test that an unverified user gets the template-based prompt, not AI.
    """
    payload = {
        "task": "Explain cooking",
        "title": "Cooking",
        "role": "Chef",
        "output": "Recipe",
    }
    headers = {"Authorization": f"Bearer {unverified_user_token}"}

    with patch("services.st_prompt_service.OllamaClient") as MockOllama:
        response = client.post(PREFIX, json=payload, headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # The structured prompt should contain standard template text, not AI output
        assert "[1. ROLE or CONTEXTUAL SETTING]" in data["structured_prompt"]

        # Ensure AI client was NOT called
        MockOllama.assert_not_called()


def test_rate_limit_exceeded(client, test_user_token):
    """
    Test that verified users are rate limited after 10 requests.
    """
    payload = {"task": "Spam request"}
    headers = {"Authorization": f"Bearer {test_user_token}"}

    # Mock AI to avoid overhead/errors
    with patch("services.st_prompt_service.OllamaClient") as MockOllama:
        mock_instance = MockOllama.return_value
        mock_instance.generate_chat_completion.return_value = {
            "choices": [{"message": {"content": "AI Content"}}]
        }

        # The default limit is 10. We consume 10 tokens.
        for i in range(10):
            response = client.post(PREFIX, json=payload, headers=headers)
            assert response.status_code == status.HTTP_200_OK

        # The 11th request should fail
        response = client.post(PREFIX, json=payload, headers=headers)
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert response.json()["detail"]["error_code"] == "rate_limit_exceeded"
