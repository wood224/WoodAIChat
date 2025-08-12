import secrets

from django.core.mail import send_mail
from django.shortcuts import redirect
from django_redis import get_redis_connection
from djangorestframework_camel_case.parser import CamelCaseJSONParser
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from users.models import User
from utils.response import StandardResponse
from wood_ai_chat_backend import settings


# Create your views here.
@extend_schema(description="邮箱验证")
class EmailVerifyViewSet(ViewSet):
    """
    邮箱验证
    """

    permission_classes = []
    parser_classes = [CamelCaseJSONParser]

    @action(
        methods=["get"],
        detail=False,
    )
    def email_code(self, request):
        print(request.query_params)
        email = request.query_params.get("email")
        change_pwd = request.query_params.get("changePwd", False)
        if not email:
            return StandardResponse(status=400, message="请输入邮箱")
        elif not change_pwd and User.objects.filter(email=email).exists():
            return StandardResponse(status=400, message="该邮箱已被使用")

        code = secrets.token_urlsafe(32)

        # 存储到 Redis
        redis_conn = get_redis_connection("ver_code")
        redis_conn.setex(f"email_{email}", 300, code)  # 300秒过期

        # 构造验证链接
        protocol = getattr(settings, "SITE_PROTOCOL", "http")
        domain = getattr(settings, "SITE_DOMAIN", "127.0.0.1:8000")
        verify_url = (
            f"{protocol}{domain}/verify/email_verify/?code={code}&email={email}"
        )

        # 发送验证邮件
        subject = "WoodAIChat 邮箱验证"
        message = f"""
            你好！

            感谢您注册 WoodAIChat。请点击下面的链接验证您的邮箱地址：

            {verify_url}

            如果您没有注册账户，请忽略此邮件。

            此链接将在5分钟后失效。

            祝好！
            WoodAIChat 团队
            """

        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@woodaichat.com")

        try:
            send_mail(subject, message, from_email, [email], fail_silently=False)
            return StandardResponse(message="验证邮件发送成功")
        except Exception as e:
            return StandardResponse(message=f"验证邮件发送失败：{str(e)}", status=500)

    @action(methods=["get"], detail=False)
    def email_verify(self, request):
        code = request.query_params.get("code")
        email = request.query_params.get("email")
        if not code or not email:
            # 重定向到前端验证结果页面，携带错误参数
            redirect_url = getattr(
                settings, "FRONTEND_VERIFY_RESULT_URL", "/verify-result"
            )
            return redirect(f"{redirect_url}?success=false&message=无效的验证链接")

        redis_conn = get_redis_connection("ver_code")
        stored_code = redis_conn.get(f"email_{email}")
        if not stored_code or stored_code.decode() != code:
            # 重定向到前端验证结果页面，携带错误参数
            redirect_url = getattr(
                settings, "FRONTEND_VERIFY_RESULT_URL", "/verify-result"
            )
            return redirect(f"{redirect_url}?success=false&message=验证码错误")

        # 验证成功后存储验证状态
        redis_conn.setex(f"email_verified_{email}", 60 * 30, "true")
        # 删除已使用的验证码
        redis_conn.delete(f"email_{email}")

        # 重定向到前端验证成功页面
        redirect_url = getattr(settings, "FRONTEND_VERIFY_RESULT_URL", "/verify-result")
        return redirect(f"{redirect_url}?success=true&message=邮箱验证成功")
