import os
import dropbox  # type: ignore
from dotenv import load_dotenv
from typing import Dict, Any, Optional, Union

# Cargar variables de entorno
load_dotenv()
DROPBOX_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')

def upload_image_to_dropbox(file_obj: Any, filename: str, folder: str = "/ParcialSI2") -> Dict[str, Optional[str]]:
    """
    Sube una imagen a Dropbox y retorna la URL pública.
    file_obj: archivo (BytesIO, InMemoryUploadedFile, etc)
    filename: nombre del archivo (ej: 'foto.jpg')
    folder: carpeta en Dropbox (por defecto /ParcialSI2)
    
    Returns:
        Dict con 'path' y 'url' de la imagen subida
    """
    print(f"[DROPBOX] Token usado: {DROPBOX_TOKEN}")
    if not DROPBOX_TOKEN:
        raise Exception("No se encontró el token de Dropbox en las variables de entorno.")
    
    try:
        dbx = dropbox.Dropbox(DROPBOX_TOKEN)
        dropbox_path = f"{folder}/{filename}"
        print(f"[DROPBOX] Subiendo archivo a: {dropbox_path}")
        file_obj.seek(0)
        
        # Subir archivo usando la API de Dropbox
        dbx.files_upload(file_obj.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)  # type: ignore
        print(f"[DROPBOX] Archivo subido correctamente a: {dropbox_path}")
    except Exception as e:
        print(f"[DROPBOX] Error subiendo archivo: {e}")
        raise
    # Crear link compartido o reutilizar si ya existe
    shared_link_metadata = None
    try:
        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(dropbox_path)  # type: ignore
        if shared_link_metadata and hasattr(shared_link_metadata, 'url'):
            print(f"[DROPBOX] Enlace público generado: {shared_link_metadata.url}")
    except Exception as e:
        print(f"[DROPBOX] Error generando enlace público: {e}")
        # Intentar obtener el enlace existente manualmente si la creación falla
        try:
            shared_links_result = dbx.sharing_list_shared_links(path=dropbox_path, direct_only=True)  # type: ignore
            if shared_links_result and hasattr(shared_links_result, 'links') and shared_links_result.links:
                shared_link_metadata = shared_links_result.links[0]
                if shared_link_metadata and hasattr(shared_link_metadata, 'url'):
                    print(f"[DROPBOX] Enlace existente reutilizado: {shared_link_metadata.url}")
            else:
                print("[DROPBOX] No se pudo obtener el enlace existente de Dropbox.")
                return {"path": dropbox_path, "url": None}
        except Exception as e2:
            print(f"[DROPBOX] Error obteniendo enlace existente: {e2}")
            return {"path": dropbox_path, "url": None}
    # Validar que tenemos un enlace válido
    if not shared_link_metadata or not hasattr(shared_link_metadata, 'url'):
        print("[DROPBOX] No se pudo obtener URL del enlace compartido.")
        return {"path": dropbox_path, "url": None}
    
    # Convertir a URL directa para mostrar imágenes en frontend
    url = shared_link_metadata.url
    
    # Convertir de www.dropbox.com a dl.dropboxusercontent.com para descarga directa
    if url and url.startswith("https://www.dropbox.com/scl/fi/"):
        url = url.replace("https://www.dropbox.com/scl/fi/", "https://dl.dropboxusercontent.com/scl/fi/")
        # Remover parámetros dl para URL directa
        if "?dl=1" in url:
            url = url.replace("?dl=1", "")
        if "?dl=0" in url:
            url = url.replace("?dl=0", "")
    
    print(f"[DROPBOX] Enlace final para descarga directa: {url}")
    # Devolver path real y url
    return {"path": dropbox_path, "url": url}
