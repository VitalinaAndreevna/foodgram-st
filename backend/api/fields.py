from base64 import b64decode

from django.core.files.base import ContentFile
from rest_framework import serializers


class ImageFieldFromBase64(serializers.ImageField):
    """Кастомное поле для обработки изображений в формате base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_info, encoded_img = data.split(';base64,')
            extension = format_info.split('/')[-1]
            data = ContentFile(b64decode(encoded_img), name=f"upload.{extension}")
        return super().to_internal_value(data)
