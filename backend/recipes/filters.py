from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from recipes.models import RecipeTag

User = get_user_model()


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=RecipeTag.objects.all(),
        to_field_name="slug",
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
