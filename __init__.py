"""
nonebot-plugin-weather
A Zhenxun Bot plugin for weather subscription and warning push.
"""

from nonebot import get_driver, on_command, logger
from nonebot.adapters import Message, Event
from nonebot.params import CommandArg, ArgPlainText
from nonebot.plugin import PluginMetadata
from pydantic import BaseModel, Field
from typing import Optional, Union

# --- 插件元数据（显示在 nb plugin list 中）---
__plugin_meta__ = PluginMetadata(
    name="天气订阅",
    description="多平台天气查询、定时推送与气象预警通知",
    usage=(
        "• /天气 <城市名> → 查询当前天气\n"
        "• /天气 订阅 <时间> → 每日定时推送（例：07:30）\n"
        "• /天气 订阅 预警 每<数字>分钟 → 预警监听（例：每5分钟）\n"
        "• /天气 help → 显示本帮助"
    ),
    type="application",
    homepage="https://github.com/aikun-China/nonebot-plugin-weather",
)

# --- 配置模型（自动从 config.toml 加载）---
class WeatherConfig(BaseModel):
    api_key: str = Field("", description="OpenWeatherMap 或和风天气 API Key")
    warning_api_key: str = Field("", description="国家预警中心 12379 token（用于预警）")
    default_city: str = Field("北京", description="默认查询城市")
    warning_check_interval: int = Field(300, description="预警检查间隔（秒，默认 5 分钟）")

driver = get_driver()
config = driver.config
weather_config = WeatherConfig.parse_obj(config)

# --- 命令匹配器 ---
weather_cmd = on_command("天气", priority=5, block=True)
subscribe_cmd = on_command("天气 订阅", priority=5, block=True)
help_cmd = on_command("天气 help", priority=5, block=True)

# --- 帮助命令 ---
@help_cmd.handle()
async def handle_help(event: Event):
    await help_cmd.finish(__plugin_meta__.usage)

# --- 主天气查询命令：/天气 北京 ---
@weather_cmd.handle()
async def handle_weather(event: Event, arg: Message = CommandArg()):
    city = ArgPlainText(arg).strip()
    if not city:
        await weather_cmd.finish("❌ 请指定城市，例如：`/天气 北京`")
    
    # ✅ 此处将调用 api.get_weather(city) 获取数据
    # ⚠️ 下一步我将为你生成 api.py，此处先返回模拟响应
    logger.info(f"User {event.get_user_id()} queried weather for: {city}")
    
    # 模拟返回（实际将替换为 api.get_weather()）
    weather_data = {
        "city": city,
        "temperature": "26°C",
        "feels_like": "28°C",
        "description": "晴朗",
        "emoji": "☀️",
        "humidity": "45%",
        "wind": "东北风 2级",
        "updated_at": "2024-05-20 14:30"
    }
    
    # ✅ 此处将调用 render.render_weather_card(weather_data) 生成图片
    # ⚠️ 下一步我将为你生成 render.py，此处先返回文字卡片
    card_text = (
        f"🌤️ {weather_data['city']} 天气\n"
        f"🌡️ 温度：{weather_data['temperature']} （体感 {weather_data['feels_like']}）\n"
        f"📝 天气：{weather_data['emoji']} {weather_data['description']}\n"
        f"💧 湿度：{weather_data['humidity']} | 💨 风：{weather_data['wind']}\n"
        f"⏰ 更新于：{weather_data['updated_at']}"
    )
    await weather_cmd.finish(card_text)

# --- 订阅命令：/天气 订阅 07:30 或 /天气 订阅 预警 每5分钟 ---
@subscribe_cmd.handle()
async def handle_subscribe(event: Event, arg: Message = CommandArg()):
    text = ArgPlainText(arg).strip()
    if not text:
        await subscribe_cmd.finish("❌ 请指定订阅参数，例如：`/天气 订阅 07:30` 或 `/天气 订阅 预警 每5分钟`")
    
    # 解析订阅类型
    if text.startswith("预警"):
        # 预警订阅：/天气 订阅 预警 每5分钟
        parts = text.split()
        if len(parts) < 3 or not parts[2].startswith("每") or not parts[2].endswith("分钟"):
            await subscribe_cmd.finish("❌ 预警订阅格式错误，请用：`/天气 订阅 预警 每<数字>分钟`（例：每5分钟）")
        
        try:
            interval = int(parts[2][1:-2])  # 提取 "每5分钟" → 5
            if interval < 1 or interval > 60:
                raise ValueError
        except (ValueError, IndexError):
            await subscribe_cmd.finish("❌ 请输入有效的分钟数（1–60）")
        
        # ✅ 此处将存入数据库 WarningSubscription（需 models.py + Tortoise）
        logger.info(f"User {event.get_user_id()} subscribed to warnings every {interval} min")
        await subscribe_cmd.finish(f"✅ 已开启预警监听！每 {interval} 分钟检查一次，发现预警立即推送。")
    
    elif ":" in text and len(text) == 5:  # 时间格式：07:30
        # 定时订阅：/天气 订阅 07:30
        try:
            hour, minute = map(int, text.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except (ValueError, IndexError):
            await subscribe_cmd.finish("❌ 时间格式错误，请用 24 小时制，例如：`07:30` 或 `14:00`")
        
        # ✅ 此处将存入数据库 WeatherSubscription（需 models.py + Tortoise）
        logger.info(f"User {event.get_user_id()} subscribed daily weather at {text}")
        await subscribe_cmd.finish(f"✅ 已设置每日天气推送时间：{text}。明天开始生效！")
    
    else:
        await subscribe_cmd.finish("❌ 无法识别订阅类型。\n请用：\n• `/天气 订阅 07:30`（每日定时）\n• `/天气 订阅 预警 每5分钟`（预警监听）")

# --- 插件加载成功提示 ---
@driver.on_startup
async def startup():
    logger.opt(colors=True).info(
        f"<green>✅ nonebot-plugin-weather 已加载</green> | "
        f"默认城市：<cyan>{weather_config.default_city}</cyan> | "
        f"预警检查间隔：<cyan>{weather_config.warning_check_interval}s</cyan>"
    )