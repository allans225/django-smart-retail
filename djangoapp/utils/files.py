import os
import uuid
from django.utils.timezone import now

def delete_file_pre_save(sender, instance, field_name):
    """
    Função Genérica para deletar a imagem antiga do sistema de arquivos
    quando a instância é atualizada com um novo arquivo.
    """
    if not instance.pk:
        return False  # Criação: não tem imagem antiga

    try:
        # OTIMIZAÇÃO: Usa .only() para não carregar a linha inteira do banco 
        # (evita puxar textos longos ou relacionamentos desnecessários)
        old_instance = sender.objects.only(field_name).get(pk=instance.pk)  # pega o objeto antigo do banco
        old_file = getattr(old_instance, field_name)                        # pega o arquivo antigo usando o nome do campo
        new_file = getattr(instance, field_name)                            # pega o novo arquivo usando o nome do campo

        if old_file and old_file != new_file:
            delete_old_file(old_file)

    except sender.DoesNotExist:
        return False

def get_file_path(instance, filename):
    """
        Gera um caminho único e organizado para qualquer tipo de arquivo.
        Funciona para ImageField, FileField e VideoField.
    """
    # extrai a extensão original (ex: .jpg, .pdf, .mp4)
    ext = os.path.splitext(filename)[1].lower()

    fake_jpeg_extensions = ['.jpeg', '.jfif', '.pjpeg', '.pjp']
    if ext in fake_jpeg_extensions:
        ext = '.jpg'  # normaliza extensões JPEG para .jpg
    
    # Gera um nome único via UUID
    new_filename = f"{uuid.uuid4()}{ext}"
    
    # Define a pasta base pelo nome do Model (ex: Product -> 'product')
    folder_name = instance.__class__.__name__.lower()
    
    # organiza por data, exemplo: product/2026/01/23/uuid.ext
    date_path = now().strftime("%Y/%m/%d")

    # usa f-string com barras laterais para garantir compatibilidade com S3/Nginx
    return f"{folder_name}/{date_path}/{new_filename}"

def delete_old_file(file):
    if file and os.path.isfile(file.path):
        os.remove(file.path)
