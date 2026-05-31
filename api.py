import httpx
from typing import Optional
from pydantic import BaseModel

class WeatherData(BaseModel):
    city: str
    date: str
    weather: str
    temperature: str
    humidity: str
    wind_direction: str
    wind_scale: str

async def get_weather(city: str, api_key: str) -> Optional[WeatherData]:
    """和风天气 API"""
    if not api_key:
        return None

    async with httpx.AsyncClient(timeout=30) as client:
        # 1. 查城市 ID
        geo_url = "https://geoapi.qweather.com/v2/city/lookup"
        geo_resp = await client.get(geo_url, params={
            "location": city,
            "key": api_key,
            "lang": "zh"
        })
        geo_data = geo_resp.json()
        if geo_data.get("code") != "200" or not geo_data.get("location"):
            return None

        city_id = geo_data["location"][0]["id"]

        # 2. 查实时天气
        weather_url = "https://devapi.qweather.com/v7/weather/now"
        w_resp = await client.get(weather_url, params={
            "location": city_id,
            "key": api_key,
            "lang": "zh"
        })
        w_data = w_resp.json()
        if w_data.get("code") != "200":
            return None

        now = w_data["now"]
        return WeatherData(
            city=city,
            date="今天",
            weather=now.get("text", "未知"),
            temperature=now.get("temp", "--"),
            humidity=now.get("humidity", "--"),
            wind_direction=now.get("windDir", "--"),
            wind_scale=now.get("windScale", "--")
        )
