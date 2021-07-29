import random

import factory
from faker import Faker

from recipes.models import Ingredient, IngredientItem, Recipe, RecipeTag
from users.factories import UserFactory

fake = Faker(["ru_RU"])


class IngredientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ingredient

    name = factory.Faker("word")
    measurement_unit = factory.Faker(
        "word", ext_word_list=["кг", "г", "мл", "л"]
    )


class RecipeTagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RecipeTag
        django_get_or_create = ["name"]

    name = factory.Faker("word")
    color = factory.Faker("hex_color", locale="en_US")


class RecipeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Recipe

    author = factory.SubFactory(UserFactory)

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


class IngredientItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IngredientItem

    ingredient = factory.Iterator(Ingredient.objects.all())
    recipe = factory.Iterator(Recipe.objects.all())
    amount = factory.LazyFunction(lambda: random.randint(1, 100))
