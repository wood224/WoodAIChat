from django.urls import path, include
from rest_framework.routers import DefaultRouter

from chat.views import ChatSessionView, ChatMessageView


router = DefaultRouter()
router.register(r"message", ChatMessageView, basename="chat-message")
router.register(r"session", ChatSessionView, basename="chat-session")

urlpatterns = [
    # path("session/", ChatSessionView.as_view()),
    # path("message/", ChatMessageView.as_view()),
    path("", include(router.urls)),
]
