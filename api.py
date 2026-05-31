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

class DailyForecast(BaseModel):
    date: str
    day_weather: str
    night_weather: str
    temp_max: str
    temp_min: str
    wind_dir_day: str
    wind_scale_day: str

class WarningInfo(BaseModel):
    title: str
    type: str
    level: str
    text: str
    pub_time: str

class AirQuality(BaseModel):
    aqi: str
    level: str
    pm25: str
    pm10: str
    o3: str
    co: str
    no2: str
    so2: str

async def get_weather(city: str, api_key: str, api_host: str) -> Optional[WeatherData]:
    if not api_key or not api_host:
        return None
    async with httpx.AsyncClient(timeout=30) as client:
        city_id = await _get_city_id(client, city, api_key, api_host)
        if not city_id:
            return None
        try:
            resp = await client.get(f"https://{api_host}/v7/weather/now",
                params={"location": city_id, "key": api_key, "lang": "zh"})
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return None
        if data.get("code") != "200":
            return None
        now = data["now"]
        return WeatherData(
            city=city, date="今天", weather=now.get("text", "未知"),
            temperature=now.get("temp", "--"), humidity=now.get("humidity", "--"),
            wind_direction=now.get("windDir", "--"), wind_scale=now.get("windScale", "--"))

async def get_forecast(city: str, days: int, api_key: str, api_host: str) -> Optional[list[DailyForecast]]:
    if not api_key or not api_host:
        return None
    days = min(max(days, 1), 7)
    async with httpx.AsyncClient(timeout=30) as client:
        city_id = await _get_city_id(client, city, api_key, api_host)
        if not city_id:
            return None
        try:
            resp = await client.get(f"https://{api_host}/v7/weather/{days}d",
                params={"location": city_id, "key": api_key, "lang": "zh"})
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return None
        if data.get("code") != "200":
            return None
        result = []
        for day in data.get("daily", [])[:days]:
            result.append(DailyForecast(
                date=day.get("fxDate", ""), day_weather=day.get("textDay", "未知"),
                night_weather=day.get("textNight", "未知"), temp_max=day.get("tempMax", "--"),
                temp_min=day.get("tempMin", "--"), wind_dir_day=day.get("windDirDay", "--"),
                wind_scale_day=day.get("windScaleDay", "--")))
        return result

async def get_warnings(city: str, api_key: str, api_host: str) -> Optional[list[WarningInfo]]:
    if not api_key or not api_host:
        return None
    async with httpx.AsyncClient(timeout=30) as client:
        city_id = await _get_city_id(client, city, api_key, api_host)
        if not city_id:
            return None
        try:
            resp = await client.get(f"https://{api_host}/v7/warning/now",
                params={"location": city_id, "key": api_key, "lang": "zh"})
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return None
        if data.get("code") != "200":
            return None
        result = []
        for w in data.get("warning", []):
            result.append(WarningInfo(
                title=w.get("title", ""), type=w.get("typeName", ""),
                level=w.get("level", "").lower(), text=w.get("text", ""),
                pub_time=w.get("pubTime", "")))
        return result if result else None

async def get_air_quality(city: str, api_key: str, api_host: str) -> Optional[AirQuality]:
    if not api_key or not api_host:
        return None
    async with httpx.AsyncClient(timeout=30) as client:
        city_id = await _get_city_id(client, city, api_key, api_host)
        if not city_id:
            return None
        try:
            resp = await client.get(f"https://{api_host}/v7/air/now",
                params={"location": city_id, "key": api_key, "lang": "zh"})
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return None
        if data.get("code") != "200":
            return None
        now = data.get("now", {})
        return AirQuality(
            aqi=now.get("aqi", "--"), level=now.get("category", "未知"),
            pm25=now.get("pm2p5", "--"), pm10=now.get("pm10", "--"),
            o3=now.get("o3", "--"), co=now.get("co", "--"),
            no2=now.get("no2", "--"), so2=now.get("so2", "--"))

async def _get_city_id(client: httpx.AsyncClient, city: str, api_key: str, api_host: str) -> Optional[str]:
    try:
        resp = await client.get(f"https://{api_host}/geo/v2/city/lookup",
            params={"location": city, "key": api_key, "lang": "zh"})
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return None
    if data.get("code") != "200" or not data.get("location"):
        return None
    return data["location"][0]["id"]
