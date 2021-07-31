from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()

User._meta.get_field("email")._unique = True
User._meta.get_field("email").blank = False
User._meta.get_field("email").null = False


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="author",
        verbose_name="Автор",
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriber",
        verbose_name="Подписчик",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ["id"]
        constraints = [
            UniqueConstraint(
                fields=["author", "subscriber"], name="unique_subscription"
            )
        ]

    def __str__(self) -> str:
        return self.author.username
