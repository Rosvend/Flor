import io
import cv2
import numpy as np
from typing import List, Dict, Any
from ultralytics import YOLO
from PIL import Image
from src.domain.ports.vision_port import VisionAnalyzerPort

class YOLOVisionAdapter(VisionAnalyzerPort):
    def __init__(self, model_name: str = "yolov8n.pt"):
        # Esto descargará el modelo automáticamente la primera vez
        self.model = YOLO(model_name)

    def analyze(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Analiza una imagen usando YOLO y devuelve los objetos detectados.
        """
        try:
            # Convertir bytes a imagen PIL y luego a formato compatible con YOLO (numpy array)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Ejecutar inferencia
            results = self.model(image, verbose=False)
            
            detected_objects = []
            
            for r in results:
                for box in r.boxes:
                    # Obtener la etiqueta (clase) y confianza
                    class_id = int(box.cls[0])
                    label = self.model.names[class_id]
                    confidence = float(box.conf[0])
                    
                    detected_objects.append({
                        "label": label,
                        "confidence": confidence,
                        "box": box.xyxy[0].tolist() # [x1, y1, x2, y2]
                    })
            
            return detected_objects
            
        except Exception as e:
            print(f"Error analizando imagen con YOLO: {e}")
            return []
