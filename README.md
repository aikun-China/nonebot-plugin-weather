# 🌤️ nonebot-plugin-weather

> 基于 [Zhenxun Bot](https://github.com/HibiKier/zhenxun_bot) 的天气查询插件，**默认输出精美天气图片卡片**。

[![NoneBot2](https://img.shields.io/badge/NoneBot2-v2.0.0+-green.svg)](https://github.com/nonebot/nonebot2)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 功能特性

- 🖼️ **精美图片卡片** —— 默认输出高清天气图片，信息一目了然
- ☀️ **实时天气查询** —— 输入城市名，秒回图文天气卡片
- 🏙️ **默认城市支持** —— 未指定城市时自动使用配置的默认城市
- 🌡️ **丰富气象数据** —— 温度、天气状况、湿度、风向、风力、能见度
- 🎨 **Emoji 天气映射** —— 晴☀️、雨🌧️、雪🌨️、霾😷 等自动匹配
- 🔌 **和风天气 API** —— 稳定可靠的数据来源

## 📦 安装

### 方式一：通过 nb-cli 安装（推荐）

```bash
nb plugin install nonebot-plugin-weather
```

### 方式二：手动安装

```bash
git clone https://github.com/aikun-China/nonebot-plugin-weather.git
```

将插件文件夹放入 Zhenxun Bot 的 `plugin` 目录下，重启 Bot 即可。

## ⚙️ 配置

在 Zhenxun Bot 的 `data/config.yaml` 中添加以下配置（首次加载插件后会自动生成）：

```yaml
nonebot_plugin_weather:
  API_KEY: ""           # 和风天气 API Key（必填）
  DEFAULT_CITY: "北京"   # 默认查询城市
```

### 🔑 API Key 获取

1. 前往 [和风天气开发者平台](https://dev.qweather.com/)
2. 注册账号并创建新项目
3. 获取 Web API Key
4. 将 Key 填入上述配置项

> 💡 **提示**：配置修改后需重启 Bot 生效。

## 🚀 使用

### 指令列表

| 指令 | 权限 | 说明 | 示例 |
|------|------|------|------|
| `天气 [城市名]` | 所有人 | 查询指定城市实时天气（图片卡片） | `天气 上海` |
| `天气` | 所有人 | 查询默认城市天气（图片卡片） | `天气` |

### 输出效果

发送 `天气 北京` 后，Bot 会回复一张精美的天气图片卡片：

- 🏙️ **城市名** + 📅 **日期** 标签
- 🌤️ **天气图标** + 🌡️ **实时温度**
- ☁️ **天气状况**（晴 / 多云 / 雨等）
- 📊 **四宫格信息卡片**：
  - 💧 湿度
  - 🍃 风向
  - 💨 风力
  - 👁️ 能见度
- 🔗 **数据来源**：和风天气

> 所有数据均通过和风天气 API 实时获取，确保准确性。

## 📁 项目结构

```
nonebot-plugin-weather/
├── __init__.py      # 插件入口 & 指令处理（图片生成 & 发送）
├── api.py           # 和风天气 API 封装（实时 / 预报 / 空气质量）
├── config.py        # 插件配置定义（Zhenxun 注册配置）
├── requirements.txt # 依赖列表
└── LICENSE          # MIT 协议
```

## 🔧 技术细节

- **框架**：NoneBot2 + Zhenxun Bot
- **适配器**：OneBot V11
- **HTTP 客户端**：httpx
- **数据验证**：Pydantic
- **API 来源**：和风天气 (QWeather)
- **输出格式**：图片卡片（默认）

## 📝 依赖

- Python >= 3.9
- nonebot2 >= 2.0.0
- httpx
- pydantic
- zhenxun_bot

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📜 协议

本项目采用 [MIT License](LICENSE) 开源。

---

> Made with ❤️ by [aikun-China](https://github.com/aikun-China)
