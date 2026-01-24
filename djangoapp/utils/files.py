import os
import uuid
from django.utils.timezone import now
"""
    Gera um caminho único e organizado para qualquer tipo de arquivo.
    Funciona para ImageField, FileField e VideoField.
"""
def get_file_path(instance, filename):
    # extrai a extensão original (ex: .jpg, .pdf, .mp4)
    ext = os.path.splitext(filename)[1].lower()
    
    # Gera um nome único via UUID
    new_filename = f"{uuid.uuid4()}{ext}"
    
    # Define a pasta base pelo nome do Model (ex: Product -> 'product')
    folder_name = instance.__class__.__name__.lower()
    
    # organiza por data, exemplo: product/2026/01/23/uuid.ext
    date_path = now().strftime("%Y/%m/%d")
    
    return os.path.join(folder_name, date_path, new_filename)
