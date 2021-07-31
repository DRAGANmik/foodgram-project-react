from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from recipes.factories import (
    IngredientFactory,
    IngredientItemFactory,
    RecipeFactory,
    RecipeTagFactory,
)
from users.factories import UserFactory


class ViewRecipeTests(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = UserFactory()
        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)
        cls.path_recipes = reverse("recipes-list")
        cls.path_ingredients = reverse("ingredients-list")

    def test_recipe_correct_fileds_unauthorized(self):
        clinet = ViewRecipeTests.unauthorized_client
        IngredientFactory.create_batch(5)
        RecipeFactory.create_batch(5)

        response_data = clinet.get(ViewRecipeTests.path_recipes).data

        self.assertTrue("next" in response_data)
        self.assertTrue("previous" in response_data)
        self.assertTrue("results" in response_data)

        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]
        results = response_data.get("results")[0]
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(field in results, msg=f"Нет поля {field}")

    def test_recipe_correct_fileds_authorized(self):
        clinet = ViewRecipeTests.authorized_client
        IngredientFactory.create_batch(5)
        RecipeFactory.create_batch(5)

        response_data = clinet.get(ViewRecipeTests.path_recipes).data

        self.assertTrue("next" in response_data)
        self.assertTrue("previous" in response_data)
        self.assertTrue("results" in response_data)

        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]
        results = response_data.get("results")[0]
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(field in results, msg=f"Нет поля {field}")

    def test_recipe_nested_fields_unauthorized(self):
        clinet = ViewRecipeTests.unauthorized_client
        IngredientFactory.create_batch(1)
        RecipeTagFactory.create_batch(1)
        RecipeFactory.create_batch(1)
        IngredientItemFactory.create_batch(10)

        response_data = clinet.get(ViewRecipeTests.path_recipes).data
        results = response_data.get("results")[0]
        tags = results["tags"][0]
        author = results.get("author")
        ingredients = results["ingredients"][0]

        tags_fields = ["id", "name", "color", "slug"]
        for field in tags_fields:
            with self.subTest(field=field):
                self.assertTrue(field in tags, msg=f"Нет поля {field} в tags")

        author_fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]
        for field in author_fields:
            with self.subTest(field=field):
                self.assertTrue(
                    field in author, msg=f"Нет поля {field} в author"
                )

        ingredients_fields = [
            "id",
            "name",
            "measurement_unit",
            "amount",
        ]
        for field in ingredients_fields:
            with self.subTest(field=field):
                self.assertTrue(
                    field in ingredients, msg=f"Нет поля {field} в ingredients"
                )

    def test_recipe_nested_fields_authorized(self):
        clinet = ViewRecipeTests.authorized_client
        IngredientFactory.create_batch(1)
        RecipeTagFactory.create_batch(1)
        RecipeFactory.create_batch(1)
        IngredientItemFactory.create_batch(10)

        response_data = clinet.get(ViewRecipeTests.path_recipes).data
        results = response_data.get("results")[0]
        tags = results.get("tags")[0]
        author = results["author"]
        ingredients = results.get("ingredients")[0]

        tags_fields = ["id", "name", "color", "slug"]
        for field in tags_fields:
            with self.subTest(field=field):
                self.assertTrue(field in tags, msg=f"Нет поля {field} в tags")

        author_fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]
        for field in author_fields:
            with self.subTest(field=field):
                self.assertTrue(
                    field in author, msg=f"Нет поля {field} в author"
                )

        ingredients_fields = [
            "id",
            "name",
            "measurement_unit",
            "amount",
        ]
        for field in ingredients_fields:
            with self.subTest(field=field):
                self.assertTrue(
                    field in ingredients, msg=f"Нет поля {field} в ingredients"
                )

    def test_recipe_detail_fields_unauthorized(self):
        clinet = ViewRecipeTests.unauthorized_client
        IngredientFactory.create_batch(1)
        RecipeTagFactory.create_batch(1)
        RecipeFactory.create_batch(1)
        IngredientItemFactory.create_batch(10)

        response_data = clinet.get(ViewRecipeTests.path_recipes + "1/").data
        tags = response_data["tags"][0]
        author = response_data.get("author")
        ingredients = response_data["ingredients"][0]

        fields = [
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        ]
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(
                    field in response_data, msg=f"Нет поля {field}"
                )

        tags_fields = ["id", "name", "color", "slug"]
        for field in tags_fields:
            with self.subTest(field=field):
                self.assertTrue(field in tags, msg=f"Нет поля {field} в tags")

        author_fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]
        for field in author_fields:
            with self.subTest(field=field):
                self.assertTrue(
                    field in author, msg=f"Нет поля {field} в author"
                )

        ingredients_fields = [
            "id",
            "name",
            "measurement_unit",
            "amount",
        ]
        for field in ingredients_fields:
            with self.subTest(field=field):
                self.assertTrue(
                    field in ingredients, msg=f"Нет поля {field} в ingredients"
                )

    def test_ingredients_correct_fileds_unauthorized(self):
        clinet = ViewRecipeTests.unauthorized_client
        IngredientFactory.create_batch(50)

        response_data = clinet.get(ViewRecipeTests.path_ingredients).data

        self.assertFalse("next" in response_data)
        self.assertFalse("previous" in response_data)
        self.assertFalse("results" in response_data)

        fields = [
            "id",
            "name",
            "measurement_unit",
        ]
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(
                    field in response_data[0], msg=f"Нет поля {field}"
                )

    def test_ingredients_correct_fileds_authorized(self):
        clinet = ViewRecipeTests.authorized_client
        IngredientFactory.create_batch(10)

        response_data = clinet.get(ViewRecipeTests.path_ingredients).data
        self.assertFalse("next" in response_data)
        self.assertFalse("previous" in response_data)
        self.assertFalse("results" in response_data)

        fields = [
            "id",
            "name",
            "measurement_unit",
        ]
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(
                    field in response_data[0], msg=f"Нет поля {field}"
                )

    def test_ingredients_correct_fileds_detail(self):
        clinet = ViewRecipeTests.unauthorized_client
        IngredientFactory.create_batch(10)

        response_data = clinet.get(
            ViewRecipeTests.path_ingredients + "1/"
        ).data
        self.assertFalse("next" in response_data)
        self.assertFalse("previous" in response_data)
        self.assertFalse("results" in response_data)

        fields = [
            "id",
            "name",
            "measurement_unit",
        ]
        for field in fields:
            with self.subTest(field=field):
                self.assertTrue(
                    field in response_data, msg=f"Нет поля {field}"
                )
