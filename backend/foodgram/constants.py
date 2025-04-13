# Ограничения по длине строк
INGREDIENT_NAME_MAX_LENGTH = 128
MEASUREMENT_UNIT_MAX_LENGTH = 64
RECIPE_TITLE_MAX_LENGTH = 256
USER_FIRST_NAME_MAX_LENGTH = 150
USER_LAST_NAME_MAX_LENGTH = 150

# Минимальные значения
MINIMUM_COOK_TIME = 1  # в минутах
MINIMUM_INGREDIENT_AMOUNT = 1  # в условных единицах

# Алфавит и делитель для base62 кодирования
BASE62_CHARS = (
    "0123456789abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)
BASE62_BASE = len(BASE62_CHARS)
