from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from recipes.tests.factories import (
    IngredientFactory,
    RecipeFactory,
    RecipeTagFactory,
)

from .factories import SubscriptionFactory, UserFactory

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
        UserFactory.create_batch(5)
        SubscriptionFactory.create_batch(5)
        IngredientFactory.create_batch(10)
        RecipeTagFactory.create_batch(2)
        RecipeFactory.create_batch(20)

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
        user = UserFactory()
        author = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        SubscriptionFactory(subscriber=user, author=author)
        RecipeFactory(author=author)
        response_data = client.get(
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

    def test_users_register(self):
        client = ViewUsersTests.unauthorized_client
        user_count = User.objects.count()
        user = {
            "username": "test",
            "first_name": "test",
            "last_name": "test",
            "email": "test@test.test",
            "password": "test_password",
        }
        response = client.post(
            path=self.path_users,
            data=user,
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(User.objects.count(), user_count + 1)

        last_user = User.objects.last()
        self.assertEqual(last_user.username, "test")
        self.assertEqual(last_user.first_name, "test")
        self.assertEqual(last_user.last_name, "test")
        self.assertEqual(last_user.email, "test@test.test")
        self.assertFalse(last_user.password is None)

        response = client.post(
            path=self.path_users,
            data=user,
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_users_login(self):
        client = ViewUsersTests.unauthorized_client
        user = UserFactory()

        self.assertTrue(
            client.login(username=user.email, password="Test1!1Test")
        )

    def test_users_change_password(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        password_dict = {
            "current_password": "Test1!1Test",
            "new_password": "Test1!1Test11",
        }

        response = client.post(
            path=self.path_users + "set_password/",
            data=password_dict,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            client.login(username=user.email, password="Test1!1Test11")
        )
