from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientItem,
    Recipe,
    RecipeTag,
)
from users.serializers import UserSerializer


class RecipeTagSerialzier(serializers.ModelSerializer):
    class Meta:
        model = RecipeTag
        fields = "__all__"


class RecipeSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ["id", "name", "image", "cooking_time"]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientItemSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientItem
        fields = ["id", "name", "amount", "measurement_unit"]


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = RecipeTagSerialzier(many=True)
    author = UserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = "__all__"

    def get_ingredients(self, obj):
        qset = IngredientItem.objects.filter(recipe=obj)
        return IngredientItemSerializer(qset, many=True).data

    def get_is_favorited(self, obj):
        try:
            request = self.context.get("request")
            is_favorited = Favorite.objects.filter(
                user=request.user, recipe=obj
            )
            return is_favorited.exists()
        except TypeError:
            return False

    def get_is_in_shopping_cart(self, obj):
        try:
            request = self.context.get("request")
            is_in_cart = Cart.objects.filter(user=request.user, recipe=obj)
            return is_in_cart.exists()
        except TypeError:
            return False


class IngredientItemPost(serializers.Serializer):

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)


class RecipeSerializerPost(serializers.ModelSerializer):
    ingredients = IngredientItemPost(
        many=True,
    )
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=RecipeTag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = [
            "image",
            "ingredients",
            "tags",
            "name",
            "text",
            "cooking_time",
        ]

    def validate(self, data):
        unique_ingr = data["ingredients"]
        ingr_list = []
        for item in unique_ingr:
            id = item["id"]
            amount = item["amount"]
            try:
                exist_item = get_object_or_404(
                    IngredientItem, id=id, amount=amount
                )
                if exist_item.ingredient in ingr_list:
                    raise serializers.ValidationError(
                        {
                            "message": "Извините,"
                            " но добавить одинаковые ингредиенты нельзя."
                        }
                    )
                else:
                    ingr_list.append(exist_item.ingredient)
            except Exception:
                new_ingr = get_object_or_404(Ingredient, id=id)
                if new_ingr in ingr_list:
                    raise serializers.ValidationError(
                        {
                            "message": "Извините,"
                            " но добавить одинаковые ингредиенты нельзя."
                        }
                    )
                else:
                    ingr_list.append(new_ingr)

        if len(ingr_list) != len(set(ingr_list)):
            raise serializers.ValidationError(
                {
                    "message": "Извините,"
                    " но добавить одинаковые ингредиенты нельзя."
                }
            )
        return data

    def create(self, validated_data):
        image = validated_data.pop("image")
        tags = validated_data.pop("tags")

        request = self.context.get("request")
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(
            image=image, author=request.user, **validated_data
        )
        for tag in tags:
            recipe.tags.add(tag)

        items = [
            IngredientItem(
                recipe=recipe,
                ingredient=get_object_or_404(Ingredient, id=item["id"]),
                amount=item["amount"],
            )
            for item in ingredients
        ]

        IngredientItem.objects.bulk_create(items)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):

        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        try:
            image = validated_data.pop("image")
            instance.image = image
            instance.save()
        except KeyError:
            pass

        recipe = Recipe.objects.filter(id=instance.id)
        recipe.update(**validated_data)

        instance_tags = [tag for tag in instance.tags.all()]

        for tag in tags:
            if tag in instance_tags:
                instance_tags.remove(tag)
            else:
                instance.tags.add(tag)
        instance.tags.remove(*instance_tags)

        instance_ingredients = [
            ingredient for ingredient in instance.ingredients.all()
        ]
        for item in ingredients:
            amount = item["amount"]
            id = item["id"]
            try:
                exist_item_ingredient = IngredientItem.objects.get(
                    id=id, amount=amount
                )

                instance_ingredients.remove(exist_item_ingredient.ingredient)
            except IngredientItem.DoesNotExist:
                IngredientItem.objects.create(
                    recipe=instance,
                    ingredient=get_object_or_404(Ingredient, id=id),
                    amount=amount,
                )

        instance.ingredients.remove(*instance_ingredients)

        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = "__all__"

    def create(self, validated_data):
        user = validated_data["user"]
        recipe = validated_data["recipe"]
        obj, created = Favorite.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            raise serializers.ValidationError(
                {
                    "message": "Извините,"
                    " но добавить в избранное второй раз нельзя."
                }
            )
        return validated_data


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"

    def create(self, validated_data):
        user = validated_data["user"]
        recipe = validated_data["recipe"]
        obj, created = Cart.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            raise serializers.ValidationError(
                {"message": "Извините, но рецепт уже добвлен в корзину."}
            )
        return validated_data
