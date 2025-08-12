from datetime import datetime

from rest_framework import serializers
from rest_framework.mixins import (
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import Throttled


# 自定义响应类
class StandardResponse(Response):
    def __init__(self, data=None, message="操作成功", status=200, **kwargs):
        # 构造响应数据结构
        response_data = {
            "status": status,
            "data": data,
            "message": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # 合并额外的响应数据
        response_data.update(kwargs)

        # 调用父类构造函数
        super().__init__(data=response_data, status=status)


# 自定义 Mixin
class StandardListModelMixin(ListModelMixin):
    """
    自定义List Mixin，返回统一格式响应
    """

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return StandardResponse(data=serializer.data)


class StandardRetrieveModelMixin(RetrieveModelMixin):
    """
    自定义Retrieve Mixin，返回统一格式响应
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return StandardResponse(data=serializer.data, message="获取信息成功")


class StandardUpdateModelMixin(UpdateModelMixin):
    """
    自定义Update Mixin，返回统一格式响应
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}

        return StandardResponse(data=serializer.data, message="更新成功")


class StandardDestroyModelMixin(DestroyModelMixin):
    """
    自定义Destroy Mixin，返回统一格式响应
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return StandardResponse(status=204, message="删除成功")


# 自定义异常处理
def custom_exception_handler(exc, context):
    # 调用默认的异常处理器
    response = exception_handler(exc, context)
    # 处理限流异常错误
    if isinstance(exc, Throttled):
        if response is not None:
            # 将 detail 字段改为 message 字段
            response.data = {
                "status": response.status_code,
                "message": response.data.get("detail", "请求过于频繁"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

    # 处理序列化器验证错误
    if response is not None and isinstance(exc, serializers.ValidationError):
        error_message = "未知错误"
        # 获取第一个错误信息
        for field, errs in exc.detail.items():
            error_message = f"{field}:{errs[0]}"
            break

        response.data = {
            "status": response.status_code,
            "message": error_message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    return response
