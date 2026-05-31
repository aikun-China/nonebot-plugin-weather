"""
Weather card and warning image renderer for nonebot-plugin-weather.
Uses nonebot-plugin-htmlrender (built into Zhenxun Bot) and local resources.
"""

import asyncio
from pathlib import Path
from typing import Optional, Union

from nonebot_plugin_htmlrender import template_to_image
from nonebot import logger

# --- 资源路径（自动定位到 nonebot-plugin-weather/resources/）---
RESOURCE_DIR = Path(__file__).parent / "resources"
ICONS_DIR = RESOURCE_DIR / "icons"
WARNING_DIR = RESOURCE_DIR / "warning"
TEMPLATES_DIR = RESOURCE_DIR / "templates"

# --- 兜底图（必须存在）---
UNKNOWN_WARNING_IMAGE = WARNING_DIR / "unknown_warning.png"


# --- 天气卡片渲染 ---
async def render_weather_card(
    weather_data: dict,
    template_name: str = "weather_card.html",
) -> Optional[bytes]:
    """
    Render weather data to PNG image using Jinja2 template.
    
    Args:
        weather_data: Dict with keys: city, temperature, feels_like, description,
                      emoji, humidity, wind, updated_at
        template_name: Jinja2 template file name under TEMPLATES_DIR
    
    Returns:
        PNG image bytes, or None on failure
    """
    try:
        # Ensure template exists
        template_path = TEMPLATES_DIR / template_name
        if not template_path.exists():
            logger.error(f"[Render] Weather template not found: {template_path}")
            return None

        # Render HTML → PNG
        image_bytes = await template_to_image(
            template_path=str(template_path),
            templates={
                "weather": weather_data,
            },
            pages={
                "viewport": {"width": 600, "height": 300},
                "base_url": str(TEMPLATES_DIR),
            },
        )
        logger.debug(f"[Render] Weather card rendered for {weather_data.get('city', 'unknown')}")
        return image_bytes

    except Exception as e:
        logger.exception(f"[Render] Failed to render weather card: {e}")
        return None


# --- 预警图片路径解析（安全版）---
def get_warning_image_path(warning_title: str) -> Optional[Path]:
    """
    Safely resolve warning image path from warning title.
    
    Rules:
      - Only allow Chinese chars, letters, digits, spaces, parentheses, underscores
      - Reject any path containing ".." or absolute path
      - Return None if file doesn't exist
    
    Example:
      Input: "暴雨橙色预警" → Output: resources/warning/暴雨橙色预警.png
    """
    # Sanitize filename: keep only safe chars
    import re
    safe_title = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9\s\(\)\_]", "", warning_title).strip()
    if not safe_title:
        logger.warning(f"[Render] Invalid warning title sanitized to empty: {warning_title}")
        return UNKNOWN_WARNING_IMAGE

    # Build path
    image_path = WARNING_DIR / f"{safe_title}.png"

    # Security check: prevent directory traversal
    try:
        # Resolve and ensure it's under WARNING_DIR
        resolved = image_path.resolve()
        if not str(resolved).startswith(str(WARNING_DIR.resolve())):
            logger.warning(f"[Render] Path traversal attempt blocked: {image_path}")
            return UNKNOWN_WARNING_IMAGE
    except Exception:
        return UNKNOWN_WARNING_IMAGE

    # Return if exists, else fallback
    if image_path.exists():
        return image_path
    else:
        logger.info(f"[Render] Warning image not found, using fallback: {safe_title}.png → {UNKNOWN_WARNING_IMAGE.name}")
        return UNKNOWN_WARNING_IMAGE


# --- 预警图片发送辅助函数（供 __init__.py 调用）---
async def send_warning_image(
    warning_info: dict,
    use_fallback: bool = False,
) -> Optional[bytes]:
    """
    Load warning image bytes for sending.
    
    Args:
        warning_info: Dict with "title", "content", etc.
        use_fallback: If True, always return unknown_warning.png (for testing)
    
    Returns:
        PNG bytes, or None
    """
    if use_fallback:
        image_path = UNKNOWN_WARNING_IMAGE
    else:
        title = warning_info.get("title", "未知预警")
        image_path = get_warning_image_path(title)

    try:
        if image_path.exists():
            return image_path.read_bytes()
        else:
            logger.warning(f"[Render] Warning image missing: {image_path}")
            return UNKNOWN_WARNING_IMAGE.read_bytes()
    except Exception as e:
        logger.exception(f"[Render] Failed to load warning image: {e}")
        return None


# --- 初始化检查（插件加载时自动触发）---
async def _check_resources():
    """Validate required resource directories on plugin load."""
    required_dirs = [ICONS_DIR, WARNING_DIR, TEMPLATES_DIR]
    for d in required_dirs:
        if not d.exists():
            logger.warning(f"[Render] Required resource dir missing: {d} (will be created)")
            try:
                d.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"[Render] Failed to create dir {d}: {e}")

# Run check once at import
asyncio.create_task(_check_resources())