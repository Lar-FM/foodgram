from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag


class RecipeIngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class RecipeTagsInLine(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'text', 'pub_date', 'author')
    search_fields = ('name', 'author')
    inlines = (RecipeIngredientsInLine, RecipeTagsInLine)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
