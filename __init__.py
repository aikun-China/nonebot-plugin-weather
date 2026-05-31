from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent
from nonebot.params import CommandArg
from nonebot.adapters import Message
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER

from zhenxun.configs.config import Config
from zhenxun.configs.utils import PluginExtraData, RegisterConfig
from zhenxun.services.log import logger

from . import api

__plugin_meta__ = PluginMetadata(
    name="天气查询",
    description="和风天气查询，支持实时/预报/预警/空气质量",
    usage="/天气 [城市] | /天气 预报 [城市] [天数] | /天气 订阅 [城市] [HH:MM]",
    extra=PluginExtraData(
        author="aikun-China",
        version="0.5.0",
        configs=[
            RegisterConfig(module="nonebot_plugin_weather", key="API_KEY", value="", help="和风天气 API Key", default_value="", type=str),
            RegisterConfig(module="nonebot_plugin_weather", key="API_HOST", value="", help="和风天气专属 API Host", default_value="", type=str),
            RegisterConfig(module="nonebot_plugin_weather", key="DEFAULT_CITY", value="北京", help="默认查询城市", default_value="北京", type=str),
        ],
    ).dict(),
)

weather_cmd = on_command("天气", priority=5, block=True)

# ============ 订阅数据 ============
import json
from pathlib import Path

SUBSCRIPTION_FILE = Path(__file__).parent / "subscriptions.json"
_subscriptions: dict[str, dict] = {}

def _load_subscriptions():
    global _subscriptions
    if SUBSCRIPTION_FILE.exists():
        try:
            with open(SUBSCRIPTION_FILE, "r", encoding="utf-8") as f:
                _subscriptions = json.load(f)
        except Exception:
            _subscriptions = {}
    else:
        _subscriptions = {}

def _save_subscriptions():
    try:
        with open(SUBSCRIPTION_FILE, "w", encoding="utf-8") as f:
            json.dump(_subscriptions, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"[Weather] 保存订阅失败: {e}")

def _get_user_id(event) -> str:
    return str(event.get_user_id())

def _parse_time(time_str: str):
    import re
    time_str = time_str.strip()
    if re.match(r"^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$", time_str):
        parts = time_str.split(":")
        return True, f"{int(parts[0]):02d}:{parts[1]}"
    if re.match(r"^([0-1][0-9]|2[0-3])([0-5][0-9])$", time_str):
        return True, f"{time_str[:2]}:{time_str[2:]}"
    return False, "时间格式错误，请使用 HH:MM 或 HHMM"

_load_subscriptions()

# ============ 图标 & HTML ============
WEATHER_ICON = {
    "晴": "100", "多云": "101", "阴": "104", "小雨": "305", "中雨": "306",
    "大雨": "307", "暴雨": "310", "雷阵雨": "302", "雪": "499", "小雪": "400",
    "中雪": "401", "大雪": "402", "雾": "501", "霾": "502", "沙": "503",
    "尘": "504", "风": "999",
}

def get_icon(weather: str) -> str:
    for k, v in WEATHER_ICON.items():
        if k in weather:
            return v
    return "100"

def get_emoji(weather: str) -> str:
    em = {"晴": "☀️", "多云": "⛅", "阴": "☁️", "小雨": "🌦️", "中雨": "🌧️",
          "大雨": "⛈️", "暴雨": "⛈️", "雷阵雨": "⛈️", "雪": "🌨️", "小雪": "🌨️",
          "中雪": "❄️", "大雪": "❄️", "雾": "🌫️", "霾": "😷", "沙": "💨", "尘": "💨", "风": "🍃"}
    for k, v in em.items():
        if k in weather:
            return v
    return "🌡️"

def get_weekday(date_str: str) -> str:
    from datetime import datetime
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return weekdays[dt.weekday()]
    except Exception:
        return ""

def get_warning_color(level: str):
    colors = {
        "blue": ("#2196F3", "#E3F2FD"),
        "yellow": ("#FFC107", "#FFF8E1"),
        "orange": ("#FF9800", "#FFF3E0"),
        "red": ("#F44336", "#FFEBEE"),
    }
    return colors.get(level, ("#9E9E9E", "#F5F5F5"))

def generate_now_html(data: api.WeatherData, warnings: list = None, air: api.AirQuality = None) -> str:
    emoji = get_emoji(data.weather)
    icon_code = get_icon(data.weather)
    icon_url = f"https://icons.qweather.com/assets/icons/{icon_code}.svg"
    tianyi = "#66CCFF"

    # 预警HTML
    warning_html = ""
    if warnings:
        for w in warnings:
            color, bg = get_warning_color(w.level)
            warning_html += f'''<div style="background: {bg}; border-left: 4px solid {color}; border-radius: 8px; padding: 10px 14px; margin-bottom: 10px; display: flex; align-items: center;">
                <span style="font-size: 22px; margin-right: 10px;">⚠️</span>
                <div>
                    <div style="font-size: 14px; font-weight: bold; color: {color};">{w.title}</div>
                    <div style="font-size: 11px; color: #888; margin-top: 2px;">{w.pub_time}</div>
                </div>
            </div>'''

    # 空气质量HTML
    aqi_html = ""
    if air:
        try:
            aqi_val = int(air.aqi)
            aqi_color = "#4CAF50" if aqi_val <= 50 else "#FFC107" if aqi_val <= 100 else "#FF9800" if aqi_val <= 150 else "#F44336"
        except:
            aqi_color = "#9E9E9E"
        aqi_html = f'''<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 14px; margin-top: 14px; color: white;">
            <div style="text-align: center; margin-bottom: 10px;">
                <span style="display: inline-block; background: rgba(255,255,255,0.2); padding: 4px 16px; border-radius: 16px; font-size: 14px; font-weight: bold;">{air.aqi} {air.level}</span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(6, 1fr); gap: 6px; text-align: center;">
                <div><div style="font-size: 10px; opacity: 0.8;">PM2.5</div><div style="font-size: 13px; font-weight: bold;">{air.pm25}</div></div>
                <div><div style="font-size: 10px; opacity: 0.8;">PM10</div><div style="font-size: 13px; font-weight: bold;">{air.pm10}</div></div>
                <div><div style="font-size: 10px; opacity: 0.8;">O₃</div><div style="font-size: 13px; font-weight: bold;">{air.o3}</div></div>
                <div><div style="font-size: 10px; opacity: 0.8;">CO</div><div style="font-size: 13px; font-weight: bold;">{air.co}</div></div>
                <div><div style="font-size: 10px; opacity: 0.8;">NO₂</div><div style="font-size: 13px; font-weight: bold;">{air.no2}</div></div>
                <div><div style="font-size: 10px; opacity: 0.8;">SO₂</div><div style="font-size: 13px; font-weight: bold;">{air.so2}</div></div>
            </div>
        </div>'''

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ width: 440px; padding: 16px; background: linear-gradient(180deg, #E6F7FF 0%, #B3E5FC 100%); font-family: "Microsoft YaHei", sans-serif; }}
.card {{ background: rgba(255,255,255,0.95); border-radius: 20px; padding: 22px; box-shadow: 0 8px 32px rgba(102,204,255,0.25); border: 2px solid {tianyi}; overflow: hidden; }}
.header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }}
.city {{ font-size: 26px; font-weight: bold; color: #1a5276; }}
.time {{ font-size: 12px; color: #5dade2; background: #E6F7FF; padding: 3px 10px; border-radius: 10px; }}
.main {{ display: flex; align-items: center; justify-content: center; margin-bottom: 16px; }}
.main img {{ width: 80px; height: 80px; margin-right: 16px; filter: drop-shadow(0 4px 8px rgba(102,204,255,0.3)); }}
.temp {{ font-size: 52px; font-weight: 200; color: #1a5276; line-height: 1; }}
.temp span {{ font-size: 24px; color: #4DB8F0; vertical-align: top; }}
.weather-text {{ font-size: 18px; color: #4DB8F0; margin-top: 4px; text-align: center; font-weight: 500; }}
.details {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 14px; }}
.detail {{ text-align: center; padding: 10px 6px; background: linear-gradient(135deg, #E6F7FF 0%, #fff 100%); border-radius: 10px; border: 1px solid rgba(102,204,255,0.25); }}
.detail .icon {{ font-size: 18px; margin-bottom: 3px; }}
.detail .label {{ font-size: 10px; color: #5dade2; }}
.detail .value {{ font-size: 13px; color: #1a5276; font-weight: 600; }}
.footer {{ text-align: center; margin-top: 12px; font-size: 10px; color: #5dade2; }}
</style></head><body>
<div class="card">
    <div class="header"><div class="city">{emoji} {data.city}</div><div class="time">{data.date}</div></div>
    {warning_html}
    <div class="main">
        <img src="{icon_url}" onerror="this.style.display='none'">
        <div><div class="temp">{data.temperature}<span>°C</span></div><div class="weather-text">{data.weather}</div></div>
    </div>
    <div class="details">
        <div class="detail"><div class="icon">💧</div><div class="label">湿度</div><div class="value">{data.humidity}%</div></div>
        <div class="detail"><div class="icon">🍃</div><div class="label">风向</div><div class="value">{data.wind_direction}</div></div>
        <div class="detail"><div class="icon">💨</div><div class="label">风力</div><div class="value">{data.wind_scale}级</div></div>
        <div class="detail"><div class="icon">👁️</div><div class="label">能见度</div><div class="value">--</div></div>
    </div>
    {aqi_html}
    <div class="footer">◆ 数据来源：和风天气 ◆</div>
</div>
</body></html>"""

def generate_forecast_html(city: str, forecasts: list, warnings: list = None) -> str:
    tianyi = "#66CCFF"

    warning_html = ""
    if warnings:
        for w in warnings:
            color, bg = get_warning_color(w.level)
            warning_html += f'''<div style="background: {bg}; border-left: 4px solid {color}; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center;">
                <span style="font-size: 22px; margin-right: 10px;">⚠️</span>
                <div><div style="font-size: 14px; font-weight: bold; color: {color};">{w.title}</div></div>
            </div>'''

    forecast_rows = ""
    for f in forecasts:
        weekday = get_weekday(f.date)
        day_icon = get_icon(f.day_weather)
        night_icon = get_icon(f.night_weather)
        day_url = f"https://icons.qweather.com/assets/icons/{day_icon}.svg"
        night_url = f"https://icons.qweather.com/assets/icons/{night_icon}.svg"
        forecast_rows += f'''<div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid rgba(102,204,255,0.15);">
            <div style="width: 70px;">
                <div style="font-size: 14px; font-weight: bold; color: #1a5276;">{weekday}</div>
                <div style="font-size: 11px; color: #888;">{f.date[5:]}</div>
            </div>
            <div style="flex: 1; display: flex; align-items: center; justify-content: center; gap: 16px;">
                <div style="text-align: center;">
                    <img src="{day_url}" style="width: 32px; height: 32px;" onerror="this.style.display='none'">
                    <div style="font-size: 11px; color: #5dade2;">{f.day_weather}</div>
                </div>
                <div style="text-align: center;">
                    <img src="{night_url}" style="width: 32px; height: 32px;" onerror="this.style.display='none'">
                    <div style="font-size: 11px; color: #888;">{f.night_weather}</div>
                </div>
            </div>
            <div style="width: 90px; text-align: right;">
                <span style="font-size: 16px; font-weight: bold; color: #1a5276;">{f.temp_max}°</span>
                <span style="font-size: 13px; color: #888;"> / {f.temp_min}°</span>
            </div>
        </div>'''

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ width: 440px; padding: 16px; background: linear-gradient(180deg, #E6F7FF 0%, #B3E5FC 100%); font-family: "Microsoft YaHei", sans-serif; }}
.card {{ background: rgba(255,255,255,0.95); border-radius: 20px; padding: 22px; box-shadow: 0 8px 32px rgba(102,204,255,0.25); border: 2px solid {tianyi}; }}
.header {{ font-size: 22px; font-weight: bold; color: #1a5276; margin-bottom: 16px; text-align: center; }}
</style></head><body>
<div class="card">
    <div class="header">🌤️ {city} {len(forecasts)}天预报</div>
    {warning_html}
    {forecast_rows}
    <div style="text-align: center; margin-top: 12px; font-size: 10px; color: #5dade2;">◆ 数据来源：和风天气 ◆</div>
</div>
</body></html>"""

async def send_html_card(html: str, target, bot=None):
    try:
        from nonebot import require
        require("nonebot_plugin_htmlrender")
        from nonebot_plugin_htmlrender import html_to_pic
        from nonebot_plugin_alconna.uniseg import UniMessage
        img_bytes = await html_to_pic(html=html, viewport={"width": 480, "height": 10})
        await UniMessage.image(raw=img_bytes).send(target, bot)
    except Exception as e:
        logger.warning(f"[Weather] 图片生成失败: {e}")
        from nonebot_plugin_alconna.uniseg import UniMessage
        await UniMessage.text("⚠️ 图片生成失败").send(target, bot)

# ============ 主命令 ============
@weather_cmd.handle()
async def handle_weather(event: MessageEvent, args: Message = CommandArg()):
    user_id = _get_user_id(event)
    raw_text = args.extract_plain_text().strip()
    parts = raw_text.split(maxsplit=2)

    # 订阅相关子命令
    if raw_text in ["取消订阅", "退订"]:
        if user_id in _subscriptions:
            del _subscriptions[user_id]
            _save_subscriptions()
            await weather_cmd.finish("✅ 天气订阅已取消")
        else:
            await weather_cmd.finish("❌ 你当前没有订阅")
        return

    if raw_text in ["我的订阅", "订阅状态"]:
        if user_id not in _subscriptions:
            await weather_cmd.finish("❌ 你当前没有订阅\n使用：天气 订阅 [城市] [时间]")
            return
        sub = _subscriptions[user_id]
        loc = f"群 {sub.get('group_id', '私聊')}" if sub.get("group_id") else "私聊"
        await weather_cmd.finish(f"📋 你的订阅：{sub['city']} 每天 {sub['time']} | {loc}")
        return

    if parts and parts[0] in ["订阅", "subscribe"]:
        if len(parts) < 3:
            await weather_cmd.finish("❌ 格式：天气 订阅 [城市] [HH:MM]")
            return
        city = parts[1]
        ok, result = _parse_time(parts[2])
        if not ok:
            await weather_cmd.finish(f"❌ {result}")
            return
        group_id = str(event.group_id) if isinstance(event, GroupMessageEvent) else ""
        _subscriptions[user_id] = {"city": city, "time": result, "group_id": group_id}
        _save_subscriptions()
        loc = f"群 {group_id}" if group_id else "私聊"
        await weather_cmd.finish(f"✅ 订阅成功！{city} 每天 {result} | {loc}")
        return

    # 获取配置
    try:
        base_config = Config.get("nonebot_plugin_weather") or {}
    except Exception:
        base_config = {}
    api_key = base_config.get("API_KEY", "")
    api_host = base_config.get("API_HOST", "")
    default_city = base_config.get("DEFAULT_CITY", "北京")

    if not api_key or not api_host:
        await weather_cmd.finish("❌ API Key 或 API Host 未配置")
        return

    from nonebot_plugin_alconna.uniseg import MsgTarget
    target = MsgTarget(event)

    # 预报模式
    if parts and parts[0] in ["预报", "预告", "forecast"]:
        city = parts[1] if len(parts) > 1 else default_city
        days = 1
        if len(parts) > 2:
            try:
                days = min(max(int(parts[2]), 1), 7)
            except ValueError:
                pass

        forecasts = await api.get_forecast(city, days, api_key, api_host)
        warnings = await api.get_warnings(city, api_key, api_host)

        if not forecasts:
            await weather_cmd.finish(f"❌ 获取「{city}」{days}天预报失败")
            return

        html = generate_forecast_html(city, forecasts, warnings)
        await send_html_card(html, target)
        return

    # 实时天气模式
    city = raw_text if raw_text else default_city

    weather_data = await api.get_weather(city, api_key, api_host)
    warnings = await api.get_warnings(city, api_key, api_host)
    air = await api.get_air_quality(city, api_key, api_host)

    if not weather_data:
        await weather_cmd.finish(f"❌ 获取「{city}」天气失败")
        return

    html = generate_now_html(weather_data, warnings, air)
    await send_html_card(html, target)


# ============ 管理员指令 ============
admin_weather = on_command("天气管理", priority=5, block=True, permission=SUPERUSER)

@admin_weather.handle()
async def handle_admin(event: MessageEvent, args: Message = CommandArg()):
    raw_text = args.extract_plain_text().strip()
    parts = raw_text.split(maxsplit=2)

    if not parts:
        if not _subscriptions:
            await admin_weather.finish("📋 当前没有任何订阅")
            return
        lines = ["📋 所有天气订阅：", "=" * 30]
        for uid, sub in _subscriptions.items():
            loc = f"群 {sub.get('group_id', '私聊')}" if sub.get("group_id") else "私聊"
            lines.append(f"QQ: {uid} | {sub['city']} | {sub['time']} | {loc}")
        await admin_weather.finish("\n".join(lines))
        return

    cmd = parts[0]
    if cmd in ["删除", "del"]:
        if len(parts) < 2:
            await admin_weather.finish("❌ 格式：天气管理 删除 [QQ号]")
            return
        uid = parts[1]
        if uid in _subscriptions:
            del _subscriptions[uid]
            _save_subscriptions()
            await admin_weather.finish(f"✅ 已删除 QQ {uid} 的订阅")
        else:
            await admin_weather.finish(f"❌ QQ {uid} 没有订阅")
        return

    if cmd in ["修改", "mod"]:
        if len(parts) < 3:
            await admin_weather.finish("❌ 格式：天气管理 修改 [QQ号] [城市] [时间]")
            return
        uid = parts[1]
        rest = parts[2].split(maxsplit=1)
        if len(rest) < 2:
            await admin_weather.finish("❌ 格式错误")
            return
        ok, result = _parse_time(rest[1])
        if not ok:
            await admin_weather.finish(f"❌ {result}")
            return
        if uid not in _subscriptions:
            await admin_weather.finish(f"❌ QQ {uid} 没有订阅")
            return
        old = _subscriptions[uid]
        _subscriptions[uid]["city"] = rest[0]
        _subscriptions[uid]["time"] = result
        _save_subscriptions()
        await admin_weather.finish(f"✅ 已修改：{old['city']} {old['time']} → {rest[0]} {result}")
        return

    await admin_weather.finish("📋 天气管理：查看/删除 [QQ]/修改 [QQ] [城市] [时间]")


# ============ 定时推送 ============
from nonebot import require
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

@scheduler.scheduled_job("cron", minute="*/1", id="weather_subscription_check")
async def check_subscriptions():
    from datetime import datetime
    now = datetime.now()
    current_time = f"{now.hour:02d}:{now.minute:02d}"
    if not _subscriptions:
        return
    try:
        base_config = Config.get("nonebot_plugin_weather") or {}
    except Exception:
        return
    api_key = base_config.get("API_KEY", "")
    api_host = base_config.get("API_HOST", "")
    if not api_key or not api_host:
        return
    try:
        from nonebot import get_bot
        bot = get_bot()
    except Exception:
        return
    from nonebot_plugin_alconna.uniseg import MsgTarget
    for uid, sub in list(_subscriptions.items()):
        if sub.get("time") != current_time:
            continue
        try:
            weather_data = await api.get_weather(sub["city"], api_key, api_host)
            warnings = await api.get_warnings(sub["city"], api_key, api_host)
            air = await api.get_air_quality(sub["city"], api_key, api_host)
            if not weather_data:
                continue
            group_id = sub.get("group_id", "")
            if group_id:
                await bot.send_group_msg(group_id=int(group_id), message=f"[CQ:at,qq={uid}] 您的每日天气推送！")
                target = MsgTarget(str(group_id))
            else:
                await bot.send_private_msg(user_id=int(uid), message="🌤️ 您的每日天气推送！")
                target = MsgTarget(str(uid), private=True)
            html = generate_now_html(weather_data, warnings, air)
            await send_html_card(html, target, bot)
        except Exception as e:
            logger.error(f"[Weather] 推送失败 {uid}: {e}")
