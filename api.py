"""
Weather and warning API client for nonebot-plugin-weather.
Supports QWeather (primary), OpenWeatherMap (fallback), and 12379.cn (warning only).
"""

import httpx
from nonebot import logger
from typing import Optional, Dict, Any

# --- 配置注入（由 __init__.py 的 WeatherConfig 传入）---
API_KEYS = {
    "qweather": "",  # 和风天气 key
    "openweathermap": "",  # OpenWeather key
    "warning_12379": "",  # 国家预警中心 token
}

# --- 全局 HTTP 客户端（复用连接池，高性能）---
_http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(10.0, connect=5.0),
    limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
)

# --- 模型定义（轻量，不依赖 Pydantic，避免插件依赖冲突）---
class WeatherData:
    def __init__(
        self,
        city: str,
        temperature: str,
        feels_like: str,
        description: str,
        emoji: str,
        humidity: str,
        wind: str,
        updated_at: str,
    ):
        self.city = city
        self.temperature = temperature
        self.feels_like = feels_like
        self.description = description
        self.emoji = emoji
        self.humidity = humidity
        self.wind = wind
        self.updated_at = updated_at

class WarningInfo:
    def __init__(
        self,
        title: str,
        content: str,
        level: str,
        publish_time: str,
        region: str,
    ):
        self.title = title
        self.content = content
        self.level = level
        self.publish_time = publish_time
        self.region = region


# --- 核心函数：获取天气（QWeather 主 + OWM 备）---
async def get_weather(city: str, config) -> Optional[WeatherData]:
    """
    Get current weather for a city.
    Tries QWeather first, falls back to OpenWeatherMap on failure.
    """
    # Update keys from config
    API_KEYS["qweather"] = config.api_key
    API_KEYS["openweathermap"] = config.api_key
    API_KEYS["warning_12379"] = config.warning_api_key

    # Step 1: Try QWeather (recommended)
    if API_KEYS["qweather"]:
        try:
            logger.debug(f"[Weather API] QWeather: querying '{city}'")
            # First, get location ID
            loc_resp = await _http_client.get(
                "https://geoapi.qweather.com/v2/city/lookup",
                params={"key": API_KEYS["qweather"], "location": city},
            )
            loc_resp.raise_for_status()
            loc_data = loc_resp.json()
            if not loc_data.get("location"):
                raise ValueError("QWeather: city not found")
            location_id = loc_data["location"][0]["id"]
            city_name = loc_data["location"][0]["name"]

            # Then get weather
            weather_resp = await _http_client.get(
                "https://dev.qweather.com/v7/weather/now",
                params={"key": API_KEYS["qweather"], "location": location_id},
            )
            weather_resp.raise_for_status()
            w_data = weather_resp.json()

            if w_data.get("code") != "200":
                raise ValueError(f"QWeather error: {w_data.get('code')}")

            now = w_data["now"]
            return WeatherData(
                city=city_name,
                temperature=f"{now['temp']}°C",
                feels_like=f"{now['feelsLike']}°C",
                description=now["textNow"],
                emoji=_get_weather_emoji(now["icon"]),
                humidity=f"{now['humidity']}%",
                wind=f"{now['windDir']} {now['windScale']}级",
                updated_at=now["obsTime"][:16].replace("T", " "),
            )
        except Exception as e:
            logger.warning(f"[Weather API] QWeather failed for '{city}': {e}")

    # Step 2: Fallback to OpenWeatherMap
    if API_KEYS["openweathermap"]:
        try:
            logger.debug(f"[Weather API] OpenWeather: querying '{city}'")
            resp = await _http_client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "q": city,
                    "appid": API_KEYS["openweathermap"],
                    "lang": "zh_cn",
                    "units": "metric",
                },
            )
            resp.raise_for_status()
            data = resp.json()

            main = data["main"]
            weather = data["weather"][0]
            wind = data.get("wind", {})
            return WeatherData(
                city=data["name"],
                temperature=f"{int(main['temp'])}°C",
                feels_like=f"{int(main['feels_like'])}°C",
                description=weather["description"],
                emoji=_get_weather_emoji_from_openweather(weather["icon"]),
                humidity=f"{main['humidity']}%",
                wind=f"{wind.get('deg', '?')}° {wind.get('speed', '?')}m/s",
                updated_at=data["dt"],
            )
        except Exception as e:
            logger.warning(f"[Weather API] OpenWeather failed for '{city}': {e}")

    # All failed
    logger.error(f"[Weather API] All providers failed for '{city}'")
    return None


# --- 核心函数：获取预警（仅 12379.cn，权威唯一源）---
async def get_warning(province: str, city: str, config) -> Optional[WarningInfo]:
    """
    Get active warnings for province & city from 12379.cn.
    Returns the latest warning if any, or None.
    """
    if not API_KEYS["warning_12379"]:
        logger.warning("[Warning API] 12379 token not configured")
        return None

    try:
        logger.debug(f"[Warning API] 12379: querying {province}/{city}")
        resp = await _http_client.get(
            "https://www.12379.cn/api/warning",
            params={
                "province": province,
                "city": city,
                "token": API_KEYS["warning_12379"],
            },
        )
        resp.raise_for_status()
        data = resp.json()

        if not isinstance(data, list) or len(data) == 0:
            return None

        # Take the most recent warning (by publishTime)
        latest = max(data, key=lambda x: x.get("publishTime", "0"))
        return WarningInfo(
            title=latest.get("title", "未知预警"),
            content=latest.get("content", "暂无详情"),
            level=latest.get("level", "未知等级"),
            publish_time=latest.get("publishTime", "未知时间")[:16],
            region=latest.get("region", province),
        )
    except Exception as e:
        logger.error(f"[Warning API] 12379 failed for {province}/{city}: {e}")
        return None


# --- Emoji 映射表（QWeather icon code → emoji）---
def _get_weather_emoji(icon_code: str) -> str:
    mapping = {
        "dayclear": "☀️", "nightclear": "🌙",
        "daycloudy": "⛅", "nightcloudy": "☁️",
        "daycloudyyu": "🌥️", "nightcloudyyu": "☁️",
        "dayrain": "🌧️", "nightrain": "🌧️",
        "dayrainyu": "🌦️", "nightrainyu": "🌧️",
        "daysnow": "❄️", "nightsnow": "❄️",
        "daythunder": "⛈️", "nightthunder": "⛈️",
        "daywind": "💨", "nightwind": "💨",
        "dayhaze": "🌫️", "nighthaze": "🌫️",
        "dayfog": "🌫️", "nightfog": "🌫️",
        "daydust": "🌪️", "nightdust": "🌪️",
        "daycold": "🥶", "nightcold": "🥶",
        "dayhot": "🔥", "nighthot": "🔥",
    }
    return mapping.get(icon_code, "🌤️")

# --- OpenWeather icon code → emoji（简化映射）---
def _get_weather_emoji_from_openweather(icon_code: str) -> str:
    # OpenWeather icon codes: 01d, 02n, 09d, etc.
    if icon_code.startswith("01"):
        return "☀️" if "d" in icon_code else "🌙"
    elif icon_code.startswith("02"):
        return "⛅" if "d" in icon_code else "☁️"
    elif icon_code.startswith("03") or icon_code.startswith("04"):
        return "☁️"
    elif icon_code.startswith("09") or icon_code.startswith("10"):
        return "🌧️" if "d" in icon_code else "🌧️"
    elif icon_code.startswith("11"):
        return "⛈️"
    elif icon_code.startswith("13"):
        return "❄️"
    elif icon_code.startswith("50"):
        return "🌫️"
    else:
        return "🌤️"