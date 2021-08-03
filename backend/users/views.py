from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework import permissions, serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import Subscription
from .serializers import (
    AuthorSerializer,
    ChangePasswordSerializer,
    CreateUserSerializer,
    SubscriptionSerializer,
    TokenSerializer,
    UserSerializer,
)

User = get_user_model()


class CreateListDestroyViewSet(
    CreateModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet
):
    pass


class TokenAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "auth_token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = get_object_or_404(Token, user=request.user)
        token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action != "list" and self.action != "retrieve":
            return CreateUserSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=["GET", "PATCH"],
        url_path="me",
        url_name="me",
        permission_classes=[permissions.IsAuthenticated],
    )
    def view_me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UserSerializer(user, data=request.data)

        if serializer.is_valid() and request.method == "PATCH":
            serializer.save()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["GET", "DELETE"],
        url_path="subscribe",
        url_name="subscribe",
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, pk):
        serializer = SubscriptionSerializer(
            data={"author": pk, "subscriber": request.user.id}
        )
        if request.method == "GET":
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"status": "Подписался"}, status=status.HTTP_201_CREATED
            )

        serializer.is_valid(raise_exception=True)
        if not Subscription.objects.filter(**serializer.validated_data):
            raise serializers.ValidationError(
                {
                    "message": "Извините,"
                    " но нельзя отписаться, если вы не подписаны."
                }
            )

        unsubscribe = get_object_or_404(
            Subscription, **serializer.validated_data
        )
        unsubscribe.delete()
        return Response(
            {"status": "Отписался"}, status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False,
        methods=["GET"],
        url_path="subscriptions",
        url_name="subscriptions",
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        subscriber = User.objects.filter(
            author__in=request.user.subscriber.all()
        ).order_by("id")
        page = self.paginate_queryset(subscriber)
        if page is not None:
            serializer = AuthorSerializer(
                subscriber, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = AuthorSerializer(
            subscriber, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["POST"],
        url_path="set_password",
        url_name="set_password",
        permission_classes=[permissions.IsAuthenticated],
    )
    def set_password(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"status": "Пароль изменен"}, status=status.HTTP_201_CREATED
        )


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    # send an e-mail to the user
    context = {
        "current_user": reset_password_token.user,
        "username": reset_password_token.user.username,
        "email": reset_password_token.user.email,
        "reset_password_url": "{}?token={}".format(
            instance.request.build_absolute_uri(
                reverse("password_reset:reset-password-confirm")
            ),
            reset_password_token.key,
        ),
    }

    # render email text
    email_html_message = render_to_string("user_reset_password.html", context)
    email_plaintext_message = render_to_string(
        "user_reset_password.txt", context
    )

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Foodgram"),
        # message:
        email_plaintext_message,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email],
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
