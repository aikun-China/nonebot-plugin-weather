"""
Tortoise ORM models for nonebot-plugin-weather.
Compatible with Zhenxun Bot's built-in Tortoise instance.
"""

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class WeatherSubscription(models.Model):
    """
    Daily weather push subscription.
    Example: User 10001 in group 20001 subscribes to "北京" at 07:30.
    """

    id = fields.IntField(pk=True)
    user_id = fields.CharField(max_length=64, description="User ID (str, e.g. '123456789')")  # QQ/WeChat/ID
    group_id = fields.CharField(
        max_length=64,
        null=True,
        description="Group ID if subscribed in group; NULL for private chat",
    )
    city = fields.CharField(
        max_length=64,
        default="",
        description="City name (e.g. '北京', '杭州市'). Empty → use config.default_city",
    )
    time = fields.TimeField(description="Daily push time (e.g., 07:30:00)")
    enabled = fields.BooleanField(default=True, description="Whether this subscription is active")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "weather_subscription"
        # Ensure index for fast query by user/group
        indexes = ["user_id", "group_id"]


class WarningSubscription(models.Model):
    """
    Real-time warning monitoring subscription.
    Example: User 10001 monitors warnings for "北京市" every 300 seconds.
    """

    id = fields.IntField(pk=True)
    user_id = fields.CharField(max_length=64, description="User ID")
    group_id = fields.CharField(
        max_length=64,
        null=True,
        description="Group ID if subscribed in group; NULL for private chat",
    )
    province = fields.CharField(
        max_length=32,
        default="北京市",
        description="Province name (e.g. '北京市', '广东省')",
    )
    city = fields.CharField(
        max_length=32,
        default="北京市",
        description="City name (e.g. '北京市', '广州市')",
    )
    interval_seconds = fields.IntField(
        default=300,
        description="Check interval in seconds (default 5 min)",
    )
    enabled = fields.BooleanField(default=True)
    last_checked = fields.DatetimeField(null=True, description="Last successful check time")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "warning_subscription"
        indexes = ["user_id", "group_id"]


# --- Pydantic models for API serialization (optional but recommended) ---
WeatherSubscriptionPydantic = pydantic_model_creator(
    WeatherSubscription,
    name="WeatherSubscription",
    exclude=("created_at", "updated_at"),
)

WarningSubscriptionPydantic = pydantic_model_creator(
    WarningSubscription,
    name="WarningSubscription",
    exclude=("created_at", "updated_at"),
)