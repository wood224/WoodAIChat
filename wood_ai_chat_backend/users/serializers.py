from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.utils.translation import gettext_lazy as _


from users.models import User


def ver_email(redis_conn, email):
    """
    验证邮箱验证状态
    """
    if redis_conn is None:
        redis_conn = get_redis_connection("ver_code")
    ver_status = redis_conn.get(f"email_verified_{email}")

    if not ver_status or ver_status.decode() != "true":
        return False

    return True


class UserSerializer(ModelSerializer):
    confirm_password = serializers.CharField(max_length=128, write_only=True)

    date_joined = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    gender = serializers.IntegerField(required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "gender",
            "email",
            "is_active",
            "password",
            "confirm_password",
            "date_joined",
            "last_login",
            "avatar",
            "name",
        )
        read_only_fields = ["last_login"]
        extra_kwargs = {
            "username": {"required": True},
            "password": {"write_only": True},
        }

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data["gender"] = instance.get_gender_display()
    #     return data

    def validate_avatar(self, value):
        """
        验证头像文件的格式和大小
        """
        if value:
            # 检查文件大小 (限制为2MB)
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError("头像文件大小不能超过2MB")

            # 检查文件格式
            valid_extensions = ["jpg", "jpeg", "png"]
            extension = value.name.split(".")[-1].lower()
            if extension not in valid_extensions:
                raise serializers.ValidationError("只允许上传jpg、jpeg、png格式的图片")

        return value

    def validate(self, attrs):
        # 获取当前用户实例（更新操作时）
        instance = getattr(self, "instance", None)

        # 检查是否是更新操作且是否有需要验证邮箱的字段被修改
        email = attrs.get("email")
        password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        # 判断是否是修改密码操作
        is_password_change = (
            "old_password" in self.context.get("request").data
            if self.context.get("request")
            else False
        )
        old_password = (
            self.context.get("request").data.get("old_password")
            if self.context.get("request")
            else None
        )

        # 只有在更新邮箱或密码时才需要邮箱验证
        need_email_verification = False

        if instance:  # 更新操作
            # 检查邮箱是否被修改
            if email and email != instance.email:
                need_email_verification = True
            # 检查密码是否被修改
            if password:
                need_email_verification = True
            # 如果是密码修改操作，验证旧密码
            if is_password_change and old_password:
                if not instance.check_password(old_password):
                    raise serializers.ValidationError("旧密码错误")
        else:  # 创建操作
            # 创建用户时如果提供了邮箱或密码，则需要验证
            if email or password:
                need_email_verification = True

        # 验证密码一致性
        if password:
            if not confirm_password:
                raise serializers.ValidationError("请输入确认密码")
            if password != confirm_password:
                raise serializers.ValidationError("密码不一致")

        # 只有在需要时才检查邮箱验证状态
        if need_email_verification and email:
            redis_conn = get_redis_connection("ver_code")
            if not ver_email(redis_conn, email):
                raise serializers.ValidationError("邮箱未验证")

            redis_conn.delete(f"email_verified_{email}")
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


# 修改密码序列化器
class PasswordChangeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_email(self, value):
        user = self.context["request"].user
        # 验证邮箱是否属于当前用户
        if user.email != value:
            raise serializers.ValidationError("邮箱不匹配")
        return value

    def validate(self, attrs):
        email = attrs.get("email")
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")
        user = self.context["request"].user

        redis_conn = get_redis_connection("ver_code")
        # 验证邮箱验证码（检查邮箱是否已验证）
        if not ver_email(redis_conn, email):
            raise serializers.ValidationError("邮箱未验证")

        # 验证旧密码是否正确
        if not user.check_password(old_password):
            raise serializers.ValidationError("旧密码错误")

        # 验证新密码和确认密码是否一致
        if new_password != confirm_password:
            raise serializers.ValidationError("新密码和确认密码不一致")

        # 验证密码强度（Django 自带）
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            # 将英文错误信息翻译为中文
            error_messages = []
            for message in e.messages:
                # 根据错误信息内容进行翻译
                if "too short" in message:
                    error_messages.append(_("密码太短"))
                elif "too common" in message:
                    error_messages.append(_("密码太常见"))
                elif "entirely numeric" in message:
                    error_messages.append(_("密码不能全为数字"))
                elif "similar to" in message:
                    error_messages.append(_("密码与用户信息太相似"))
                else:
                    # 如果没有匹配的翻译，则使用原消息
                    error_messages.append(_(message))
            raise serializers.ValidationError(error_messages)

        redis_conn.delete(f"email_verified_{email}")
        return attrs
