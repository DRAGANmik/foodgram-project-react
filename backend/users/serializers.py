from django.contrib.auth import (
    authenticate,
    get_user_model,
    password_validation,
)
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from recipes.models import Recipe
from users.models import Subscription

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "last_name",
            "first_name",
            "email",
            "is_subscribed",
        ]

    def get_is_subscribed(self, obj):
        try:
            request = self.context.get("request")
            subscription = Subscription.objects.filter(
                subscriber=request.user, author=obj
            )
            return bool(subscription)
        except TypeError:
            return False


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"

    def create(self, validated_data):
        author = validated_data["author"]
        subscriber = validated_data["subscriber"]
        if author == subscriber:
            raise serializers.ValidationError(
                {"message": "Извините, но подписаться на себя нельзя."}
            )
        if not Subscription.objects.filter(
            author=author, subscriber=subscriber
        ):
            Subscription.objects.create(author=author, subscriber=subscriber)
        else:
            raise serializers.ValidationError(
                {"message": "Извините, но подписаться второй раз нельзя."}
            )
        return validated_data


class DetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "last_name",
            "first_name",
            "email",
        ]


class AuthorSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = [
            "id",
            "username",
            "last_name",
            "first_name",
            "email",
            "is_subscribed",
            "recipes",
            "recipes_count",
        ]

    def get_recipes(self, obj):
        from recipes.serializers import RecipeSubscriptionSerializer

        qset = Recipe.objects.filter(author=obj)
        return [RecipeSubscriptionSerializer(el).data for el in qset]

    def get_recipes_count(self, obj):
        qset = Recipe.objects.filter(author=obj)
        return qset.count()


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        max_length=128, write_only=True, required=True
    )
    new_password = serializers.CharField(
        max_length=128, write_only=True, required=True
    )

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _("Введенный пароль невереный. Пожалуйста введите снова.")
            )
        return value

    def validate(self, data):
        password_validation.validate_password(
            data["new_password"], self.context["request"].user
        )
        return data

    def save(self, **kwargs):
        password = self.validated_data["new_password"]
        user = self.context["request"].user
        user.set_password(password)
        user.save()
        return user


class TokenSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(
        max_length=128, write_only=True, required=True
    )

    def validate(self, data):
        email = data["email"]
        password = data["password"]
        if email is None:
            raise serializers.ValidationError("Введите email.")
        if password is None:
            raise serializers.ValidationError("Введите пароль.")

        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                "Пользователь с таким email или паролем не найден."
            )

        if not user.is_active:
            raise serializers.ValidationError("Пользователь заблокирован.")

        return user