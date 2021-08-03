from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from recipes.filters import IngredientFilter, RecipeFilter
from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientItem,
    Recipe,
    RecipeTag,
)
from recipes.serializers import (
    CartSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeSerializerPost,
    RecipeTagSerialzier,
)


class ListDetailViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    pass


class RecipeViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_in_shopping_cart = self.request.query_params.get(
            "is_in_shopping_cart"
        )
        is_favorited = self.request.query_params.get("is_favorited")
        cart = Cart.objects.filter(user=self.request.user.id)
        favorite = Favorite.objects.filter(user=self.request.user.id)

        if is_in_shopping_cart == "true":
            queryset = queryset.filter(cart__in=cart)
        elif is_in_shopping_cart == "false":
            queryset = queryset.exclude(cart__in=cart)
        if is_favorited == "true":
            queryset = queryset.filter(favorite__in=favorite)
        elif is_favorited == "false":
            queryset = queryset.exclude(favorite__in=favorite)
        return queryset.all()

    def get_serializer_class(self):
        if self.action != "list" and self.action != "retrieve":
            return RecipeSerializerPost
        return RecipeSerializer

    @action(
        detail=True,
        methods=["GET", "DELETE"],
        url_path="favorite",
        url_name="favorite",
        permission_classes=[permissions.IsAuthenticated],
    )
    def favorite(self, request, pk):
        serializer = FavoriteSerializer(
            data={"recipe": pk, "user": request.user.id}
        )
        if request.method == "GET":
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"status": "Добавлено в избранное"},
                status=status.HTTP_201_CREATED,
            )

        serializer.is_valid(raise_exception=True)
        if not Favorite.objects.filter(**serializer.validated_data):
            raise serializers.ValidationError(
                {
                    "message": "Извините, но нельзя удалить из избранного,"
                    " если вы это не добавили."
                }
            )

        disfavor = get_object_or_404(Favorite, **serializer.validated_data)
        disfavor.delete()
        return Response(
            {"status": "Удалено из избранного"},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=True,
        methods=["GET", "DELETE"],
        url_path="shopping_cart",
        url_name="shopping_cart",
        permission_classes=[permissions.IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        serializer = CartSerializer(
            data={"recipe": pk, "user": request.user.id}
        )
        if request.method == "GET":
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"status": "Добавлено в корзину"},
                status=status.HTTP_201_CREATED,
            )

        serializer.is_valid(raise_exception=True)
        if not Cart.objects.filter(**serializer.validated_data):
            raise serializers.ValidationError(
                {
                    "message": "Извините, но нельзя удалить из корзины,"
                    " если вы это не добавили."
                }
            )

        empty = get_object_or_404(Cart, **serializer.validated_data)
        empty.delete()
        return Response(
            {"status": "Удалено из корзины"}, status=status.HTTP_204_NO_CONTENT
        )


class RecipeTagViewSet(ListDetailViewSet):
    queryset = RecipeTag.objects.distinct().order_by("id")
    serializer_class = RecipeTagSerialzier
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class PDFCartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        ingredients_dict = {}
        ingredients = IngredientItem.objects.filter(recipe__cart__user=user)

        for item in ingredients:
            name = item.ingredient.name
            measurement_unit = item.ingredient.measurement_unit
            amount = item.amount
            if name not in ingredients_dict:
                ingredients_dict[name] = {
                    "measurement_unit": measurement_unit,
                    "amount": amount,
                }
            else:
                ingredients_dict[name][amount] += amount
        pdfmetrics.registerFont(
            TTFont("DejaVuSerif", "DejaVuSerif.ttf", "UTF-8")
        )
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            "attachment; " 'filename="shopping_list.pdf"'
        )
        page = canvas.Canvas(response)
        page.setFont("DejaVuSerif", size=20)
        page.drawString(180, 750, "Список ингредиентов:")
        page.setFont("DejaVuSerif", size=16)
        height = 700
        i = 1

        for name, data in ingredients_dict.items():
            page.drawString(
                50,
                height,
                (
                    f'{i}) { name } - {data["amount"]} '
                    f'({data["measurement_unit"]}.)'
                ),
            )
            height -= 25
            i += 1

        page.showPage()
        page.save()

        Cart.objects.filter(user=user).delete()

        return response
