import string
import random
from django.utils.text import slugify

def generate_unique_slug(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name)

    instance_class = instance.__class__
    # Verifica se o slug já existe na base de dados
    exists = instance_class.objects.filter(slug=slug).exists()

    if exists:
        ramdom_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        new_slug = f"{slug}-{ramdom_str}"
        # Recursividade para garantir que o slug é único
        return generate_unique_slug(instance, new_slug=new_slug)
    
    return slug
