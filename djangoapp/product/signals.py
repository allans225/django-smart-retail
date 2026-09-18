from django.db.models.signals import post_save, pre_save, post_delete
from .models import Product, VariationImage
from utils.images import process_image_for_webp
from utils.files import delete_old_file, delete_file_pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Product)
def product_pre_save_delete_old_image(sender, instance, **kwargs):
    delete_file_pre_save(sender, instance, 'cover_image')

@receiver(pre_save, sender=VariationImage)
def variation_image_pre_save_delete_old_image(sender, instance, **kwargs):
    delete_file_pre_save(sender, instance, 'image')

""" Product - processar imagem para WebP depois de salvar o produto """
@receiver(post_save, sender=Product)
def product_process_image(sender, instance, **kwargs):
    if instance.cover_image:
        if instance.cover_image.path.lower().endswith('.webp'):
            return  # A imagem já está em WebP, não precisa processar
        new_path = process_image_for_webp(instance.cover_image) # processa a imagem para WebP
        if new_path:
            # Atualiza o campo cover_image com o novo caminho da imagem WebP
            Product.objects.filter(pk=instance.pk).update(cover_image=new_path)

""" VariationImage - processar imagem para WebP depois de salvar a variação """
@receiver(post_save, sender=VariationImage)
def variation_image_process_webp(sender, instance, **kwargs):
    if instance.image and not instance.image.path.lower().endswith('.webp'):
        new_path = process_image_for_webp(instance.image)
        if new_path:
            VariationImage.objects.filter(pk=instance.pk).update(image=new_path)

""" Deletar o objeto = deletar a imagem do sistema de arquivos """
@receiver(post_delete, sender=Product)
def product_delete_file_on_delete(sender, instance, **kwargs):
    if instance.cover_image:
        delete_old_file(instance.cover_image)

@receiver(post_delete, sender=VariationImage)
def variation_image_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        delete_old_file(instance.image)
