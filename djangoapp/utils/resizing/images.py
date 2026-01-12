import os
from PIL import Image
from django.conf import settings

def resize_image(img, new_width=800):
    img_full_path = os.path.join(settings.MEDIA_ROOT, img.name)
    
    try:
        pil_img = Image.open(img_full_path)
        original_width, original_height = pil_img.size

        if original_width <= new_width:
            pil_img.close()
            return

        # Cálculo da nova altura mantendo a proporção
        new_height = round((new_width * original_height) / original_width)

        # Redimensiona usando as novas dimensões
        new_img = pil_img.resize((new_width, new_height), Image.LANCZOS)
        
        new_img.save(
            img_full_path,
            optimize=True,
            quality=60 # 60 é um bom equilíbrio entre peso e qualidade
        )
        
        new_img.close()
        pil_img.close()
    except Exception as e:
        print(f"Erro ao redimensionar imagem: {e}")