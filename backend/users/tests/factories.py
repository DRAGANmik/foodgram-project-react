import factory
from django.contrib.auth import get_user_model
from faker import Faker

from users.models import Subscription

User = get_user_model()
fake = Faker(["ru-RU"])


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ["username"]

    username = factory.Sequence(lambda n: "user_%d" % (User.objects.count()))
    password = "Test1!1Test"
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.test")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):

        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    author = factory.Iterator(User.objects.all())
    subscriber = factory.SubFactory(UserFactory)
