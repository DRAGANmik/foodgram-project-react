from datetime import datetime

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from recipes.filters import RecipeFilter
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
    IngredientItemSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeSerializerPost,
    RecipeTagSerialzier,
)


class ListDetailViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    pass


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
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

        disfavor = Favorite.objects.get(**serializer.validated_data)
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

        empty = Cart.objects.get(**serializer.validated_data)
        empty.delete()
        return Response(
            {"status": "Удалено из корзины"}, status=status.HTTP_204_NO_CONTENT
        )


class RecipeTagViewSet(ListDetailViewSet):
    queryset = RecipeTag.objects.distinct().order_by("id")
    serializer_class = RecipeTagSerialzier
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class IngredientItemViewSet(ModelViewSet):
    queryset = IngredientItem.objects.all()
    serializer_class = IngredientItemSerializer


def pdf_dw(request):

    # Create the HttpResponse object
    response = HttpResponse(content_type="application/pdf")

    # This line force a download
    response["Content-Disposition"] = 'attachment; filename="1.pdf"'

    # READ Optional GET param
    get_param = request.GET.get("name", "World")

    # Generate unique timestamp
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")

    p = canvas.Canvas(response)

    # Write content on the PDF
    p.drawString(100, 500, "Hello " + get_param + " (Dynamic PDF) - " + ts)

    my_image = ImageReader("https://www.google.com/images/srpr/logo11w.png")

    p.drawImage(my_image, 5, 50, mask="auto")
    # Close the PDF object.
    p.showPage()
    p.save()

    # Show the result to the user
    return response
