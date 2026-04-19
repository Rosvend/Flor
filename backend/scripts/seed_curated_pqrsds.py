"""
Genera 5 PQRSD curated y las carga al endpoint /api/v1/ingest/curated.
Uso: python -m scripts.seed_curated_pqrsds [--url http://localhost:8000]
"""

import sys
import httpx
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = sys.argv[sys.argv.index("--url") + 1] if "--url" in sys.argv else "http://localhost:8000"
ENDPOINT = f"{BACKEND_URL}/api/v1/ingest/curated"


def ts(days_ago: int = 0) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


REGISTROS = [
    {
        "timestamp_radicacion": ts(4),
        "tipo": "Peticion",
        "canal": "WEB",
        "anonima": False,
        "estado": "PENDIENTE",
        "organization_id": 1,
        "usuario": {
            "nombre": "Carlos Andrés Mendoza",
            "documento": "CC 71845632",
            "telefono": "+573142981045",
            "email": "camendoza@gmail.com",
        },
        "ubicacion": {
            "pais": "Colombia",
            "departamento": "Antioquia",
            "ciudad": "Medellín",
            "direccion": "Calle 50 # 40-20, Apto 301, Laureles",
            "direccion_hecho": "Calle 50 # 40-20, Apto 301, Laureles",
        },
        "contenido": (
            "Solicito información detallada sobre los programas de financiación disponibles "
            "para microempresarios del sector panadero. Soy propietario de una panadería artesanal "
            "con cinco años de operación en el barrio Laureles y deseo acceder a crédito para "
            "adquirir un horno de mayor capacidad."
        ),
        "respuesta": None,
        "metadata": {
            "persona": "natural",
            "genero": "masculino",
            "atencion_preferencial": "Ninguna",
            "es_solicitud_informacion": "Si",
            "autoriza_notificacion": "Si",
        },
    },
    {
        "timestamp_radicacion": ts(3),
        "tipo": "Denuncia",
        "canal": "MAIL",
        "anonima": False,
        "estado": "PENDIENTE",
        "organization_id": 1,
        "usuario": {
            "nombre": "Valentina Torres Gómez",
            "documento": "CC 43892017",
            "telefono": "+573008871234",
            "email": "v.torres@outlook.com",
        },
        "ubicacion": {
            "pais": "Colombia",
            "departamento": "Antioquia",
            "ciudad": "Medellín",
            "direccion": "Carrera 80 # 33-15, El Poblado",
            "direccion_hecho": "Carrera 80 # 33-15, El Poblado",
        },
        "contenido": (
            "Presento denuncia formal por presuntas irregularidades en la adjudicación de contratos "
            "de capacitación empresarial de la Subsecretaría de Creación y Fortalecimiento Empresarial "
            "durante el primer trimestre de 2026. Los contratos fueron asignados sin licitación pública "
            "a una empresa con vínculos familiares a un funcionario de planta."
        ),
        "respuesta": None,
        "metadata": {
            "persona": "natural",
            "genero": "femenino",
            "atencion_preferencial": "Ninguna",
            "es_solicitud_informacion": "No",
            "autoriza_notificacion": "Si",
        },
    },
    {
        "timestamp_radicacion": ts(2),
        "tipo": "Queja",
        "canal": "FB_DM",
        "anonima": False,
        "estado": "PENDIENTE",
        "organization_id": 1,
        "usuario": {
            "nombre": "María Alejandra Suárez",
            "documento": "CE-8821045",
            "telefono": "+573214456789",
            "email": "msuarez.ve@gmail.com",
        },
        "ubicacion": {
            "pais": "Venezuela",
            "departamento": "Antioquia",
            "ciudad": "Medellín",
            "direccion": "Calle 30 # 65-40, Belén",
            "direccion_hecho": "Alpujarra - Centro de Emprendimiento",
        },
        "contenido": (
            "Presento queja formal por la atención recibida en el Centro de Emprendimiento de la "
            "Alpujarra. El funcionario de turno me informó que los programas de apoyo no aplican "
            "para personas con cédula de extranjería, lo cual considero discriminatorio. Solicito "
            "aclaración oficial y capacitación al personal."
        ),
        "respuesta": None,
        "metadata": {
            "persona": "natural",
            "genero": "femenino",
            "atencion_preferencial": "Victima de conflicto",
            "es_solicitud_informacion": "No",
            "autoriza_notificacion": "Si",
        },
    },
    {
        "timestamp_radicacion": ts(1),
        "tipo": "Solicitud",
        "canal": "IG_DM",
        "anonima": False,
        "estado": "PENDIENTE",
        "organization_id": 1,
        "usuario": {
            "nombre": "TechGirls SAS",
            "documento": "NIT 900.441.821-7",
            "telefono": "+576042881100",
            "email": "contacto@techgirls.co",
        },
        "ubicacion": {
            "pais": "Colombia",
            "departamento": "Antioquia",
            "ciudad": "Medellín",
            "direccion": "Calle 10 # 43E-31, El Poblado",
            "direccion_hecho": "Calle 10 # 43E-31, El Poblado",
        },
        "contenido": (
            "En representación de TechGirls SAS, startup de tecnología educativa fundada por mujeres, "
            "solicitamos información sobre convocatorias de capital semilla disponibles para empresas "
            "de base tecnológica. Contamos con dos años de operación y tres empleadas de tiempo completo. "
            "Buscamos financiación para nuestra aplicación de alfabetización digital para adultos mayores."
        ),
        "respuesta": None,
        "metadata": {
            "persona": "juridica",
            "genero": None,
            "atencion_preferencial": "Ninguna",
            "es_solicitud_informacion": "Si",
            "autoriza_notificacion": "Si",
        },
    },
    {
        "timestamp_radicacion": ts(0),
        "tipo": "Reclamo",
        "canal": "WEB",
        "anonima": False,
        "estado": "PENDIENTE",
        "organization_id": 1,
        "usuario": {
            "nombre": "Jorge Iván Ospina Cardona",
            "documento": "CC 98654320",
            "telefono": "+573015672891",
            "email": "jospina.robledo@gmail.com",
        },
        "ubicacion": {
            "pais": "Colombia",
            "departamento": "Antioquia",
            "ciudad": "Medellín",
            "direccion": "Transversal 39 # 72-18, Robledo",
            "direccion_hecho": "Centro de Servicios Laureles",
        },
        "contenido": (
            "Presento reclamo formal por cobro indebido realizado en la ventanilla del Centro de "
            "Servicios Laureles el 10 de abril de 2026. Me cobraron $45.000 por un certificado de "
            "actividad económica que según la Resolución Municipal 0234 de 2025 es completamente "
            "gratuito. Recibo de pago #20260410-8821. Solicito devolución del dinero."
        ),
        "respuesta": None,
        "metadata": {
            "persona": "natural",
            "genero": "masculino",
            "atencion_preferencial": "Adulto mayor",
            "es_solicitud_informacion": "No",
            "autoriza_notificacion": "No",
        },
    },
]


def main():
    print(f"\n{'='*60}")
    print(f"  Seed curated PQRSDs → {ENDPOINT}")
    print(f"{'='*60}")
    print(f"  Registros a enviar: {len(REGISTROS)}")

    resp = httpx.post(ENDPOINT, json=REGISTROS, timeout=30)
    resp.raise_for_status()
    result = resp.json()

    stored_keys = result["stored_keys"]
    print(f"  ✓ {len(stored_keys)} registros almacenados:\n")
    for key, reg in zip(stored_keys, REGISTROS):
        tipo  = reg["tipo"]
        canal = reg["canal"]
        nombre = reg["usuario"]["nombre"]
        print(f"    [{key:<28}] [{tipo:<10}] [{canal:<7}] {nombre}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
