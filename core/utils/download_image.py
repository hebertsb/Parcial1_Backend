import requests
from io import BytesIO
import os
import dropbox
from dotenv import load_dotenv

load_dotenv()
DROPBOX_TOKEN = os.getenv('DROPBOX_ACCESS_TOKEN')

def download_image_from_url(url):
    """
    Descarga una imagen desde una URL y la retorna como BytesIO.
    Si la URL es de Dropbox, usa la API para obtener el archivo binario real.
    """
    # Si es un dict con path, usar Dropbox API
    if isinstance(url, dict) and 'path' in url and DROPBOX_TOKEN:
        dbx = dropbox.Dropbox(DROPBOX_TOKEN)
        _, res = dbx.files_download(url['path'])
        return BytesIO(res.content)
    # Si es string, mantener compatibilidad
    if isinstance(url, str) and 'dropbox.com' in url and DROPBOX_TOKEN:
        import re
        m = re.search(r'dropbox.com/.+?/([^/?]+)', url)
        filename = m.group(1) if m else None
        dbx = dropbox.Dropbox(DROPBOX_TOKEN)
        dropbox_path = f"/FotoVisita/{filename}" if filename else None
        if dropbox_path:
            _, res = dbx.files_download(dropbox_path)
            return BytesIO(res.content)
        else:
            raise Exception("No se pudo extraer el nombre de archivo de la URL de Dropbox.")
    else:
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)
