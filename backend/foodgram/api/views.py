from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User
from .filters import IngredientFilter, RecipeFilter
from .pagination import PageLimitPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (
    CreateRecipeSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    ShowSubscriptionsSerializer,
    SubscriptionSerializer,
    TagSerializer,
)


class SubscribeView(APIView):
    """ Операция подписки/отписки. """

    permission_classes = [IsAuthenticated, ]

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'author': id
        }
        serializer = SubscriptionSerializer(
            data=data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)
        if Subscription.objects.filter(
                user=request.user, author=author
        ).exists():
            subscription = get_object_or_404(
                Subscription, user=request.user, author=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShowSubscriptionsView(ListAPIView):
    """ Вью Отображение подписок """

    permission_classes = [IsAuthenticated, ]
    pagination_class = PageLimitPagination

    def get(self, request):
        user = request.user
        queryset = User.objects.filter(author__user=user)
        page = self.paginate_queryset(queryset)
        serializer = ShowSubscriptionsSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ Вьюсет ингредиентов """

    permission_classes = [AllowAny, ]
    pagination_class = None
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = [IngredientFilter, ]
    search_fields = ['^name', ]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ Вьюсет тегов """

    permission_classes = [AllowAny, ]
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """ Вьюсет CRUD рецептов """

    permission_classes = [IsAuthorOrAdminOrReadOnly, ]
    pagination_class = PageLimitPagination
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context


class FavoriteView(APIView):
    """ Вью избранного рецепта """

    permission_classes = [IsAuthenticated, ]
    pagination_class = PageLimitPagination

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        if not Favorite.objects.filter(
                user=request.user, recipe__id=id).exists():
            serializer = FavoriteSerializer(
                data=data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            Favorite.objects.filter(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartView(APIView):
    """ Вью корзины. """

    permission_classes = [IsAuthenticated, ]

    def post(self, request, id):
        data = {
            'user': request.user.id,
            'recipe': id
        }
        recipe = get_object_or_404(Recipe, id=id)
        if not ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
        ).exists():
            serializer = ShoppingCartSerializer(
                data=data, context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        if ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
        ).exists():
            ShoppingCart.objects.filter(
                user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def download_shopping_cart(request):
    ingredient_list = generate_ingridient_list(request.user)
    file = 'shopping_list'
    response = HttpResponse(ingredient_list, 'Content-Type: application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file}.pdf"'
    return response


def generate_ingridient_list(user):
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping_cart__user=user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(amount=Sum('amount'))
    ingredient_list = ', '.join([
        f"{ingredient['ingredient__name']} - {ingredient['amount']} "
        f"{ingredient['ingredient__measurement_unit']}"
        for ingredient in ingredients
    ])
    ingredient_list = f"Cписок покупок:\n{ingredient_list}"
    return ingredient_list
