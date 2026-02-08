import re
import random
import string
from django.utils.text import slugify

def unique_slug(instance, new_slug=None):
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
        return unique_slug(instance, new_slug=new_slug)
    
    return slug


def sku(product_name, variation_name=None):
    # Limpa e formata o nome (ex: "Camiseta Azul" -> "CAMAZU")
    clean_name = re.sub(r'[^A-Z0-9]', '', product_name.upper())
    sku_base = clean_name[:6] # Pega os primeiros 6 caracteres
    
    if variation_name:
        clean_var = re.sub(r'[^A-Z0-9]', '', variation_name.upper())
        sku_base += f"-{clean_var[:3]}"
        
    return sku_base