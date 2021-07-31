from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import (
    IngredientViewSet,
    PDFCartAPIView,
    RecipeTagViewSet,
    RecipeViewSet,
)

router = DefaultRouter()
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("tags", RecipeTagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")


urlpatterns = [
    path("recipes/download_shopping_cart/", PDFCartAPIView.as_view()),
    path("", include(router.urls)),
]
