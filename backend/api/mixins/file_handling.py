import base64
import csv
import os
import uuid
from io import StringIO

from django.core.files.base import ContentFile
from django.http import HttpResponse
from fpdf import FPDF


class FileGenerationMixin:
    """Миксин для генерации файлов (TXT, CSV, PDF)"""
    
    @staticmethod
    def generate_txt_file(ingredients):
        content = "\n".join(
            f"{i['name']} ({i['measurement_unit']}) — {i['amount']}"
            for i in ingredients
        )
        response = HttpResponse(content, content_type="text/plain")
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
        return response

    @staticmethod
    def generate_csv_file(ingredients):
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Ингредиент', 'Количество', 'Единица измерения'])
        for ingredient in ingredients:
            writer.writerow([ingredient['name'], ingredient['amount'], ingredient['measurement_unit']])
        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.csv"'
        return response

    @staticmethod
    def generate_pdf_file(ingredients):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Список покупок", ln=True, align='C')
        for ingredient in ingredients:
            pdf.cell(200, 10, txt=f"{ingredient['name']} ({ingredient['measurement_unit']}) — {ingredient['amount']}", ln=True)
        response = HttpResponse(pdf.output(dest='S').encode('latin1'), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.pdf"'
        return response


class AvatarHandlingMixin:
    """Миксин для обработки аватаров пользователей"""
    
    @staticmethod
    def process_avatar_upload(user, avatar_data):
        if user.avatar:
            user.avatar.delete()
        
        format, imgstr = avatar_data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f"{uuid.uuid4()}.{ext}")
        user.avatar.save(data.name, data, save=True)
        