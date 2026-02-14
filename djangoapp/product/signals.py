from django.db.models.signals import post_save, pre_save, post_delete
from .models import Product, VariationImage
from utils.images import process_image_for_webp
from utils.files import delete_old_file
from django.dispatch import receiver

""" Product - deletar imagem antiga antes de salvar a nova img """
@receiver(pre_save, sender=Product)
def product_delete_old_image(sender, instance, **kwargs):
    if not instance.pk:
        return False    # se for criação, não tem imagem antiga para deletar
    try:
        old = Product.objects.get(pk=instance.pk) # pega o produto antigo do banco
    except Product.DoesNotExist:
        return False    # se não existir, não tem imagem antiga para deletar
    
    if old.cover_image and old.cover_image != instance.cover_image:
        delete_old_file(old.cover_image)    # deleta a imagem antiga do sistema de arquivos

""" Product - processar imagem para WebP depois de salvar o produto """
@receiver(post_save, sender=Product)
def product_process_image(sender, instance, **kwargs):
    if instance.cover_image:
        new_path = process_image_for_webp(instance.cover_image)     # processa a imagem para WebP
        if new_path:
            # Atualiza o campo cover_image com o novo caminho da imagem WebP
            Product.objects.filter(pk=instance.pk).update(cover_image=new_path)

""" VariationImage - Deletar imagem antiga """
@receiver(pre_save, sender=VariationImage)
def variationimage_delete_old_image(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old = VariationImage.objects.get(pk=instance.pk)
    except VariationImage.DoesNotExist:
        return False
    if old.image and old.image != instance.image:
        delete_old_file(old.image)

""" Deletar o objeto = deletar a imagem do sistema de arquivos """
@receiver(post_delete, sender=Product)
def product_delete_file_on_delete(sender, instance, **kwargs):
    if instance.cover_image:
        delete_old_file(instance.cover_image)

@receiver(post_delete, sender=VariationImage)
def variationimage_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        delete_old_file(instance.image)
