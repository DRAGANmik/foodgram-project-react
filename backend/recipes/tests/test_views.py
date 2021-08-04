import tempfile

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientItem,
    Recipe,
    RecipeTag,
)
from users.tests.factories import UserFactory

from .factories import IngredientFactory, RecipeFactory, RecipeTagFactory

TEST_IMAGE = """
iVBORw0KGgoAAAANSUhEUgA
AAAoAAAAKCAYAAACNMs+9AAAABmJLR0QA/wD/AP+gvaeTAAAAB3RJ
TUUH1ggDCwMADQ4NnwAAAFVJREFUGJWNkMEJADEIBEcbSDkXUnfSg
nBVeZ8LSAjiwjyEQXSFEIcHGP9oAi+H0Bymgx9MhxbFdZE2a0s9kT
Zdw01ZhhYkABSwgmf1Z6r1SNyfFf4BZ+ZUExcNUQUAAAAASUVORK5
CYII=
""".strip()


class ViewRecipeTests(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        UserFactory.create_batch(5)
        IngredientFactory.create_batch(20)
        RecipeTagFactory.create_batch(4)
        RecipeFactory.create_batch(10)

        cls.user = UserFactory()
        cls.unauthorized_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)
        cls.path_recipes = reverse("recipes-list")
        cls.path_ingredients = reverse("ingredients-list")

    def test_recipe_correct_fileds_unauthorized(self):
        clinet = ViewRecipeTests.unauthorized_client
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

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_recipes_create(self):
        image = TEST_IMAGE
        client = ViewRecipeTests.authorized_client
        recipe_count = Recipe.objects.count()
        recipe_data = {
            "name": "test",
            "tags": [1],
            "ingredients": [{"id": 1, "amount": 55}],
            "image": image,
            "cooking_time": 355,
            "text": "text",
        }
        response = client.post(
            path=self.path_recipes,
            data=recipe_data,
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Recipe.objects.count(), recipe_count + 1)

        last_recipe = Recipe.objects.get(name="test")
        tag = RecipeTag.objects.get(recipe=last_recipe)
        ingredient = Ingredient.objects.get(id=1)
        item = IngredientItem.objects.get(
            ingredient=ingredient, recipe=last_recipe
        )

        self.assertEqual(last_recipe.name, "test")
        self.assertTrue(tag in last_recipe.tags.all())
        self.assertTrue(ingredient in last_recipe.ingredients.all())
        self.assertEqual(item.amount, 55)
        self.assertEqual(last_recipe.cooking_time, 355)
        self.assertEqual(last_recipe.text, "text")
        self.assertFalse(last_recipe.image is None)

    def test_recipes_delete(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        recipe = RecipeFactory(author=user)
        response = client.delete(
            path=self.path_recipes + f"{recipe.id}/",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

    def test_recipes_update(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        recipe = RecipeFactory(author=user)
        image = TEST_IMAGE
        recipe_data_patch = {
            "name": "test",
            "tags": [1],
            "ingredients": [{"id": 1, "amount": 55}],
            "image": image,
            "cooking_time": 355,
            "text": "text",
        }

        response = client.put(
            path=self.path_recipes + f"{recipe.id}/",
            data=recipe_data_patch,
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        last_recipe = Recipe.objects.get(name="test")
        tag = RecipeTag.objects.get(recipe=last_recipe)
        ingredient = Ingredient.objects.get(id=1)
        item = IngredientItem.objects.get(
            ingredient=ingredient, recipe=last_recipe
        )

        self.assertEqual(last_recipe.name, "test")
        self.assertTrue(tag in last_recipe.tags.all())
        self.assertTrue(ingredient in last_recipe.ingredients.all())
        self.assertEqual(item.amount, 55)
        self.assertEqual(last_recipe.cooking_time, 355)
        self.assertEqual(last_recipe.text, "text")
        self.assertFalse(last_recipe.image is None)

        recipe_data_upd = {
            "name": "test_upd",
            "tags": [1, 2],
            "ingredients": [{"id": 3, "amount": 65}, {"id": 4, "amount": 100}],
            "cooking_time": 77,
            "text": "text_upd",
            "image": image,
        }

        response = client.put(
            path=self.path_recipes + f"{recipe.id}/",
            data=recipe_data_upd,
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        last_recipe = Recipe.objects.get(name="test_upd")
        tag = RecipeTag.objects.filter(recipe=last_recipe)
        item = IngredientItem.objects.filter(recipe=last_recipe)

        self.assertEqual(last_recipe.name, "test_upd")
        self.assertEqual(tag[0].id, 1)
        self.assertEqual(tag[1].id, 2)
        self.assertEqual(last_recipe.tags.count(), 2)
        self.assertEqual(item[0].ingredient.id, 3)
        self.assertEqual(item[1].ingredient.id, 4)
        self.assertEqual(last_recipe.ingredients.count(), 2)
        self.assertEqual(item[0].amount, 65)
        self.assertEqual(item[1].amount, 100)
        self.assertEqual(last_recipe.cooking_time, 77)
        self.assertEqual(last_recipe.text, "text_upd")
        self.assertFalse(last_recipe.image is None)

        recipe_data_upd = {
            "name": "test_upd",
            "tags": [tag[1].id],
            "ingredients": [
                {"id": item[0].id, "amount": 65},
                {"id": item[1].id, "amount": 100},
                {"id": 1, "amount": 150},
            ],
            "cooking_time": 77,
            "text": "text_upd",
            "image": image,
        }

        response = client.put(
            path=self.path_recipes + f"{recipe.id}/",
            data=recipe_data_upd,
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        last_recipe = Recipe.objects.get(name="test_upd")
        tag = RecipeTag.objects.filter(recipe=last_recipe)
        item = IngredientItem.objects.filter(recipe=last_recipe)

        self.assertEqual(last_recipe.name, "test_upd")
        self.assertEqual(tag[0].id, 2)
        self.assertEqual(last_recipe.tags.count(), 1)
        self.assertEqual(item[0].ingredient.id, 3)
        self.assertEqual(item[1].ingredient.id, 4)
        self.assertEqual(item[2].ingredient.id, 1)
        self.assertEqual(last_recipe.ingredients.count(), 3)
        self.assertEqual(item[0].amount, 65)
        self.assertEqual(item[1].amount, 100)
        self.assertEqual(item[2].amount, 150)
        self.assertEqual(last_recipe.cooking_time, 77)
        self.assertEqual(last_recipe.text, "text_upd")
        self.assertFalse(last_recipe.image is None)

    def test_recipes_cart(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        count_cart = Cart.objects.filter(user=user).count()
        response = client.get(
            path=self.path_recipes + "1/shopping_cart/",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            Cart.objects.filter(user=user).count(), count_cart + 1
        )
        response = client.get(
            path=self.path_recipes + "1/shopping_cart/",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            Cart.objects.filter(user=user).count(), count_cart + 1
        )

        response = client.delete(
            path=self.path_recipes + "1/shopping_cart/",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertEqual(Cart.objects.filter(user=user).count(), count_cart)
        response = client.delete(
            path=self.path_recipes + "1/shopping_cart/",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(Cart.objects.filter(user=user).count(), count_cart)

    def test_recipes_favorite(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        count_favorite = Favorite.objects.filter(user=user).count()
        response = client.get(
            path=self.path_recipes + "1/favorite/",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            Favorite.objects.filter(user=user).count(), count_favorite + 1
        )
        response = client.get(
            path=self.path_recipes + "1/favorite/",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            Favorite.objects.filter(user=user).count(), count_favorite + 1
        )

        response = client.delete(
            path=self.path_recipes + "1/favorite/",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertEqual(
            Favorite.objects.filter(user=user).count(), count_favorite
        )
        response = client.delete(
            path=self.path_recipes + "1/favorite/",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            Favorite.objects.filter(user=user).count(), count_favorite
        )
