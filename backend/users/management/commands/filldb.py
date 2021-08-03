import random

import factory
from django.core.management.base import BaseCommand

from recipes.tests.factories import (
    CartFactory,
    FavoriteFactory,
    IngredientFactory,
    RecipeFactory,
    RecipeTagFactory,
)
from users.tests.factories import SubscriptionFactory, UserFactory


class AllFactories:
    def create_user(self, arg):
        UserFactory.create_batch(arg)

    def create_ingredient(self, arg):
        IngredientFactory.create_batch(arg)

    def create_recipetag(self, arg):
        RecipeTagFactory.create_batch(arg)

    def create_recipe(self, arg):
        for _ in range(arg):
            num_tags = random.randint(1, 2)
            num_ingr = random.randint(3, 6)
            RecipeFactory.create(tags=num_tags, ingredients=num_ingr)

    def create_cart(self, arg):
        CartFactory.create_batch(arg)

    def create_favorite(self, arg):
        FavoriteFactory.create_batch(arg)

    def create_subscription(self, arg):
        SubscriptionFactory.create_batch(arg)


allfactories = AllFactories()

OPTIONS_AND_FUNCTIONS = {
    "user": allfactories.create_user,
    "ingredient": allfactories.create_ingredient,
    "recipetag": allfactories.create_recipetag,
    "recipe": allfactories.create_recipe,
    "cart": allfactories.create_cart,
    "favorite": allfactories.create_favorite,
    "subscription": allfactories.create_subscription,
}


class Command(BaseCommand):
    help = "Fill Data Base with test data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            nargs=1,
            type=int,
            help="Creates User objects",
            required=False,
        )
        parser.add_argument(
            "--ingredient",
            nargs=1,
            type=int,
            help="Creates Ingredient objects",
            required=False,
        )
        parser.add_argument(
            "--recipetag",
            nargs=1,
            type=int,
            help="Creates RecipeTag objects",
            required=False,
        )
        parser.add_argument(
            "--recipe",
            nargs=1,
            type=int,
            help="Creates Recipe objects",
            required=False,
        )
        parser.add_argument(
            "--cart",
            nargs=1,
            type=int,
            help="Creates Cart objects",
            required=False,
        )
        parser.add_argument(
            "--favorite",
            nargs=1,
            type=int,
            help="Creates Favorite objects",
            required=False,
        )
        parser.add_argument(
            "--subscription",
            nargs=1,
            type=int,
            help="Creates Subscription objects",
            required=False,
        )

    def handle(self, *args, **options):  # noqa

        optional_arguments = 0

        for item in list(OPTIONS_AND_FUNCTIONS):
            if options[item]:
                optional_arguments += 1
                with factory.Faker.override_default_locale("ru_RU"):
                    OPTIONS_AND_FUNCTIONS[item](options[item][0])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"{options[item][0]} {item} created successfully"
                        )
                    )

        if optional_arguments == 0:
            try:

                with factory.Faker.override_default_locale("ru_RU"):
                    UserFactory.create_batch(10)

                    IngredientFactory.create_batch(100)

                    RecipeTagFactory.create_batch(4)

                    for _ in range(100):
                        num_tags = random.randint(1, 2)
                        num_ingr = random.randint(3, 6)
                        RecipeFactory.create(
                            tags=num_tags, ingredients=num_ingr
                        )

                    CartFactory.create_batch(50)

                    FavoriteFactory.create_batch(50)

                    SubscriptionFactory.create_batch(50)

                self.stdout.write(
                    self.style.SUCCESS("The database is filled with test data")
                )
            except Exception:
                self.stdout.write(
                    self.style.ERROR(
                        "The database is already filled with standard test "
                        "data. To top up individual tables, use the arguments."
                    )
                )
