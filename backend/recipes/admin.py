from django.contrib import admin
from django.contrib.admin import register
from django.utils.html import format_html

from recipes.models import Cart, Favorite, Ingredient, Recipe, RecipeTag


class IngridientItemAdmin(admin.StackedInline):
    model = Recipe.ingredients.through
    extra = 0


@register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngridientItemAdmin]
    list_display = [
        "id",
        "author",
        "name",
        "cooking_time",
        "image_list_preview",
    ]
    exclude = ["ingredients"]
    search_fields = ("name", "author__username")
    list_filter = ("name", "cooking_time", "author")
    filter_horizontal = ("tags",)

    readonly_fields = ("image_change_preview",)

    def image_change_preview(self, obj):
        if obj.image:
            url = obj.image.url
            return format_html(
                '<img src="{}" width="600" height="300" style="'
                "border: 2px solid grey;"
                'border-radius:50px;" />'.format(url)
            )
        return "Превью"

    image_change_preview.short_description = "Превью"

    def image_list_preview(self, obj):
        if obj.image:

            url = obj.image.url
            return format_html(
                '<img src="{}" width="100" height="50" style="'
                "border: 1px solid grey;"
                'border-radius:10px;" />'.format(url)
            )
        return "Картинка"

    image_list_preview.short_description = "Картинка"


@register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
    ]
    search_fields = [
        "name",
        "slug",
    ]
    prepopulated_fields = {
        "slug": ["name"],
    }


@register(Ingredient)
class IngridientAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "measurement_unit",
    ]
    search_fields = [
        "name",
        "measurement_unit",
    ]


@register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        "recipe",
        "user",
    ]
    search_fields = [
        "recipe__name",
        "user__username",
    ]
    list_filter = [
        "recipe",
        "user",
    ]


@register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = [
        "recipe",
        "user",
    ]
    search_fields = [
        "recipe__name",
        "user__username",
    ]
    list_filter = [
        "recipe",
        "user",
    ]
