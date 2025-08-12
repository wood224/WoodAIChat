import json
import os
import time

from django.http import StreamingHttpResponse
from drf_spectacular.utils import extend_schema
from openai import OpenAI
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from chat.models import ChatMessage, ChatSession, ChatModel
from chat.serializers import (
    ChatSessionSerializer,
    ChatMessageSerializer,
    ChatModelSerializer,
)
from utils.response import (
    StandardResponse,
    StandardRetrieveModelMixin,
    StandardUpdateModelMixin,
    StandardDestroyModelMixin,
    StandardListModelMixin,
)


class Choice:
    def __init__(
        self,
        content="",
        role="assistant",
        index=0,
        reasoning_content="",
        finish_reason=None,
    ):
        self.content = content
        self.role = role
        self.index = index
        self.reasoning_content = reasoning_content
        self.finish_reason = finish_reason

    def to_dict(self):
        """
        将 Choice 对象转换为字典格式
        """
        choice_dict = {
            "index": self.index,
            "delta": {
                "role": self.role,
                "content": self.content,
            },
        }

        # 只有当 reasoning_content 不为空时才添加
        if self.reasoning_content:
            choice_dict["delta"]["reasoning_content"] = self.reasoning_content

        # 只有当 finish_reason 不为空时才添加
        if self.finish_reason:
            choice_dict["finish_reason"] = self.finish_reason

        return choice_dict


class SSEGenerator:
    def __init__(self, data_generator):
        """
        初始化 SSEGenerator

        :param data_generator: 一个生成器，产生要发送给客户端的数据字典
        """
        self.data_generator = data_generator

    @staticmethod
    def create_chat_chunk(
        id,
        choices,
        model,
        created=int(time.time()),
        object_type="response",
        usage=None,
    ):
        """
        创建一个符合格式的聊天块

        :param id: 响应ID
        :param choices: 选择项列表
        :param created: 创建时间戳
        :param model: 模型名称
        :param object_type: 对象类型
        :param usage: 使用情况统计
        :return: 格式化的字典
        """
        chunk = {
            "id": id,
            "choices": choices,
            "created": created,
            "model": model,
            "object": object_type,
        }

        if usage:
            chunk["usage"] = usage

        return chunk

    def __iter__(self):
        """
        使对象可迭代，生成 SSE 格式的响应
        """
        try:
            for data_dict in self.data_generator:
                # 确保数据是字典格式
                if isinstance(data_dict, dict):
                    # 生成 SSE 格式的响应
                    yield f"data: {json.dumps(data_dict, separators=(',', ':'))}\n\n"
                else:
                    # 如果不是字典，转换为字符串处理
                    yield f"data: {str(data_dict)}\n\n"
        except Exception as e:
            # 发送错误信息给客户端
            error_data = {"error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"


@extend_schema(description="聊天消息")
class ChatMessageView(StandardListModelMixin, CreateModelMixin, GenericViewSet):
    think = ("disabled", "enabled", "auto")
    api_key = os.environ.get("ARK_API_KEY")
    OpenAI_client = OpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key,
        # 设置服务响应超时时间，单位秒，推荐1800秒及以上
        timeout=1800,
        # 设置重试次数
        max_retries=2,
    )
    serializer_class = ChatMessageSerializer

    # 获取 Response API 的响应数据
    def generate_response_response(
        self, user_message, chat_session, chat_model, think_type, previous_response_id
    ):
        # 创建 Response API 的配置
        response_config = {
            "model": chat_model.model_id,
            "input": [{"role": "user", "content": user_message.content}],
            "stream": True,
            "extra_body": {
                "thinking": {"type": self.think[think_type]},
            },
        }
        if previous_response_id:
            response_config["previous_response_id"] = previous_response_id

        client = self.OpenAI_client
        res = client.responses.create(**response_config)

        # 收集AI回复消息
        ai_content = {
            "reasoning_content": "",
            "content": "",
            "tokens": 0,
            "response_id": "",
        }

        # 先发送完整的消息结构（除了reasoning_content、content和tokens）
        message_data = {
            "id": -1,  # 将在保存后更新
            "role": "assistant",
            "reasoning_content": "",  # 将逐步更新
            "content": "",  # 将逐步更新
            "created_at": None,  # 将在保存后更新
            "tokens": 0,  # 将逐步更新
            "message_resp_id": None,  # 将在保存后更新
            "session": ChatSessionSerializer(chat_session).data,
            "model": ChatModelSerializer(chat_model).data,
            # "session": {
            #     "id": chat_session.id,
            #     "title": chat_session.title,
            #     "user": chat_session.user.id,
            #     "updated_at": (
            #         chat_session.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            #         if chat_session.updated_at
            #         else None
            #     ),
            #     "is_active": chat_session.is_active,
            #     "created_at": (
            #         chat_session.created_at.strftime("%Y-%m-%d %H:%M:%S")
            #         if chat_session.created_at
            #         else None
            #     ),
            # },
            # "model": {
            #     "id": chat_model.id,
            #     "name": chat_model.name,
            #     "model_id": chat_model.model_id,
            #     "description": chat_model.description,
            #     "is_active": chat_model.is_active,
            #     "ep_id": chat_model.ep_id,
            # },
            "parent_message": user_message.id,
        }

        # 发送初始消息结构
        yield {"type": "message_start", "data": message_data}

        try:
            for chunk in res:
                if hasattr(chunk, "type"):
                    # 获取AI回复ID
                    if (
                        ai_content["response_id"] == ""
                        and chunk.type == "response.created"
                    ):
                        ai_content["response_id"] = chunk.response.id
                        continue
                    # 收集AI回复消息
                    if chunk.type == "response.reasoning_summary_text.delta":
                        ai_content["reasoning_content"] += chunk.delta

                        yield SSEGenerator.create_chat_chunk(
                            id=chunk.item_id,
                            choices=[
                                Choice(
                                    content="",
                                    role="assistant",
                                    reasoning_content=chunk.delta,
                                ).to_dict()
                            ],
                            model=chat_model.model_id,
                        )
                    elif chunk.type == "response.output_text.delta":
                        ai_content["content"] += chunk.delta
                        yield SSEGenerator.create_chat_chunk(
                            id=chunk.item_id,
                            choices=[
                                Choice(
                                    content=chunk.delta,
                                    role="assistant",
                                ).to_dict()
                            ],
                            model=chat_model.model_id,
                        )
                    # 统计token
                    if chunk.type == "response.completed":
                        ai_content["tokens"] = chunk.response.usage.total_tokens
                        yield SSEGenerator.create_chat_chunk(
                            id=chunk.response.id,
                            choices=[],
                            usage=chunk.response.usage.total_tokens,
                            model=chat_model.model_id,
                        )
        finally:
            # 保存AI回复消息
            ai_message_ser = ChatMessageSerializer(
                data={
                    "reasoning_content": ai_content["reasoning_content"],
                    "content": ai_content["content"],
                    "session": chat_session.id,
                    "role": "assistant",
                    "model": chat_model.id,
                    "tokens": ai_content["tokens"],
                    "parent_message": user_message.id,
                    "message_resp_id": (
                        ai_content["response_id"] if ai_content["response_id"] else None
                    ),
                }
            )
            ai_message_ser.is_valid(raise_exception=True)
            ai_message_instance = ai_message_ser.save()

            # 在流的最后发送完整的AI消息数据
            yield {
                "type": "message_end",
                "data": {
                    "id": ai_message_instance.id,
                    "created_at": ai_message_instance.created_at.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "message_resp_id": ai_message_instance.message_resp_id,
                    "tokens": ai_message_instance.tokens,
                },
            }

    def get_queryset(self):
        """
        过滤查询集，只返回当前用户的消息
        """
        user = self.request.user
        queryset = ChatMessage.objects.filter(session__user=user)

        # 如果提供了session_id查询参数，则进一步过滤
        session_id = self.request.query_params.get("session_id")
        if session_id:
            queryset = queryset.filter(session_id=session_id)

        return queryset

    # def create(self, request, *args, **kwargs):
    #     user = request.user
    #
    #     data = request.data
    #     content = data.get("content")
    #     session_id = data.get("session_id")
    #     parent_message_id = data.get("parent_message_id")
    #     model_id = data.get("model_id")
    #     think_type = data.get("think_type", 1)
    #
    #     # 如果session_id不存在，则创建一个会话
    #     if not session_id:
    #         chat_session_ser = ChatSessionSerializer(
    #             data={
    #                 "title": content[:20] if len(content) > 20 else content,
    #                 "user": user.id,
    #             }
    #         )
    #         if not chat_session_ser.is_valid():
    #             return StandardResponse(status=400, message=chat_session_ser.errors)
    #         chat_session = chat_session_ser.save()
    #         parent_message_id = None
    #     # 验证会话是否存在且属于当前用户
    #     else:
    #         try:
    #             chat_session = ChatSession.objects.get(id=session_id, user=user)
    #         except ChatSession.DoesNotExist:
    #             return StandardResponse(
    #                 status=404, message="当前会话不存在或无权限访问"
    #             )
    #
    #     # 验证模型是否存在
    #     try:
    #         chat_model = ChatModel.objects.get(model_id=model_id)
    #     except ChatModel.DoesNotExist:
    #         return StandardResponse(status=404, message="当前模型不存在")
    #
    #     user_message_ser = ChatMessageSerializer(
    #         data={
    #             "content": content,
    #             "role": "user",
    #             "session": chat_session.id,
    #             "model": chat_model.id,
    #             "parent_message": parent_message_id,
    #         }
    #     )
    #     user_message_ser.is_valid(raise_exception=True)
    #     user_message = user_message_ser.save()
    #
    #     previous_response_id = (
    #         user_message.parent_message.message_resp_id
    #         if user_message.parent_message
    #         and user_message.parent_message.message_resp_id
    #         else None
    #     )
    #
    #     sse_response = SSEGenerator(
    #         self.generate_response_response(
    #             user_message, chat_session, chat_model, think_type, previous_response_id
    #         )
    #     )
    #
    #     return StreamingHttpResponse(
    #         sse_response,
    #         content_type="text/event-stream",
    #     )

    def create(self, request, *args, **kwargs):
        user = request.user

        data = request.data
        content = data.get("content")
        session_id = data.get("session_id")
        parent_message_id = data.get("parent_message_id")
        model_id = data.get("model_id")

        # 如果session_id不存在，则创建一个会话
        if not session_id:
            chat_session_ser = ChatSessionSerializer(
                data={
                    "title": content[:20] if len(content) > 20 else content,
                    "user": user.id,
                }
            )
            if not chat_session_ser.is_valid():
                return StandardResponse(status=400, message=chat_session_ser.errors)
            chat_session = chat_session_ser.save()
            parent_message_id = None
        # 验证会话是否存在且属于当前用户
        else:
            try:
                chat_session = ChatSession.objects.get(id=session_id, user=user)
            except ChatSession.DoesNotExist:
                return StandardResponse(
                    status=404, message="当前会话不存在或无权限访问"
                )

        # 验证模型是否存在
        try:
            chat_model = ChatModel.objects.get(model_id=model_id)
        except ChatModel.DoesNotExist:
            return StandardResponse(status=404, message="当前模型不存在")

        user_message_ser = ChatMessageSerializer(
            data={
                "content": content,
                "role": "user",
                "session": chat_session.id,
                "model": chat_model.id,
                "parent_message": parent_message_id,
            }
        )
        user_message_ser.is_valid(raise_exception=True)
        user_message = user_message_ser.save()

        # 更新会话的更新时间
        chat_session.save(update_fields=["updated_at"])

        # 返回用户消息的详细信息
        return StandardResponse(
            status=201,
            message="用户消息创建成功",
            data=ChatMessageSerializer(user_message).data,
        )

    @action(detail=False, methods=["post"], url_path="ai-response")
    def ai_response(self, request, *args, **kwargs):
        """
        获取AI响应的独立端点
        """

        user = request.user
        data = request.data
        user_message_id = data.get("user_message_id")
        think_type = data.get("think_type", 1)

        try:
            user_message = ChatMessage.objects.get(
                id=user_message_id, session__user=user, role="user"
            )
        except ChatMessage.DoesNotExist:
            return StandardResponse(status=404, message="用户消息不存在或无权限访问")

        chat_session = user_message.session
        chat_model = user_message.model

        previous_response_id = (
            user_message.parent_message.message_resp_id
            if user_message.parent_message
            and user_message.parent_message.message_resp_id
            else None
        )

        sse_response = SSEGenerator(
            self.generate_response_response(
                user_message, chat_session, chat_model, think_type, previous_response_id
            )
        )

        return StreamingHttpResponse(
            sse_response,
            content_type="text/event-stream",
        )


@extend_schema(description="聊天会话")
class ChatSessionView(
    StandardListModelMixin,
    StandardRetrieveModelMixin,
    StandardUpdateModelMixin,
    StandardDestroyModelMixin,
    GenericViewSet,
):
    serializer_class = ChatSessionSerializer

    def get_queryset(self):
        # 从 request 中获取当前用户
        user = self.request.user
        queryset = ChatSession.objects.filter(user=user)

        return queryset
