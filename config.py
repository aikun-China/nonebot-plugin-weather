from pydantic import BaseModel
from nonebot import get_driver
from nonebot.plugin import PluginMetadata

class WeatherConfig(BaseModel):
    api_key: str = ""
    default_city: str = "北京"

# 从 NoneBot 全局配置读取 weather.xxx
global_config = get_driver().config
weather_config = WeatherConfig.parse_obj(global_config.dict().get("weather", {}))

__plugin_meta__ = PluginMetadata(
    name="天气查询",
    description="和风天气查询，文字+emoji返回",
    usage="/天气 [城市名]",
    config=WeatherConfig,
)