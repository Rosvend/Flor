import sys
import os
from pathlib import Path
import asyncio

# Configurar PYTHONPATH para que reconozca 'src'
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.infrastructure.container import curated_data_lake, get_process_pqrs
from src.application.dtos.pqrs_dtos import ProcessPQRSInput

def get_contenido(pqr: dict) -> str:
    return pqr.get("contenido", pqr.get("descripcion_detallada", ""))

def reprocess_all():
    print("Obteniendo todos los registros del bucket Curated...")
    all_pqrs = curated_data_lake.get_all()
    print(f"Total registros encontrados: {len(all_pqrs)}")
    
    process_pqrs = get_process_pqrs()
    
    updated_count = 0
    for record in all_pqrs:
        radicado = record.get("radicado")
        if not radicado:
            continue
            
        # Si ya tiene análisis, se salta (o se podría forzar reprocesamiento si se desea)
        if "analisis_ia" in record and record["analisis_ia"].get("tipo_sugerido"):
            continue
            
        texto = get_contenido(record)
        if len(texto) < 5:
            continue
            
        print(f"Procesando {radicado}...")
        retries = 3
        while retries > 0:
            try:
                # Ejecutar el pipeline de análisis de texto (sin imágenes para registros históricos por ahora)
                analisis = process_pqrs.execute(ProcessPQRSInput(text=texto, images=[]))
                
                analisis_ia = {
                    "sentimiento":        analisis.sentiment,
                    "is_offensive":       analisis.is_offensive,
                    "toxicity_warning":   analisis.toxicity_warning,
                    "offensive_words":    analisis.offensive_words,
                    "tipo_sugerido":      analisis.tipo_sugerido,
                    "secretaria_asignada": analisis.secretaria_asignada,
                    "texto_mejorado":     analisis.improved_text,
                    "objetos_detectados": analisis.detected_objects,
                }
                
                # Actualizar en S3
                curated_data_lake.update_by_radicado(radicado, {"analisis_ia": analisis_ia})
                updated_count += 1
                print(f"  ✓ Actualizado {radicado} -> {analisis.tipo_sugerido} ({analisis.secretaria_asignada})")
                
                # Pausa para respetar el límite de 5 RPM
                import time
                time.sleep(12)
                break
                
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower() or "exhausted" in err_str.lower():
                    print(f"  ! Límite de API alcanzado. Esperando 30 segundos... (Quedan {retries} reintentos)")
                    import time
                    time.sleep(30)
                    retries -= 1
                else:
                    print(f"  X Error en {radicado}: {e}")
                    break

    print(f"Reprocesamiento finalizado. {updated_count} registros actualizados con IA.")

if __name__ == "__main__":
    reprocess_all()
