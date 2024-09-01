import short_url
from djoser.views import UserViewSet
from rest_framework import status, viewsets, exceptions, filters
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, redirect
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.decorators import action, api_view
from django.db.models import Sum

from .serializers import UserSerializer
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredients,
    Favorite,
    ShoppingCart,
)
from users.models import Follow
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeCreateUpdateSerializer,
    SubscriptionSerializer,
    ShortRecipeSerializer,
    AvatarSerializer,
)
from api.permissions import IsAdminAuthorOrReadOnly
from api.filters import RecipeFilter


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queruset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(
        detail=False,
        methods=('put', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar',
        url_name='avatar',
    )
    def avatar(self, request):
        """Добавление и удаление аватарок."""
        user = request.user
        if request.method == 'PUT':
            if not request.data:
                raise exceptions.ValidationError('Нужно добавить фото')
            serializer = AvatarSerializer(
                user, data=request.data, partial=True
            )
            if serializer.is_valid():
                if 'avatar' in request.data:
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
        obj_user = get_object_or_404(User, id=user.id)
        obj_user.avatar = None
        obj_user.save(update_fields=['avatar'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('get',),
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        obj_user = get_object_or_404(User, id=request.user.id)
        serializer = UserSerializer(obj_user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = self.request.user
        queryset = user.follower.all()
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete'),
    )
    def subscribe(self, request, id=None):
        """Подписка"""
        user = self.request.user
        author = get_object_or_404(User, pk=id)

        if user == author:
            return Response(
                {'errors': 'Подписаться или отписаться от себя нельзя'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if self.request.method == 'POST':
            if Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Уже есть подписка'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            queryset = Follow.objects.create(author=author, user=user)
            serializer = SubscriptionSerializer(
                queryset, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not Follow.objects.filter(
            user=user, author=author
        ).exists():
            return Response(
                {'errors': 'Уже отписаны'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = get_object_or_404(
            Follow, user=user, author=author
        )
        subscription.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer

        return RecipeSerializer

    def get_serializer_context(self):
        """Метод для передачи контекста. """

        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def add(self, model, user, pk):
        """Добавление рецепта"""
        recipe = get_object_or_404(Recipe, pk=pk)
        relation = model.objects.filter(user=user, recipe=recipe)
        if relation.exists():
            return Response(
                {'errors': 'Нельзя повторно добавить рецепт'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_relation(self, model, user, pk):
        """Удаление рецепта из списка пользователя."""
        recipe = get_object_or_404(Recipe, pk=pk)
        relation = model.objects.filter(user=user, recipe=recipe)
        if not relation.exists():
            return Response(
                {'errors': 'Нельзя повторно удалить рецепт'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='favorite',
        url_name='favorite',
    )
    def favorite(self, request, pk=None):
        """Добавление и удаление рецептов из избранного."""
        user = request.user
        if request.method == 'POST':
            return self.add(Favorite, user, pk)
        return self.delete_relation(Favorite, user, pk)

    @action(
        detail=True,
        methods=('post', 'delete'),
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        """Добавление и удаление рецептов из списока покупок."""
        user = request.user
        if request.method == 'POST':
            return self.add(ShoppingCart, user, pk)
        return self.delete_relation(ShoppingCart, user, pk)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        buy = (
            RecipeIngredients.objects.filter(recipe__in=recipes)
            .values('ingredient')
            .annotate(amount=Sum('amount'))
        )

        purchased = [
            'Список покупок:',
        ]
        for item in buy:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            purchased.append(
                f'{ingredient.name}: {amount}, '
                f'{ingredient.measurement_unit}'
            )
        purchased_in_file = '\n'.join(purchased)

        response = HttpResponse(purchased_in_file, content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename=shopping-list.txt'

        return response


@api_view(['GET'])
def redirect_view(request, pk=None):
    host_url = f'{str(request.scheme)}://{str(request.get_host())}'
    if pk:
        my_short_url = (
            f'{host_url}/s/{short_url.encode_url(pk)}'
        )
        return Response(
            {'short-link': my_short_url},
            status=status.HTTP_200_OK
        )
    pk_recipe = short_url.decode_url(str(request.path)[3:])
    return redirect(f'{host_url}/recipes/{pk_recipe}/')
