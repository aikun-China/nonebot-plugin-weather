from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.params import CommandArg
from nonebot.adapters import Message

from . import api
from .config import weather_config

weather_cmd = on_command("天气", priority=5, block=True)

# 天气 -> emoji 映射表
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
    """根据天气文字匹配 emoji"""
    for key, emoji in WEATHER_EMOJI.items():
        if key in weather_text:
            return emoji
    return "🌡️"  # 默认

@weather_cmd.handle()
async def handle_weather(event: MessageEvent, args: Message = CommandArg()):
    city = args.extract_plain_text().strip()
    
    if not city:
        city = weather_config.default_city or "北京"
    
    # 真实调用 API
    data = await api.get_weather(city, weather_config)
    
    if data is None:
        await weather_cmd.finish(
            f"❌ 获取「{city}」天气失败\n"
            f"可能原因：城市名不对 / API Key 没填 / 网络问题\n"
            f"请在 config.yaml 里填写 weather.api_key"
        )
        return
    
    emoji = get_weather_emoji(data.weather)
    
    # 纯文字 + emoji 表情包风格
    msg = (
        f"{emoji} {data.city} 实时天气\n"
        f"━━━━━━━━━━━━\n"
        f"🌡️ 气温：{data.temperature}°C\n"
        f"☁️ 天气：{data.weather}\n"
        f"💧 湿度：{data.humidity}%\n"
        f"🍃 风向：{data.wind_direction}\n"
        f"💨 风力：{data.wind_scale}级\n"
        f"━━━━━━━━━━━━\n"
        f"数据来源：和风天气"
    )
    
    await weather_cmd.finish(msg)