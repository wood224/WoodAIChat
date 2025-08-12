import uuid
import os
from django.contrib.auth.models import AbstractUser
from django.db import models


def user_avatar_upload_path(instance, filename):
    """
    用户头像上传路径函数
    该函数会被 ImageField 的 upload_to 参数调用
    生成格式: avatar/uuid4().ext
    """
    ext = filename.split(".")[-1].lower()
    new_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("avatar", new_filename)


class User(AbstractUser):
    first_name = None
    last_name = None
    is_staff = None
    is_superuser = None
    groups = None
    user_permissions = None

    name = models.CharField(
        "昵称",
        max_length=128,
        blank=False,
        null=False,
    )

    email = models.EmailField(
        "邮箱",
        blank=False,
        null=False,
        unique=True,
        error_messages={
            "unique": "该邮箱已被使用",
        },
    )

    gender = models.SmallIntegerField(
        "性别",
        choices=((0, "保密"), (1, "男"), (2, "女")),
        default=0,
    )

    is_active = models.BooleanField(
        "是否激活",
        default=True,
    )

    avatar = models.ImageField(
        "头像",
        upload_to=user_avatar_upload_path,  # 使用自定义上传路径函数
        default="avatar/default.png",
    )

    def save(self, *args, **kwargs):
        # 如果昵称为空，则使用用户名作为默认值
        if not self.name:
            self.name = self.username
        super().save(*args, **kwargs)
