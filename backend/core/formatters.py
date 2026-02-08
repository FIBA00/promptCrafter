import re


def clean_json_block(text: str) -> str:
    """
    Cleans a JSON string from markdown code blocks if present.
    Example:
    ```json
    {"key": "value"}
    ```
    becomes {"key": "value"}
    """
    # Remove ```json or ``` at the start
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    # Remove ``` at the end
    text = re.sub(r"\s*```$", "", text)
    return text.strip()
