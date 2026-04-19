import json
import time
import logging
from typing import Dict, Any, List
from src.domain.ports.curated_data_lake import CuratedDataLakePort
from src.domain.ports.generation_port import GenerationPort

logger = logging.getLogger(__name__)

class AnalyzeMapDensity:
    """
    Lee las PQR del Data Lake, extrae la información de ubicación y texto,
    y utiliza Gemini para agruparlas por Comuna de Medellín (1 a 16),
    identificando la densidad y la problemática principal.
    """
    
    COMUNAS_MEDELLIN = [
        {"id": 1, "nombre": "Popular", "lat": 6.295, "lng": -75.545},
        {"id": 2, "nombre": "Santa Cruz", "lat": 6.290, "lng": -75.555},
        {"id": 3, "nombre": "Manrique", "lat": 6.275, "lng": -75.545},
        {"id": 4, "nombre": "Aranjuez", "lat": 6.275, "lng": -75.560},
        {"id": 5, "nombre": "Castilla", "lat": 6.290, "lng": -75.575},
        {"id": 6, "nombre": "Doce de Octubre", "lat": 6.300, "lng": -75.580},
        {"id": 7, "nombre": "Robledo", "lat": 6.275, "lng": -75.590},
        {"id": 8, "nombre": "Villa Hermosa", "lat": 6.255, "lng": -75.545},
        {"id": 9, "nombre": "Buenos Aires", "lat": 6.235, "lng": -75.550},
        {"id": 10, "nombre": "La Candelaria", "lat": 6.250, "lng": -75.565},
        {"id": 11, "nombre": "Laureles-Estadio", "lat": 6.245, "lng": -75.590},
        {"id": 12, "nombre": "La América", "lat": 6.255, "lng": -75.605},
        {"id": 13, "nombre": "San Javier", "lat": 6.255, "lng": -75.620},
        {"id": 14, "nombre": "El Poblado", "lat": 6.205, "lng": -75.570},
        {"id": 15, "nombre": "Guayabal", "lat": 6.210, "lng": -75.585},
        {"id": 16, "nombre": "Belén", "lat": 6.220, "lng": -75.600},
    ]

    def __init__(
        self,
        curated_data_lake: CuratedDataLakePort,
        generation: GenerationPort,
        cache_ttl: int = 900 # 15 minutos
    ):
        self._data_lake = curated_data_lake
        self._generation = generation
        self._cache_ttl = cache_ttl
        
        # Cache memory
        self._cache_time = 0.0
        self._cache_data = None
        self._cache_org = None

    def execute(self, organization_id: int) -> List[Dict[str, Any]]:
        # Verificar cache
        if self._cache_data and self._cache_org == organization_id and (time.time() - self._cache_time) < self._cache_ttl:
            logger.info("Retornando datos del mapa desde caché.")
            return self._cache_data

        # 1. Obtener todas las PQR de la organización
        all_pqrs = [
            p for p in self._data_lake.get_all() 
            if p.get("organization_id", 1) == organization_id
        ]
        
        if not all_pqrs:
            return []

        # 2. Extraer datos relevantes para la IA
        data_to_analyze = []
        for p in all_pqrs:
            radicado = p.get("radicado")
            
            # Buscar ubicación en el formato nuevo o legacy
            ubicacion = ""
            if "ubicacion" in p and isinstance(p["ubicacion"], dict):
                ubicacion = p["ubicacion"].get("direccion_hecho") or p["ubicacion"].get("direccion") or ""
            elif "ciudadano" in p and isinstance(p["ciudadano"], dict):
                ubicacion = p["ciudadano"].get("direccion") or ""
                
            contenido = p.get("contenido") or p.get("descripcion_detallada") or ""
            
            if ubicacion and len(ubicacion.strip()) > 3:
                data_to_analyze.append({
                    "id": radicado,
                    "ubicacion": ubicacion,
                    "contenido": contenido[:300] # Truncar para no sobrepasar tokens
                })

        if not data_to_analyze:
            return []

        system_prompt = f"""
        Eres un experto en geografía urbana de la ciudad de Medellín, Colombia, y analista de datos.
        A continuación te presento una lista de {len(data_to_analyze)} registros de PQRS.
        Cada registro tiene una 'ubicacion' (dirección o barrio) y un 'contenido' resumiendo el problema.
        
        Tu tarea es:
        1. Inferir a cuál de las 16 comunas de Medellín pertenece cada PQRS basado en su 'ubicacion'.
        2. Agrupar las PQRS por comuna (solo considera las comunas del 1 al 16).
        3. Contar la cantidad de PQRS en cada comuna.
        4. Redactar una explicación de 1 o 2 frases resumiendo cuál es la problemática principal o más repetitiva en esa comuna basada en el 'contenido' de las PQRS.

        Comunas de Medellín:
        1: Popular, 2: Santa Cruz, 3: Manrique, 4: Aranjuez, 5: Castilla, 6: Doce de Octubre, 7: Robledo, 8: Villa Hermosa, 9: Buenos Aires, 10: La Candelaria, 11: Laureles-Estadio, 12: La América, 13: San Javier, 14: El Poblado, 15: Guayabal, 16: Belén.
        
        Si no puedes determinar la comuna de una PQRS, ignórala.
        
        Responde ESTRICTAMENTE con un JSON Array válido donde cada objeto tenga esta estructura exacta (no agregues markdown ni explicaciones adicionales, solo el JSON raw):
        [
            {{
                "comuna_id": 14,
                "count": 5,
                "explicacion": "Múltiples quejas sobre ruido excesivo en zonas comerciales y problemas de basuras."
            }}
        ]
        """
        
        user_prompt = f"DATOS:\n{json.dumps(data_to_analyze, ensure_ascii=False)}"

        try:
            # 4. Llamar a Gemini
            response_text = self._generation.generate(
                system=system_prompt,
                user=user_prompt,
                max_tokens=2048
            )
            
            # Limpiar posible markdown
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            response_text = response_text.strip()
            
            ai_data = json.loads(response_text)
            
            # 5. Fusionar con las coordenadas reales
            result = []
            comunas_dict = {c["id"]: c for c in self.COMUNAS_MEDELLIN}
            
            for item in ai_data:
                cid = item.get("comuna_id")
                if cid in comunas_dict:
                    comuna_info = comunas_dict[cid]
                    result.append({
                        "comuna_id": cid,
                        "nombre": comuna_info["nombre"],
                        "lat": comuna_info["lat"],
                        "lng": comuna_info["lng"],
                        "count": item.get("count", 0),
                        "explicacion": item.get("explicacion", "Sin datos.")
                    })
            
            # Actualizar caché
            self._cache_data = result
            self._cache_time = time.time()
            self._cache_org = organization_id
            
            return result
            
        except Exception as e:
            logger.error(f"Error generando datos del mapa: {e}")
            # Si hay error (ej. Rate Limit), retornar datos vacíos o la caché anterior si existe
            if self._cache_data:
                return self._cache_data
            return []
