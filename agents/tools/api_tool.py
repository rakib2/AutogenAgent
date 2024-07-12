import requests
from pydantic import BaseModel, Field
from typing import Annotated

class APIInput(BaseModel):
    endpoint: Annotated[str, Field(description="The API endpoint to call.")]
    method: Annotated[str, Field(description="HTTP method (GET, POST, etc.).")]
    headers: dict = Field(default_factory=dict)
    body: dict = Field(default_factory=dict)

def api_call(input: Annotated[APIInput, "Input for making API call."]) -> dict:
    response = requests.request(
        method=input.method,
        url=input.endpoint,
        headers=input.headers,
        json=input.body
    )
    return response.json()
