from django.contrib.auth import authenticate
from django.utils import timezone
from djangorestframework_camel_case.parser import CamelCaseJSONParser
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import UserSerializer, PasswordChangeSerializer
from utils.response import (
    StandardResponse,
    StandardRetrieveModelMixin,
    StandardUpdateModelMixin,
    StandardDestroyModelMixin,
)
from wood_ai_chat_backend import settings


# Create your views here.
@extend_schema(description="用户")
class UserViewSet(
    StandardRetrieveModelMixin,
    StandardUpdateModelMixin,
    StandardDestroyModelMixin,
    viewsets.ViewSetMixin,
    generics.GenericAPIView,
):
    """
    用户
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = (
        MultiPartParser,
        FormParser,
        CamelCaseJSONParser,
    )  # 添加支持文件上传的解析器

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        password = request.data.get("newPassword")

        if password:
            instance.set_password(password)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return StandardResponse(data=serializer.data, message="更新成功")

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    # 注册
    @action(methods=["POST"], detail=False, permission_classes=[])
    def register(self, request):
        ser = UserSerializer(data=request.data)
        ser.is_valid(raise_exception=True)  # 抛出 ValidationError

        ser.save()
        return StandardResponse(data=ser.data, message="注册成功")

    # 登录
    @action(methods=["POST"], detail=False, permission_classes=[])
    def login(self, request):
        data = request.data
        # 输入验证
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return StandardResponse(status=400, message="用户名和密码不能为空")

        user = authenticate(username=username, password=password)
        if not user:
            return StandardResponse(status=400, message="用户名或密码错误")
        if not user.is_active:
            return StandardResponse(status=400, message="用户已被禁用")

        # 更新最近登录时间
        user.last_login = timezone.now()
        user.save()

        # 生成 Token
        refresh = RefreshToken.for_user(user)

        # 返回数据
        ser = UserSerializer(user)
        return StandardResponse(
            status=200,
            data=ser.data,
            message="登录成功",
            access=str(refresh.access_token),
            refresh=str(refresh),
            expires_in=int(
                settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
            ),
        )

    # 通过 token 获取当前用户信息
    @action(methods=["GET"], detail=False)
    def query_info(self, request):
        user = request.user
        ser = UserSerializer(user)
        return StandardResponse(data=ser.data, message="获取用户信息成功")

    # 更新用户头像
    @action(methods=["POST"], detail=False)
    def update_avatar(self, request):
        user = request.user
        avatar = request.FILES.get("avatar")

        if not avatar:
            return StandardResponse(status=400, message="未提供头像文件")

        # 更新用户头像
        user.avatar = avatar
        user.save()

        # 返回更新后的用户信息
        ser = UserSerializer(user)
        return StandardResponse(status=200, data=ser.data, message="头像更新成功")

    # 修改用户密码
    @action(methods=["PATCH"], detail=False)
    def update_password(self, request):
        ser = PasswordChangeSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)

        user = request.user
        new_password = ser.validated_data["new_password"]
        user.set_password(new_password)
        user.save()

        return StandardResponse(message="修改密码成功")
