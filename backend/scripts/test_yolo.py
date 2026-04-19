import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para poder importar src
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.infrastructure.vision.yolo_vision_adapter import YOLOVisionAdapter

def test_yolo():
    print("Iniciando prueba de YOLO...")
    try:
        adapter = YOLOVisionAdapter()
        print("Modelo cargado exitosamente.")
        
        # Si quieres probar con una imagen real, coloca la ruta aquí
        # image_path = "ruta/a/tu/imagen.jpg"
        # with open(image_path, "rb") as f:
        #     results = adapter.analyze(f.read())
        #     print(f"Objetos detectados: {results}")
        
        print("Prueba de inicialización completada con éxito.")
    except Exception as e:
        print(f"Error en la prueba: {e}")

if __name__ == "__main__":
    test_yolo()
