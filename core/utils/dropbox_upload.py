import os
import dropbox
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
DROPBOX_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')

def upload_image_to_dropbox(file_obj, filename, folder="/FotoVisita"):
    """
    Sube una imagen a Dropbox y retorna la URL pública.
    file_obj: archivo (BytesIO, InMemoryUploadedFile, etc)
    filename: nombre del archivo (ej: 'foto.jpg')
    folder: carpeta en Dropbox (por defecto /FotoVisita)
    """
    if not DROPBOX_TOKEN:
        raise Exception("No se encontró el token de Dropbox en las variables de entorno.")
    dbx = dropbox.Dropbox(DROPBOX_TOKEN)
    dropbox_path = f"{folder}/{filename}"
    # Subir archivo
    file_obj.seek(0)
    dbx.files_upload(file_obj.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
    # Crear link compartido o reutilizar si ya existe
    try:
        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)
    except dropbox.exceptions.ApiError as e:
        if (hasattr(e, 'error') and hasattr(e.error, 'is_shared_link_already_exists') and e.error.is_shared_link_already_exists()):
            # Obtener el enlace existente
            links = dbx.sharing_list_shared_links(path=dropbox_path, direct_only=True).links
            if links:
                shared_link_metadata = links[0]
            else:
                raise Exception("No se pudo obtener el enlace existente de Dropbox.")
        else:
            raise
    # Convertir a enlace de descarga directa (dl=1)
    url = shared_link_metadata.url
    if url.endswith('?dl=0'):
        url = url.replace('?dl=0', '?dl=1')
    elif url.endswith('?dl=1'):
        pass
    elif '?dl=0&' in url:
        url = url.replace('?dl=0&', '?dl=1&')
    elif '?dl=0' in url:
        url = url.replace('?dl=0', '?dl=1')
    else:
        # Si no tiene ?dl=0 ni ?dl=1, forzar ?dl=1
        if '?' in url:
            url = url.split('?')[0]
        url = url + '?dl=1'
    # Devolver path real y url
    return {"path": dropbox_path, "url": url}
