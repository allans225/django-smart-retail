import os
from PIL import Image
from django.conf import settings

def process_image_for_webp(img_field, new_width=800):
    img_full_path = os.path.join(settings.MEDIA_ROOT, img_field.name)
    
    try:
        # garante que o arquivo seja fechado corretamente
        with Image.open(img_full_path) as pil_img:
            # lógica de Redimensionamento
            original_width, original_height = pil_img.size

            # Se a largura original for maior que a nova largura, redimensiona...
            if original_width > new_width:
                new_height = round((new_width * original_height) / original_width)
                # Usando Resampling.LANCZOS se Pillow >= 10 (versão), senão apenas LANCZOS
                resample_method = getattr(Image, 'Resampling', Image).LANCZOS
                pil_img = pil_img.resize((new_width, new_height), resample_method)

            # preparação do Caminho WebP
            path_without_ext = os.path.splitext(img_full_path)[0]
            webp_full_path = f"{path_without_ext}.webp"
            
            # Salvamento Único (converte para WebP)
            pil_img.save(webp_full_path, "WEBP", optimize=True, quality=80)

        # Limpeza: remove o original se não for webp
        if not img_full_path.endswith('.webp'):
            if os.path.exists(img_full_path):
                os.remove(img_full_path)
            
        # Retorna o novo nome relativo para o banco de dados
        return os.path.splitext(img_field.name)[0] + '.webp'

    except Exception as e:
        print(f"Erro no processamento da imagem: {e}")
        return None
