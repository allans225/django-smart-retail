from django.db.models.signals import post_save, pre_save, post_delete
from .models import Profile
from utils.images import process_image_for_webp
from utils.files import delete_old_file, delete_file_pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Profile)
def profile_pre_save_delete_old_image(sender, instance, **kwargs):
    """ Deletar a imagem antiga do sistema de arquivos quando a instância é atualizada com uma nova imagem """
    delete_file_pre_save(sender, instance, 'picture')

@receiver(post_save, sender=Profile)
def profile_process_image(sender, instance, **kwargs):
    """ Processar imagem para WebP depois de salvar o perfil """
    if instance.picture:
        if instance.picture.path.lower().endswith('.webp'):
            return  # A imagem já está em WebP, não precisa processar
        new_path = process_image_for_webp(instance.picture) # processa a imagem para WebP
        if new_path:
            # Atualiza o campo picture com o novo caminho da imagem WebP
            Profile.objects.filter(pk=instance.pk).update(picture=new_path)

@receiver(post_delete, sender=Profile)
def profile_delete_file_on_delete(sender, instance, **kwargs):
    """ Deletar o objeto = deletar a imagem do sistema de arquivos """
    if instance.picture:
        delete_old_file(instance.picture)
