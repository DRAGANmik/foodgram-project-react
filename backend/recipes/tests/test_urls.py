from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from users.tests.factories import UserFactory

from .factories import IngredientFactory, RecipeFactory, RecipeTagFactory


class UrlRecipeTests(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        UserFactory.create_batch(5)
        IngredientFactory.create_batch(10)
        RecipeTagFactory.create_batch(2)
        RecipeFactory.create_batch(2)

        cls.user = UserFactory()
        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)
        cls.path_recipes = reverse("recipes-list")
        cls.path_ingredients = reverse("ingredients-list")

    def test_urls_smoke_unauthorized(self):
        clinet = UrlRecipeTests.unauthorized_client

        response = clinet.get(reverse("recipes-list"))
        self.assertEqual(response.status_code, 200)

        response = clinet.get(reverse("recipes-list") + "1/")
        self.assertEqual(response.status_code, 200)

        response = clinet.get(reverse("ingredients-list"))
        self.assertEqual(response.status_code, 200)

        response = clinet.get(reverse("ingredients-list") + "1/")
        self.assertEqual(response.status_code, 200)
