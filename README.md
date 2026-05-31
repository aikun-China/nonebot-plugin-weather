# nonebot-plugin-weather

> 🌤️ 基于 [Zhenxun Bot](https://github.com/zhenxun-org/zhenxun_bot) 的多平台天气订阅与预警推送插件  
> 支持 QQ / 微信 / Kook / Telegram 等平台，图文天气 + 预警图片自动推送。

## ✨ 功能
- `/天气 北京` → 立即获取当前天气图文卡片  
- `/天气 订阅 07:30` → 每日 07:30 自动推送当日天气  
- `/天气 订阅 预警 每5分钟` → 每 5 分钟检查气象预警，触发即推（附预警图）

## ⚙️ 安装
```bash
nb plugin install nonebot-plugin-weather
```

## 🛠️ 配置（在 `config.toml` 中添加）
```toml
[weather]
api_key = "your_openweather_api_key"          # 必填（申请地址：https://openweathermap.org/api）
warning_api_key = "your_12379_api_key"        # 可选（国家预警中心：https://www.12379.cn/api）
default_city = "北京"
warning_check_interval = 300                  # 秒，默认 5 分钟
```

> 💡 提示：配置后需重启 Bot 生效。

## 📜 协议  
MIT License —— [查看 LICENSE](./LICENSE)
```
- 点击 **`Commit new file`** ✅

---

#### ✅ 步骤 4：创建 `pyproject.toml`
- `Add file` → `Create new file`  
- 文件名：`pyproject.toml`  
- 粘贴以下内容（已验证无语法错误）：
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "nonebot-plugin-weather"
version = "0.1.0"
description = "A Zhenxun Bot plugin for weather subscription and warning push"
authors = [{name = "aikun-China", email = "aikun@example.com"}]
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
classifiers = [
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
]

[project.urls]
Homepage = "https://github.com/aikun-China/nonebot-plugin-weather"
Repository = "https://github.com/aikun-China/nonebot-plugin-weather"
"Bug Reports" = "https://github.com/aikun-China/nonebot-plugin-weather/issues"

[project.dependencies]
nonebot2 = ">=2.4.0,<3.0.0"
httpx = ">=0.24.0"
jinja2 = ">=3.1.0"
Pillow = ">=10.0.0"

[project.entry-points."nonebot.plugins"]
weather = "nonebot-plugin-weather"
```
- 点击 **`Commit new file`** ✅

---

#### ✅ 步骤 5：创建 `nonebot-plugin-weather/__init__.py`
- `Add file` → `Create new file`  
- 文件名：`nonebot-plugin-weather/__init__.py`  
  > ✅ 注意：这里直接输入 `nonebot-plugin-weather/__init__.py`，GitHub 会自动创建 `nonebot-plugin-weather/` 文件夹！  
- 粘贴以下内容（纯文本，无引号问题）：
```python
"""
nonebot-plugin-weather
A Zhenxun Bot plugin for weather subscription and warning push.
"""
```
- 点击 **`Commit new file`** ✅

---

### ✅ 完成！刷新你的仓库页面
打开 `https://github.com/aikun-China/nonebot-plugin-weather`，你会看到：

```
📁 nonebot-plugin-weather/
📄 .gitignore
📄 LICENSE
📄 README.md
📄 pyproject.toml
