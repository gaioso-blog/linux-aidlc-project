"""User domain model."""
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """Represents a user in the system (sourced from Cognito)."""

    user_id: str = Field(..., description="Cognito sub (UUID)")
    email: str = Field(..., description="User email address")
    name: str = Field(..., description="User display name")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    model_config = {"use_enum_values": True}

    @classmethod
    def from_cognito_attributes(cls, sub: str, attributes: list[dict]) -> "User":
        """Build a User from Cognito UserAttributes list."""
        attr_map: dict[str, str] = {a["Name"]: a["Value"] for a in attributes}
        return cls(
            user_id=sub,
            email=attr_map.get("email", ""),
            name=attr_map.get("name", attr_map.get("email", sub)),
            created_at=attr_map.get("created_at", datetime.now(timezone.utc).isoformat()),
        )
