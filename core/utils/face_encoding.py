from django.core.files.base import ContentFile
import base64

def generate_face_encoding_from_base64(foto_base64):
    """
    Recibe una imagen en base64 (data:image/...) y retorna el encoding facial (o None si falla).
    """
    try:
        import face_recognition
        format_str, imgstr = foto_base64.split(';base64,')
        ext = format_str.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'temp_face.{ext}')
        image = face_recognition.load_image_file(data)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            return encodings[0].tolist()
        return None
    except Exception:
        return None
