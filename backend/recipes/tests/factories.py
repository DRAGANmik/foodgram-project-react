import random
import urllib

import factory
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from faker import Faker

from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientItem,
    Recipe,
    RecipeTag,
)

User = get_user_model()

fake = Faker(["ru_RU"])


class IngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ingredient
        django_get_or_create = ["name"]

    name = factory.Faker("word")
    measurement_unit = factory.Faker(
        "word", ext_word_list=["кг", "г", "мл", "л"]
    )


class RecipeTagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RecipeTag
        django_get_or_create = ["name"]

    name = factory.Faker(
        "word",
        ext_word_list=["Завтрак", "Обед", "Ужин", "Полдник", "Ланч", "Десерт"],
    )
    color = factory.Faker("hex_color", locale="en_US")


class RecipeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Recipe

    author = factory.Iterator(User.objects.all())

    name = factory.Faker("word")
    text = factory.Faker("text")
    cooking_time = factory.LazyFunction(lambda: random.randint(5, 100))
    image = factory.django.ImageField(
        color=factory.Faker("color_name", locale="en_US")
    )

    @factory.post_generation
    def tags(self, created, extracted, **kwargs):
        if not created:
            return

        at_least = 1
        how_many = extracted or at_least

        tags_count = RecipeTag.objects.count()
        how_many = min(tags_count, how_many)

        tags = RecipeTag.objects.order_by("?")[:how_many]
        self.tags.add(*tags)

    @factory.post_generation
    def ingredients(self, created, extracted, **kwargs):
        if not created:
            return

        at_least = 4
        how_many = extracted or at_least

        ingredients_count = Ingredient.objects.count()
        start = random.randint(1, ingredients_count)
        how_many = min(ingredients_count, how_many) + start

        ingredients = Ingredient.objects.order_by("?")[start:how_many]
        [
            IngredientItem.objects.create(
                ingredient=ingredient,
                recipe=self,
                amount=random.randint(1, 500),
            )
            for ingredient in ingredients
        ]
        self.ingredients.add(*ingredients)

    @factory.post_generation
    def image(self, created, extracted, **kwargs):
        if not created:
            return

        image = urllib.request.urlopen("https://picsum.photos/800/800").read()
        self.image.save(self.name + ".jpg", ContentFile(image), save=False)


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.Iterator(User.objects.all())
    recipe = factory.Iterator(Recipe.objects.all())


class FavoriteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Favorite

    user = factory.Iterator(User.objects.all())
    recipe = factory.Iterator(Recipe.objects.all())
