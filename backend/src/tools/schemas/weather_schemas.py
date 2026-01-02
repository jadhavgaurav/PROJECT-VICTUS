from pydantic import BaseModel, Field

class GetWeatherInfoSchema(BaseModel):
    location: str = Field(..., description="The city or location to get weather for.")
    num_days: int = Field(default=1, description="Number of days for the forecast (1-5). Default is 1 (current weather).")
