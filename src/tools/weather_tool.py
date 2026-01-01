"""
Weather information tool using OpenWeatherMap API
"""

import httpx
from datetime import datetime
from langchain_core.tools import tool

from ..config import settings
from .config import async_client

@tool
async def get_weather_info(location: str, num_days: int = 1) -> str:
    """
    Provides the current weather or a multi-day forecast for a specific location.
    - If 'num_days' is 1, it returns the current weather conditions.
    - If 'num_days' is greater than 1, it returns a forecast for that many days.
    - The maximum forecast period is 5 days.
    Keywords: weather, forecast, temperature, rain, wind, climate.
    """
    api_key = settings.OPENWEATHER_API_KEY
    if not api_key:
        return "Error: OpenWeatherMap API key is not set. Please add it to your .env file."

    base_url = "http://api.openweathermap.org/data/2.5"
    num_days = min(num_days, 5)

    try:
        if num_days <= 1:
            # Get Current Weather
            url = f"{base_url}/weather?q={location}&appid={api_key}&units=metric"
            response = await async_client.get(url)
            response.raise_for_status()
            data = response.json()
            
            city = data['name']
            condition = data['weather'][0]['description']
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            
            return (f"Current weather in {city}:\n"
                    f"- Condition: {condition.title()}\n"
                    f"- Temperature: {temp}°C (Feels like {feels_like}°C)\n"
                    f"- Humidity: {humidity}%\n"
                    f"- Wind Speed: {wind_speed} m/s")
        else:
            # Get 5-Day / 3-Hour Forecast and process it for daily summary
            url = f"{base_url}/forecast?q={location}&appid={api_key}&units=metric"
            response = await async_client.get(url)
            response.raise_for_status()
            data = response.json()
            
            city = data['city']['name']
            forecast_summary = [f"{num_days}-day forecast for {city}:"]
            
            daily_forecasts = {}
            for item in data['list']:
                # Parse date from timestamp (dt)
                date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                if date not in daily_forecasts:
                    daily_forecasts[date] = {'temps': [], 'conditions': set()}
                
                daily_forecasts[date]['temps'].append(item['main']['temp'])
                daily_forecasts[date]['conditions'].add(item['weather'][0]['description'])

            # Create a readable summary for the requested number of days
            day_count = 0
            for date, daily_data in daily_forecasts.items():
                if day_count >= num_days:
                    break
                
                day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A, %b %d')
                min_temp = min(daily_data['temps'])
                max_temp = max(daily_data['temps'])
                conditions = ", ".join(c.title() for c in daily_data['conditions'])
                
                forecast_summary.append(
                    f"\n- {day_name}:\n"
                    f"  - Temperature: {min_temp:.1f}°C to {max_temp:.1f}°C\n"
                    f"  - Conditions: {conditions}"
                )
                day_count += 1
                
            return "\n".join(forecast_summary)

    except httpx.HTTPStatusError as http_err:
        if http_err.response.status_code == 404:
            return f"Error: Could not find weather data for '{location}'. Please check the spelling."
        return f"HTTP error occurred: {http_err}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

