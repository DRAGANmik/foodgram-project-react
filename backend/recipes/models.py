from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from recipes.slugify import slugify

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор"
    )
    ingredients = models.ManyToManyField(
        "Ingredient",
        through="IngredientItem",
        through_fields=("recipe", "ingredient"),
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField("RecipeTag", verbose_name="Теги")
    image = models.ImageField(upload_to="recipes/", verbose_name="Изображение")
    name = models.CharField(max_length=200, verbose_name="Название")
    text = models.TextField(verbose_name="Описание")
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления",
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-id"]

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    name = models.CharField(
        max_length=50, unique=True, verbose_name="Название"
    )
    color = ColorField(verbose_name="Цвет")
    slug = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50, unique=True, verbose_name="Название"
    )
    measurement_unit = models.CharField(
        max_length=5, verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "Игредиент"
        verbose_name_plural = "Игредиенты"
        ordering = ["id"]

    def __str__(self):
        return self.name


class IngredientItem(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1)], verbose_name="Количество"
    )

    class Meta:
        verbose_name = "Элемент рецепта"
        verbose_name_plural = "Элементы рецепта"
        ordering = ["id"]
        unique_together = (("recipe", "ingredient"),)

    def __str__(self):
        return self.ingredient.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite"
            )
        ]

    def __str__(self):
        return "Пользователь {} рецепт {}".format(
            self.user.username, self.recipe.name
        )


class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_cart"
            )
        ]

    def __str__(self):
        return "Пользователь {} рецепт {}".format(
            self.user.username, self.recipe.name
        )
