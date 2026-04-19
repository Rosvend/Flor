"""
1. Elimina TODOS los objetos curated/ del S3.
2. Crea 20 PQRSDs curated con JSON completo y las sube al endpoint /api/v1/ingest/curated:
   - 10 para secretaria_desarrollo_economico (org_id=1)
   - 1 para cada uno de los 10 departamentos seleccionados al azar (org_ids: 22,5,2,25,10,9,27,6,29,19)

Uso: uv run python -m scripts.seed_curated_v2 [--url http://localhost:8000]
"""

import sys
import os
import boto3
from botocore.config import Config
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import httpx

load_dotenv()

BACKEND_URL = sys.argv[sys.argv.index("--url") + 1] if "--url" in sys.argv else "http://localhost:8000"
ENDPOINT = f"{BACKEND_URL}/api/v1/ingest/curated"

BUCKET = os.environ["S3_RAW_BUCKET"]
PREFIX = os.getenv("S3_CURATED_PREFIX", "curated/")

CORREO = "pedroj1229@gmail.com"


def ts(days_ago: int = 0, hours_ago: int = 0) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago, hours=hours_ago)).isoformat()


# ── 1. Limpiar S3 ────────────────────────────────────────────────────────────

def delete_all_curated():
    s3 = boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        config=Config(connect_timeout=5, read_timeout=10, retries={"max_attempts": 2}),
    )
    paginator = s3.get_paginator("list_objects_v2")
    keys = []
    for page in paginator.paginate(Bucket=BUCKET, Prefix=PREFIX):
        for obj in page.get("Contents", []):
            if "_metadata" not in obj["Key"]:
                keys.append({"Key": obj["Key"]})

    if keys:
        s3.delete_objects(Bucket=BUCKET, Delete={"Objects": keys})
        print(f"✓ Eliminados {len(keys)} objetos de s3://{BUCKET}/{PREFIX}")
    else:
        print("  No había objetos curated en S3.")


# ── 2. Registros ─────────────────────────────────────────────────────────────

def ciudadano(nombre: str, doc: str, telefono: str, genero: str = "Masculino") -> dict:
    return {
        "nombres":           nombre,
        "apellidos":         None,
        "tipo_documento":    "CC",
        "numero_documento":  doc,
        "tipo_persona":      "Natural",
        "genero":            genero,
        "correo_electronico": CORREO,
        "telefono":          telefono,
        "id_meta":           None,
    }


def ubicacion(direccion: str, direccion_hecho: str = None) -> dict:
    return {
        "pais":            "Colombia",
        "departamento":    "Antioquia",
        "ciudad":          "Medellín",
        "direccion":       direccion,
        "direccion_hecho": direccion_hecho or direccion,
    }


def meta(genero: str = "Masculino", preferencial: str = "Ninguna", info: str = "No") -> dict:
    return {
        "persona":                "Natural",
        "genero":                 genero,
        "atencion_preferencial":  preferencial,
        "es_solicitud_informacion": info,
        "autoriza_notificacion":  "Si",
    }


REGISTROS = [

    # ── 10 para Secretaría de Desarrollo Económico (org_id=1) ────────────────

    {
        "tipo": "Peticion",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 1,
        "ciudadano": ciudadano("Carlos Andrés Mendoza", "1023456789", "3014567890"),
        "ubicacion": ubicacion("Calle 50 # 40-20", "Centro de Servicios Laureles"),
        "contenido": (
            "Soy propietario de una panadería artesanal con cinco años de operación en el "
            "barrio Laureles. Deseo acceder a crédito para adquirir un horno de mayor "
            "capacidad y así expandir mi producción. Solicito información sobre los programas "
            "de financiación disponibles para microempresarios en Medellín."
        ),
        "metadata": meta(),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=5),
    },
    {
        "tipo": "Queja",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 1,
        "ciudadano": ciudadano("Luisa Fernanda Ríos", "1098765432", "3124567890", "Femenino"),
        "ubicacion": ubicacion("Carrera 70 # 45-30", "Parque Estadio"),
        "contenido": (
            "Mi empresa de confecciones lleva tres meses esperando respuesta a una solicitud "
            "de vinculación al programa de fortalecimiento empresarial. Nadie en la Secretaría "
            "de Desarrollo Económico me responde los correos ni atiende el teléfono. Solicito "
            "respuesta urgente ya que perdí dos contratos mientras esperaba el apoyo prometido."
        ),
        "metadata": meta("Femenino"),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=8),
    },
    {
        "tipo": "Denuncia",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 1,
        "ciudadano": ciudadano("Andrés Felipe Vargas", "71456789", "3006789012"),
        "ubicacion": ubicacion("Av. El Poblado # 15-20"),
        "contenido": (
            "Denuncio presunta irregularidad en la asignación de subsidios del Banco Distrital "
            "de las Oportunidades. Los contratos del primer trimestre de 2026 fueron asignados "
            "sin licitación pública a una empresa con vínculos familiares a un funcionario de "
            "planta de la Subsecretaría. Adjunto registros de contratación pública."
        ),
        "metadata": meta(),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=12),
    },
    {
        "tipo": "Reclamo",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 1,
        "ciudadano": ciudadano("María Isabel Cano", "43567890", "3157890123", "Femenino"),
        "ubicacion": ubicacion("Calle 10 # 32-15", "Centro Comercial Palmas"),
        "contenido": (
            "El programa de emprendimiento femenino al que me inscribí prometía asesoría "
            "mensual durante seis meses. Solo recibí dos sesiones y el acompañante asignado "
            "dejó de contestar desde enero. Solicito la reanudación del servicio o una "
            "explicación formal sobre la cancelación del programa."
        ),
        "metadata": meta("Femenino", "Mujer embarazada"),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=3),
    },
    {
        "tipo": "Peticion",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 1,
        "ciudadano": ciudadano("Jorge Iván Ospina", "98654320", "3015672891"),
        "ubicacion": ubicacion("Calle 50 # 40-20"),
        "contenido": (
            "Solicito información detallada sobre los requisitos y procedimientos para acceder "
            "al programa de microcrédito del Banco Distrital de las Oportunidades. Soy "
            "vendedor ambulante con cédula de extranjería y en la oficina me indicaron que "
            "el programa es exclusivo para cédula de ciudadanía, lo cual considero "
            "discriminatorio. Solicito aclaración oficial."
        ),
        "metadata": meta(),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=1),
    },
    {
        "tipo": "Sugerencia",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 1,
        "ciudadano": ciudadano("Valentina Torres", "1001234567", "3209876543", "Femenino"),
        "ubicacion": ubicacion("Carrera 43A # 1-50"),
        "contenido": (
            "Como emprendedora del sector tecnológico sugiero que la Secretaría de Desarrollo "
            "Económico cree una ventanilla virtual única para radicar solicitudes de programas "
            "de apoyo. Actualmente debo ir en persona a tres dependencias distintas para "
            "completar un trámite que debería resolverse en línea en menos de una hora."
        ),
        "metadata": meta("Femenino"),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=2),
    },
    {
        "tipo": "Peticion",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 1,
        "ciudadano": ciudadano("Ricardo Salazar", "1045678901", "3183456789"),
        "ubicacion": ubicacion("Calle 77 # 65-30"),
        "contenido": (
            "Represento a una cooperativa de transporte informal de la zona noroccidental. "
            "Queremos formalizar nuestra operación y necesitamos orientación sobre los pasos "
            "para constituirnos como empresa de transporte legalmente habilitada, acceder a "
            "créditos de renovación vehicular y vincularnos a programas de empleo formal."
        ),
        "metadata": meta(),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=6),
    },
    {
        "tipo": "Reclamo",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 1,
        "ciudadano": ciudadano("Sofía Ramírez", "1007654321", "3002345678", "Femenino"),
        "ubicacion": ubicacion("Calle 30 # 81-200"),
        "contenido": (
            "El pasado 10 de abril realicé el pago del registro mercantil para formalizar "
            "mi negocio de base tecnológica según la Resolución Municipal 0234 de 2025, "
            "trámite que según dicha resolución es completamente gratuito. "
            "Recibo de pago #20260410-8821. Solicito devolución del dinero cobrado."
        ),
        "metadata": meta("Femenino"),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=9),
    },
    {
        "tipo": "Peticion",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 1,
        "ciudadano": ciudadano("Esteban Muñoz", "1034567890", "3118765432"),
        "ubicacion": ubicacion("Diagonal 75B # 2A-50"),
        "contenido": (
            "Soy diseñador gráfico independiente y quiero acceder al programa de exportación "
            "de servicios creativos que la Subsecretaría de Productividad y Competitividad "
            "anunció en febrero. No encuentro información en la página web sobre fechas de "
            "inscripción, requisitos ni contactos del equipo responsable."
        ),
        "metadata": meta(),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=4),
    },
    {
        "tipo": "Queja",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 1,
        "ciudadano": ciudadano("Natalia Herrera", "1056789012", "3165678901", "Femenino"),
        "ubicacion": ubicacion("Carrera 80 # 34-20"),
        "contenido": (
            "Asistí a una feria de emprendimiento organizada por la Secretaría de Desarrollo "
            "Económico el pasado 5 de abril. Los stands prometidos para conectar con "
            "compradores institucionales nunca se habilitaron y el evento terminó dos horas "
            "antes de lo programado sin aviso. Invertí $800.000 en materiales de exhibición "
            "que no pude aprovechar. Solicito explicación y compensación."
        ),
        "metadata": meta("Femenino"),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=14),
    },

    # ── 10 para los otros departamentos (1 cada uno) ──────────────────────────

    # org_id=22 — Secretaría de Medio Ambiente
    {
        "tipo": "Reclamo",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 22,
        "ciudadano": ciudadano("Pablo Giraldo", "1078901234", "3041234567"),
        "ubicacion": ubicacion("Calle 107 # 63-20", "Parque Lineal La Presidenta"),
        "contenido": (
            "Desde hace dos semanas hay un árbol de gran tamaño inclinado sobre la vía pública "
            "frente a mi casa en el barrio Laureles, sector La Presidenta. Representa un peligro "
            "inminente para los transeúntes y los vehículos estacionados. Llamé a la línea de "
            "Medio Ambiente tres veces y nadie ha venido a evaluar la situación."
        ),
        "metadata": meta(),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=2),
    },

    # org_id=5 — Vicealcaldía de Hábitat, Movilidad, Infraestructura y Sostenibilidad
    {
        "tipo": "Peticion",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 5,
        "ciudadano": ciudadano("Diana Lopera", "43901234", "3052345678", "Femenino"),
        "ubicacion": ubicacion("Carrera 48 # 20-10", "Barrio Boston"),
        "contenido": (
            "Solicito información sobre el plan de renovación urbana del sector Boston anunciado "
            "para 2026. Los residentes no hemos sido convocados a ninguna socialización y "
            "hay rumores sobre expropiaciones. Pedimos acceso al documento técnico del proyecto "
            "y las fechas de los espacios de participación ciudadana."
        ),
        "metadata": meta("Femenino"),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=7),
    },

    # org_id=2 — Despacho del Alcalde
    {
        "tipo": "Peticion",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 2,
        "ciudadano": ciudadano("Hernán Zapata", "8045678", "3063456789"),
        "ubicacion": ubicacion("Calle 44 # 52-165"),
        "contenido": (
            "Dirijo esta petición directamente al Despacho del Alcalde porque llevo seis meses "
            "enviando solicitudes a distintas secretarías sin obtener respuesta sobre la "
            "reubicación de los vendedores informales del sector del Hueco. Solicito una reunión "
            "con el equipo de la Alcaldía para presentar la propuesta de la asociación de "
            "vendedores y buscar una solución concertada antes del 30 de mayo."
        ),
        "metadata": meta(),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=11),
    },

    # org_id=25 — Secretaría de Comunicaciones
    {
        "tipo": "Queja",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 25,
        "ciudadano": ciudadano("Camila Arango", "1067890123", "3074567890", "Femenino"),
        "ubicacion": ubicacion("Calle 33 # 74-50"),
        "contenido": (
            "La página web oficial de la Alcaldía de Medellín lleva más de dos semanas sin "
            "actualizar la sección de convocatorias públicas. Me perdí una convocatoria de "
            "empleo por confiar en la información publicada que estaba desactualizada. "
            "Solicito que la Secretaría de Comunicaciones establezca un protocolo de "
            "actualización diaria de contenidos críticos para la ciudadanía."
        ),
        "metadata": meta("Femenino"),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=3),
    },

    # org_id=10 — Secretaría de Gobierno y Gestión del Gabinete
    {
        "tipo": "Denuncia",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 10,
        "ciudadano": ciudadano("Mauricio Palacio", "71789012", "3085678901"),
        "ubicacion": ubicacion("Calle 57 # 43-120", "Parque de Bolívar"),
        "contenido": (
            "Denuncio que en el sector del Parque de Bolívar grupos de personas utilizan el "
            "espacio público para venta de estupefacientes a plena luz del día desde hace más "
            "de un mes. Los vecinos hemos llamado a la línea 123 reiteradamente sin resultado. "
            "Solicito intervención coordinada de la Secretaría de Gobierno con la Policía "
            "Nacional para recuperar el espacio público."
        ),
        "metadata": meta(),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=5),
    },

    # org_id=9 — Vicealcaldía de Creación y Desarrollo Económico
    {
        "tipo": "Sugerencia",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 9,
        "ciudadano": ciudadano("Isabela Montes", "1089012345", "3096789012", "Femenino"),
        "ubicacion": ubicacion("Carrera 65 # 74-80"),
        "contenido": (
            "Propongo que la Vicealcaldía de Creación y Desarrollo Económico cree un fondo "
            "rotatorio de capital semilla dirigido exclusivamente a emprendimientos liderados "
            "por mujeres en zonas de ladera. Actualmente los programas existentes exigen "
            "garantías que las emprendedoras de estos sectores no pueden ofrecer. Un fondo con "
            "aval comunitario podría cubrir ese vacío y generar impacto real."
        ),
        "metadata": meta("Femenino"),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=1),
    },

    # org_id=27 — Subsecretaría de Creación y Fortalecimiento Empresarial
    {
        "tipo": "Peticion",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 27,
        "ciudadano": ciudadano("Felipe Castañeda", "1012345678", "3107890123"),
        "ubicacion": ubicacion("Calle 10 # 43-20", "El Poblado"),
        "contenido": (
            "Tengo una empresa de base tecnológica con dos años de operación y tres empleadas "
            "de tiempo completo. Buscamos financiación y acompañamiento para escalar nuestra "
            "aplicación de alfabetización digital para adultos mayores. Solicito información "
            "sobre el proceso de postulación a los programas de la Subsecretaría de Creación "
            "y Fortalecimiento Empresarial y los criterios de selección aplicados."
        ),
        "metadata": meta(),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=4),
    },

    # org_id=6 — Vicealcaldía de Salud, Inclusión y Familia
    {
        "tipo": "Reclamo",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 6,
        "ciudadano": ciudadano("Rosa Elena Pérez", "22345678", "3118901234", "Femenino"),
        "ubicacion": ubicacion("Calle 92 # 80-45", "Barrio Robledo"),
        "contenido": (
            "Mi madre de 78 años con movilidad reducida lleva cuatro meses esperando la "
            "asignación de una silla de ruedas a través del programa de ayudas técnicas. "
            "En cada llamada me dicen que el pedido está en proceso pero no dan fecha. "
            "La situación afecta gravemente su calidad de vida. Solicito respuesta urgente "
            "y fecha concreta de entrega."
        ),
        "metadata": meta("Femenino", "Adulto mayor"),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=10),
    },

    # org_id=29 — Subsecretaría de Productividad, Competitividad y Relaciones Internacionales
    {
        "tipo": "Peticion",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 29,
        "ciudadano": ciudadano("Juan Sebastián Gómez", "1023890123", "3129012345"),
        "ubicacion": ubicacion("Calle 19 # 69-72", "Laureles"),
        "contenido": (
            "Represento un clúster de pequeñas empresas del sector moda y diseño que busca "
            "participar en la feria Colombiamoda 2026 con apoyo institucional. Solicitamos "
            "información sobre los convenios de cooperación internacional vigentes que puedan "
            "facilitar nuestra vinculación a compradores extranjeros y los recursos disponibles "
            "para cofinanciación de la participación ferial."
        ),
        "metadata": meta(),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=6),
    },

    # org_id=19 — Secretaría de Participación Ciudadana
    {
        "tipo": "Queja",
        "canal": "WEB",
        "anonima": False,
        "estado": "abierto",
        "organization_id": 19,
        "ciudadano": ciudadano("Alejandro Ríos", "1056234567", "3130123456"),
        "ubicacion": ubicacion("Carrera 36 # 15-40", "Barrio Manila"),
        "contenido": (
            "La Junta de Acción Comunal de nuestro barrio presentó hace cuatro meses una "
            "propuesta de presupuesto participativo para la construcción de una cancha cubierta. "
            "La propuesta cumplía todos los requisitos pero nunca fue incluida en la "
            "plataforma de votación ciudadana. Solicitamos explicación por escrito sobre "
            "los criterios de selección y la razón por la que fue excluida."
        ),
        "metadata": meta(),
        "autoriza_notificacion_correo": True,
        "respuesta": None,
        "timestamp_radicacion": ts(days_ago=8),
    },
]


# ── 3. Subir al endpoint ──────────────────────────────────────────────────────

def upload(records: list[dict]) -> None:
    print(f"\nSubiendo {len(records)} registros a {ENDPOINT}...")
    with httpx.Client(timeout=120) as client:
        resp = client.post(ENDPOINT, json=records)
        resp.raise_for_status()
        data = resp.json()
    print(f"✓ {data['count']} registros almacenados.")
    for key in data["stored_keys"]:
        print(f"  {key}")


if __name__ == "__main__":
    print("── Paso 1: Limpiando S3 ─────────────────────────────────────────")
    delete_all_curated()

    print("\n── Paso 2: Subiendo 20 curated al backend ───────────────────────")
    upload(REGISTROS)

    print("\n✓ Listo. 10 en Desarrollo Económico (org=1), 10 en otros departamentos.")
