import json
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


def json_dict():
    with open("../data/ingredients.json") as json_file:
        return json.load(json_file)


name = [i["title"] for i in json_dict()]
dimension = [i["dimension"] for i in json_dict()]


User = get_user_model()

fake = Faker(["ru_RU"])


class IngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ingredient

    name = factory.Iterator(name)
    measurement_unit = factory.Iterator(dimension)


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

        tags_count = Ingredient.objects.count()
        how_many = min(tags_count, how_many)
        start = random.randint(1, tags_count)
        tags = Ingredient.objects.order_by("?")[start:how_many]
        self.ingredients.add(*tags)

    @factory.post_generation
    def image(self, created, extracted, **kwargs):
        if not created:
            return

        image = urllib.request.urlopen("https://picsum.photos/800/800").read()
        self.image.save(self.name + ".jpg", ContentFile(image), save=False)


class IngredientItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IngredientItem

    ingredient = factory.SubFactory(IngredientFactory)
    recipe = factory.Iterator(Recipe.objects.all())
    amount = factory.LazyFunction(lambda: random.randint(1, 500))


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
