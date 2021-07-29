from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import (
    IngredientItemViewSet,
    IngredientViewSet,
    RecipeTagViewSet,
    RecipeViewSet,
    pdf_dw,
)

router = DefaultRouter()
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", RecipeTagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("igredientsitem", IngredientItemViewSet, basename="ingr")

urlpatterns = [
    path("recipes/download_shopping_cart/", pdf_dw),
    path("", include(router.urls)),
]
