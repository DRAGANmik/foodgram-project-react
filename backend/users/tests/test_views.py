from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from recipes.factories import (
    IngredientFactory,
    IngredientItemFactory,
    RecipeFactory,
    RecipeTagFactory,
)
from recipes.models import Recipe
from users.factories import SubscriptionFactory, UserFactory

User = get_user_model()


class ViewUsersTests(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = UserFactory()
        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)
        cls.path_users = reverse("users-list")
        cls.path_ingredients = reverse("ingredients-list")

    def test_users_correct_fields_unauthorized(self):
        clinet = ViewUsersTests.unauthorized_client
        UserFactory.create_batch(10)

        response_data = clinet.get(ViewUsersTests.path_users).data

        self.assertTrue("next" in response_data)
        self.assertTrue("previous" in response_data)
        self.assertTrue("results" in response_data)

        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]
        results = response_data.get("results")[0]
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(field in results, msg=f"Нет поля {field}")

    def test_users_correct_fields_authorized(self):
        clinet = ViewUsersTests.authorized_client
        UserFactory.create_batch(10)

        response_data = clinet.get(ViewUsersTests.path_users).data

        self.assertTrue("next" in response_data)
        self.assertTrue("previous" in response_data)
        self.assertTrue("results" in response_data)

        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]
        results = response_data.get("results")[0]
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(field in results, msg=f"Нет поля {field}")

    def test_users_subscriptions_correct_fields(self):
        clinet = ViewUsersTests.authorized_client
        UserFactory.create_batch(5)
        SubscriptionFactory.create_batch(5)
        IngredientFactory.create_batch(10)
        RecipeTagFactory.create_batch(1)
        RecipeFactory.create_batch(2)
        IngredientItemFactory.create_batch(2)

        author = User.objects.get(id=7)
        recipe = Recipe.objects.get(id=1)
        recipe.author = author
        recipe.save()

        response_data = clinet.get(
            ViewUsersTests.path_users + "subscriptions/"
        ).data

        self.assertTrue("next" in response_data)
        self.assertTrue("previous" in response_data)
        self.assertTrue("results" in response_data)

        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        ]
        results = response_data.get("results")[0]
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(field in results, msg=f"Нет поля {field}")
        recipes = results["recipes"][0]

        recipes_fields = ["id", "name", "image", "cooking_time"]
        for field in recipes_fields:
            with self.subTest(field=field):
                self.assertTrue(
                    field in recipes, msg=f"Нет поля {field} в recipes"
                )
