from pydantic import BaseModel, Field, model_validator
from typing import Optional

class WeatherData(BaseModel):
    """
    Internal structured model for data returned by the MCP Weather Server.
    Handles multiple possible field names from different MCP implementations.
    """
    location: str = Field(..., description="Location name or city")
    temperature: float = Field(..., description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Relative humidity percentage")
    condition: Optional[str] = Field(None, description="Weather description (e.g., 'light snow')")

    @model_validator(mode='before')
    def normalize_fields(cls, values):
        # Normalize alternative MCP field names
        if "city" in values and "location" not in values:
            values["location"] = values.pop("city")
        if "temperature_celsius" in values and "temperature" not in values:
            values["temperature"] = values.pop("temperature_celsius")
        if "humidity_percent" in values and "humidity" not in values:
            values["humidity"] = values.pop("humidity_percent")
        if "description" in values and "condition" not in values:
            values["condition"] = values.pop("description")
        return values

    class Config:
        json_schema_extra = {
            "example": {
                "location": "Helsinki",
                "temperature": -2.5,
                "humidity": 85,
                "condition": "light snow"
            }
        }