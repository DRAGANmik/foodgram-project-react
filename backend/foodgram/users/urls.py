from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LogoutAPIView, TokenAPIView, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "auth/token/login/",
        TokenAPIView.as_view(),
        name="token_login",
    ),
    path(
        "auth/token/logout/",
        LogoutAPIView.as_view(),
        name="token_logout",
    ),
    path(
        "auth/reset_password/",
        include("django_rest_passwordreset.urls", namespace="reset_password"),
    ),
]
