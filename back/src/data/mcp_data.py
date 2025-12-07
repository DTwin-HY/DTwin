from pydantic import BaseModel, Field, model_validator


class WeatherData(BaseModel):
    """
    Internal structured model for data returned by the MCP Weather Server.
    Handles multiple possible field names from different MCP implementations.
    """

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    location: str = Field(..., description="Location name or city")
    sunny: bool = Field(..., description="Whether the day is considered sunny")

    @model_validator(mode="before")
    def normalize_fields(cls, values):
        if "city" in values and "location" not in values:
            values["location"] = values.pop("city")
        if "sunny" in values and isinstance(values["sunny"], str):
            values["sunny"] = values["sunny"].lower() in ("true", "1", "yes")
        return values

    class Config:
        json_schema_extra = {
            "example": {"date": "2025-11-25", "location": "Helsinki", "sunny": False}
        }
