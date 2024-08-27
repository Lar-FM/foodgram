from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    TagViewSet,
    CustomUserViewSet,
    IngredientViewSet,
    RecipeViewSet,
    redirect_view,
)


router = DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/<int:pk>/get-link/', view=redirect_view, name='short_url_view'
    ),
    path('', include(router.urls)),
]
