from django.apps import AppConfig


class RecipeModuleConfig(AppConfig):
    name = 'recipes'
    verbose_name = 'Модуль рецептов'
    default_auto_field = 'django.db.models.BigAutoField'
