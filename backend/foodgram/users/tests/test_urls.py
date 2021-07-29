from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from recipes.factories import (
    IngredientFactory,
    IngredientItemFactory,
    RecipeFactory,
    RecipeTagFactory,
)
from users.factories import UserFactory


class UrlUsersTests(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = UserFactory()
        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)
        cls.path_recipes = reverse("recipes-list")
        cls.path_ingredients = reverse("ingredients-list")

    def test_urls_smoke_unauthorized(self):
        clinet = UrlUsersTests.unauthorized_client
        IngredientFactory.create_batch(1)
        RecipeTagFactory.create_batch(1)
        RecipeFactory.create_batch(1)
        IngredientItemFactory.create_batch(10)

        response = clinet.get(reverse("users-list"))
        self.assertEqual(response.status_code, 200)

        response = clinet.get(reverse("users-list") + "1/")
        self.assertEqual(response.status_code, 200)

        response = clinet.get(reverse("users-list") + "subscriptions/")
        self.assertEqual(response.status_code, 401)

        response = clinet.get(reverse("users-list") + "me/")
        self.assertEqual(response.status_code, 401)
