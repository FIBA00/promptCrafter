from fastapi import status


def test_create_prompt_guest_minimal(client):
    """
    Test sending a prompt with ONLY the required 'task' field.
    This simulates a guest user just typing "Help me..."
    """
    payload = {"task": "Help me write a Python script"}

    response = client.post("/api/v1/process_prompt/", json=payload)

    # 1. Check HTTP Status
    assert response.status_code == status.HTTP_200_OK

    # 2. Check Response Structure
    data = response.json()
    assert "structured_prompt" in data
    assert "natural_prompt" in data

    # Check that our input was actually used in the response
    assert payload["task"] in data["structured_prompt"]
    # Check for template markers instead of exact string match
    assert "[1. ROLE or CONTEXTUAL SETTING]" in data["structured_prompt"]


def test_create_prompt_guest_full_fields(client):
    """
    Test sending a prompt with ALL optional fields filled.
    """
    payload = {
        "task": "Build a rocket",
        "title": "Mars Mission",
        "role": "Rocket Scientist",
        "constraints": "No fuel allowed",
        "output": "Blueprint",
        "personality": "Elon Musk like",
    }

    response = client.post("/api/v1/process_prompt/", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["natural_prompt"] is not None


def test_create_prompt_validation_error(client):
    """
    Test sending a prompt WITHOUT the required 'task' field.
    Should return 422 Unprocessable Entity.
    """
    payload = {"title": "Missing Task"}

    response = client.post("/api/v1/process_prompt/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = response.json()["detail"]
    # Pydantic tells us exactly what is missing
    assert detail[0]["loc"] == ["body", "task"]
    assert detail[0]["msg"] == "Field required"


def test_create_prompt_invalid_types(client):
    """
    Test sending a Number where a String is expected.
    """
    payload = {
        "task": "Valid task",
        "title": 123456,  # Should be a string
    }

    response = client.post("/api/v1/process_prompt/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
