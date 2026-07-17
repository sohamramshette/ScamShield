import json
import os
import sys

# Add backend to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.openapi.utils import get_openapi

from main import app


def generate_openapi():
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

    os.makedirs("../docs", exist_ok=True)
    with open("../docs/openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print("Generated OpenAPI schema at docs/openapi.json")
    print(
        "You can import this file directly into Postman to create a Postman Collection."
    )


if __name__ == "__main__":
    generate_openapi()
