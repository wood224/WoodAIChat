from django.db import models
from users.models import User


class ChatSession(models.Model):
    """聊天会话模型"""

    title = models.CharField(max_length=200, verbose_name="会话标题")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")

    class Meta:
        db_table = "chat_session"
        verbose_name = "聊天会话"
        verbose_name_plural = "聊天会话"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class ChatModel(models.Model):
    """大模型配置模型"""

    name = models.CharField(max_length=100, unique=True, verbose_name="模型名称")
    model_id = models.CharField(max_length=100, unique=True, verbose_name="模型ID")
    description = models.TextField(blank=True, verbose_name="模型描述")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    ep_id = models.CharField(
        max_length=100, null=True, blank=True, unique=True, verbose_name="推理接入点ID"
    )

    class Meta:
        db_table = "chat_model"
        verbose_name = "大模型"
        verbose_name_plural = "大模型"

    def __str__(self):
        return self.name


class ChatMessage(models.Model):
    """聊天消息模型"""

    ROLE_CHOICES = (
        ("user", "用户"),
        ("assistant", "助手"),
        ("system", "系统"),
    )

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, verbose_name="聊天会话"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="角色")
    reasoning_content = models.TextField(
        null=True,
        blank=True,
        verbose_name="推理内容",
    )
    content = models.TextField(verbose_name="消息内容")
    model = models.ForeignKey(
        ChatModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="使用模型",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    tokens = models.IntegerField(default=0, verbose_name="消耗token数")
    parent_message = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="父消息",
        related_name="child_messages",
    )

    message_resp_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="消息的响应ID",
    )

    class Meta:
        db_table = "chat_message"
        verbose_name = "聊天消息"
        verbose_name_plural = "聊天消息"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.session.title} - {self.role}: {self.content[:50]}..."


class ChatSettings(models.Model):
    """聊天设置模型"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    default_model = models.ForeignKey(
        ChatModel, on_delete=models.SET_NULL, null=True, verbose_name="默认模型"
    )
    temperature = models.FloatField(default=0.7, verbose_name="温度")
    max_tokens = models.IntegerField(default=2048, verbose_name="最大token数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "chat_settings"
        verbose_name = "聊天设置"
        verbose_name_plural = "聊天设置"

    def __str__(self):
        return f"{self.user.username} 的设置"
