import base64
import sys
import json
import os

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python to_base64.py authz/test/media/imagen9.jpg [authz/test/media/imagen10.jpg ...]")
        print("Ejemplo: python to_base64.py authz/test/media/imagen9.jpg authz/test/media/imagen10.jpg authz/test/media/imagen11.jpg authz/test/media/imagen12.jpg")
        sys.exit(1)

    fotos_base64 = []
    for image_path in sys.argv[1:]:
        if not os.path.isfile(image_path):
            print(f"ADVERTENCIA: El archivo '{image_path}' no existe y será ignorado.")
            continue
        b64 = image_to_base64(image_path)
        fotos_base64.append(b64)

    if not fotos_base64:
        print("No se procesó ninguna imagen válida.")
        sys.exit(1)

    # Puedes agregar aquí otros campos de ejemplo si lo deseas
    json_data = {
        "fotos_reconocimiento_base64": fotos_base64
    }

    output_file = "salida.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2)
    print(f"\nEl JSON se ha guardado en el archivo '{output_file}'. Puedes abrirlo y copiarlo en Postman.")
import base64
for idx in range(9, 13):
    with open(f"authz/tests/media/{idx}.jpg", "rb") as img_file:
        img_b64 = base64.b64encode(img_file.read()).decode('utf-8')
        print(f"Imagen {idx}.jpg:\n{img_b64}\n")