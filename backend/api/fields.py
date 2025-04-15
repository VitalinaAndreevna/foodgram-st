import base64
from django.core.files.base import ContentFile
from rest_framework import serializers

from foodgram.constants import BASE62_ALPHABET, BASE62_DIVIDER


class Base64ImageField(serializers.ImageField):
    """Поле для загрузки изображений в формате base64."""
    
    def to_internal_value(self, data):
        """Преобразует base64 строку в файл изображения."""
        if not isinstance(data, str) or not data.startswith('data:image'):
            return super().to_internal_value(data)
            
        try:
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            decoded_file = base64.b64decode(imgstr)
            return ContentFile(decoded_file, name=f'temp.{ext}')
        except (ValueError, AttributeError) as error:
            raise serializers.ValidationError("Некорректный формат base64 изображения") from error


class Base62Converter:
    """Конвертер для преобразования чисел в base62 и обратно."""
    
    @staticmethod
    def to_base62(num):
        """Конвертирует число в base62 строку."""
        if not isinstance(num, int) or num < 0:
            raise ValueError("Требуется положительное целое число")
            
        if num == 0:
            return BASE62_ALPHABET[0]
            
        chars = []
        while num > 0:
            chars.append(BASE62_ALPHABET[num % BASE62_DIVIDER])
            num = num // BASE62_DIVIDER
            
        return ''.join(reversed(chars))

    @staticmethod
    def from_base62(short_code):
        """Конвертирует base62 строку в число."""
        if not isinstance(short_code, str) or not short_code:
            raise ValueError("Требуется непустая строка")
            
        num = 0
        for char in short_code:
            if char not in BASE62_ALPHABET:
                raise ValueError(f"Недопустимый символ: {char}")
            num = num * BASE62_DIVIDER + BASE62_ALPHABET.index(char)
        return num
    