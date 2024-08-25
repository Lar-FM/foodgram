from django_filters import ModelMultipleChoiceFilter
from django_filters.rest_framework import FilterSet, filters
from django.contrib.auth import get_user_model

from recipes.models import Recipe, Tag


User = get_user_model()


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method="favorited_method")
    is_in_shopping_cart = filters.BooleanFilter(
        method="in_shopping_cart_method"
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.all(),
    )

    def favorited_method(self, queryset, name, value):
        if value == 1:
            user = self.request.user
            return queryset.filter(favorite__user_id=user.id)
        return queryset

    def in_shopping_cart_method(self, queryset, name, value):
        if value == 1:
            user = self.request.user
            return queryset.filter(shopping_list__user_id=user.id)
        return queryset

    class Meta:
        model = Recipe
        fields = ("author", "tags")
