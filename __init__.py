from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import CommandArg
from nonebot.adapters import Message

from zhenxun.configs.config import Config

from . import api

weather_cmd = on_command("天气", priority=5, block=True)

WEATHER_EMOJI = {
    "晴": "☀️",
    "多云": "⛅",
    "阴": "☁️",
    "小雨": "🌦️",
    "中雨": "🌧️",
    "大雨": "⛈️",
    "暴雨": "⛈️",
    "雷阵雨": "⛈️",
    "雪": "🌨️",
    "小雪": "🌨️",
    "中雪": "❄️",
    "大雪": "❄️",
    "雾": "🌫️",
    "霾": "😷",
    "沙": "💨",
    "尘": "💨",
    "风": "🍃",
}

def get_weather_emoji(weather_text: str) -> str:
    for key, emoji in WEATHER_EMOJI.items():
        if key in weather_text:
            return emoji
    return "🌡️"

@weather_cmd.handle()
async def handle_weather(event: MessageEvent, args: Message = CommandArg()):
    city = args.extract_plain_text().strip()

    # 从 Zhenxun 配置系统读取
    base_config = Config.get("nonebot_plugin_weather")
    default_city = base_config.get("DEFAULT_CITY") if base_config else "北京"
    api_key = base_config.get("API_KEY") if base_config else ""

    if not city:
        city = default_city or "北京"

    weather_data = await api.get_weather(city, api_key)

    if weather_data is None:
        await weather_cmd.finish(
            f"❌ 获取「{city}」天气失败\n"
            f"可能原因：城市名不对 / API Key 未填 / 网络问题\n"
            f"请在 data/config.yaml 里填写 nonebot_plugin_weather.API_KEY"
        )
        return

    emoji = get_weather_emoji(weather_data.weather)

    msg = (
        f"{emoji} {weather_data.city} 实时天气\n"
        f"━━━━━━━━━━━━\n"
        f"🌡️ 气温：{weather_data.temperature}°C\n"
        f"☁️ 天气：{weather_data.weather}\n"
        f"💧 湿度：{weather_data.humidity}%\n"
        f"🍃 风向：{weather_data.wind_direction}\n"
        f"💨 风力：{weather_data.wind_scale}级\n"
        f"━━━━━━━━━━━━\n"
        f"数据来源：和风天气"
    )

    await weather_cmd.finish(msg)
