from nonebot.plugin import PluginMetadata
from zhenxun.configs.config import Config
from zhenxun.configs.utils import PluginExtraData, RegisterConfig

# 注册配置项（Zhenxun 启动时会自动写入 data/config.yaml）
__plugin_meta__ = PluginMetadata(
    name="天气查询",
    description="和风天气查询，文字+emoji风格",
    usage="/天气 [城市名]",
    extra=PluginExtraData(
        author="aikun-China",
        version="0.1.0",
        configs=[
            RegisterConfig(
                module="nonebot_plugin_weather",
                key="API_KEY",
                value="",
                help="和风天气 API Key（必填），申请地址：https://dev.qweather.com/",
                default_value="",
                type=str,
            ),
            RegisterConfig(
                module="nonebot_plugin_weather",
                key="DEFAULT_CITY",
                value="北京",
                help="默认查询城市",
                default_value="北京",
                type=str,
            ),
        ],
    ).dict(),
)
