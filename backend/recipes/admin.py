from django.contrib import admin
from django.contrib.admin import register

from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientItem,
    Recipe,
    RecipeTag,
)


class IngridientItemAdmin(admin.StackedInline):
    model = IngredientItem
    fk_name = "recipe"


@register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngridientItemAdmin]
    list_display = ["id", "name"]


@register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    pass


@register(Ingredient)
class IngridientAdmin(admin.ModelAdmin):
    pass


@register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass


@register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass
