# 发布到真寻插件库 — Issue / PR 模板示例

请将下述内容填入 Issue（并打上 `Plugin` 标签）或作为 PR 的描述提交。

插件名: nonebot-plugin-weather
仓库地址: https://github.com/aikun-China/nonebot-plugin-weather
作者: aikun-China
版本: 0.1
描述: 基于 Zhenxun Bot 的天气查询、每日推送与气象预警插件，支持图文卡片与预警图片推送。

主要命令与用法:
- `/天气 <城市>` → 查询当前天气
- `/天气 订阅 <HH:MM>` → 每日定时推送
- `/天气 订阅 预警 每<N>分钟` → 预警监听

运行依赖（请在 `requirements.txt` 中查看或补充）:
- nonebot2
- nonebot-plugin-htmlrender
- httpx
- tortoise-orm

License: MIT

README: https://github.com/aikun-China/nonebot-plugin-weather/blob/main/README.md

附加说明（可选）:
- 已包含 `weather_card.html` 与本地 `resources/` 目录用于渲染。
- 如果需要，插件作者愿意协助调试安装问题。
