import factory
from django.contrib.auth import get_user_model
from faker import Faker

from users.models import Subscription

User = get_user_model()
fake = Faker(["ru-RU"])


# @factory.django.mute_signals(signals.post_save)
class UserFactory(factory.django.DjangoModelFactory):
    """Please review factory_boy docs why decoratory is required here."""

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
        """Override the default ``_create`` with our custom call.

        The method has been taken from factory_boy manual. Without it
        password for users is being created without HASH and doesn't work
        right.
        """

        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class SubscriptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Subscription

    author = factory.SubFactory(UserFactory)
    subscriber = factory.Iterator(User.objects.all())
