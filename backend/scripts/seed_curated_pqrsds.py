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


def radicado(n: int) -> str:
    return f"MDE-{n:05d}"


def ts(days_ago: int = 0) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


REGISTROS = [
    {
        "radicado": radicado(1),
        "timestamp_radicacion": ts(4),
        "canal": "PORTAL",
        "anonima": False,
        "ciudadano": {
            "tipo_persona": "natural",
            "tipo_documento": "cedula_ciudadania",
            "numero_documento": "71845632",
            "nombres": "Carlos Andrés",
            "apellidos": "Mendoza Restrepo",
            "genero": "masculino",
            "pais": "Colombia",
            "departamento": "Antioquia",
            "ciudad": "Medellín",
            "direccion": "Calle 50 # 40-20, Apto 301, Laureles",
            "correo_electronico": "camendoza@gmail.com",
            "telefono": "+573142981045",
        },
        "asunto_principal": "peticion",
        "atencion_preferencial": "ninguna",
        "autoriza_notificacion_correo": True,
        "descripcion_detallada": (
            "Me dirijo a la Secretaría de Desarrollo Económico para solicitar información detallada sobre "
            "los programas de financiación disponibles para microempresarios del sector panadero. "
            "Soy propietario de una panadería artesanal con cinco años de operación en el barrio Laureles "
            "y deseo acceder a crédito para adquirir un horno de mayor capacidad. Quisiera conocer los "
            "requisitos, tasas de interés vigentes, plazos máximos y las entidades aliadas con la Alcaldía "
            "para este tipo de financiación. Quedo atento a su respuesta."
        ),
        "metadata": {"post_id": None, "created_time": ts(4)},
    },
    {
        "radicado": radicado(2),
        "timestamp_radicacion": ts(3),
        "canal": "MAIL",
        "anonima": False,
        "ciudadano": {
            "tipo_persona": "natural",
            "tipo_documento": "cedula_ciudadania",
            "numero_documento": "43892017",
            "nombres": "Valentina",
            "apellidos": "Torres Gómez",
            "genero": "femenino",
            "pais": "Colombia",
            "departamento": "Antioquia",
            "ciudad": "Medellín",
            "direccion": "Carrera 80 # 33-15, El Poblado",
            "correo_electronico": "v.torres@outlook.com",
            "telefono": "+573008871234",
        },
        "asunto_principal": "denuncia",
        "atencion_preferencial": "ninguna",
        "autoriza_notificacion_correo": True,
        "descripcion_detallada": (
            "Por medio del presente correo electrónico presento denuncia formal por presuntas irregularidades "
            "en la adjudicación de contratos de capacitación empresarial de la Subsecretaría de Creación y "
            "Fortalecimiento Empresarial durante el primer trimestre de 2026. Según información de dominio "
            "público, los contratos fueron asignados sin licitación pública a una empresa cuyo representante "
            "legal tiene vínculos familiares con un funcionario de planta de dicha dependencia. Solicito la "
            "apertura de una investigación formal y me pongo a disposición para aportar pruebas documentales."
        ),
        "metadata": {"post_id": None, "created_time": ts(3)},
    },
    {
        "radicado": radicado(3),
        "timestamp_radicacion": ts(2),
        "canal": "FB_DM",
        "anonima": False,
        "ciudadano": {
            "tipo_persona": "natural",
            "tipo_documento": "cedula_extranjeria",
            "numero_documento": "CE-8821045",
            "nombres": "María Alejandra",
            "apellidos": "Suárez Vargas",
            "genero": "femenino",
            "pais": "Venezuela",
            "departamento": "Antioquia",
            "ciudad": "Medellín",
            "direccion": "Calle 30 # 65-40, Belén",
            "correo_electronico": "msuarez.ve@gmail.com",
            "telefono": "+573214456789",
            "id_meta": "fb_10231",
        },
        "asunto_principal": "queja",
        "atencion_preferencial": "victima_conflicto",
        "autoriza_notificacion_correo": True,
        "descripcion_detallada": (
            "Presento queja formal por la atención recibida en el Centro de Emprendimiento de la Alpujarra "
            "el pasado 14 de abril. Asistí a solicitar orientación sobre formalización de mi negocio de "
            "confecciones y el funcionario de turno me informó que los programas de apoyo no aplican para "
            "personas con cédula de extranjería, lo cual considero discriminatorio e inexacto según la "
            "normatividad vigente. Solicito aclaración oficial sobre si los programas son accesibles para "
            "migrantes con permiso de permanencia y que se capacite adecuadamente al personal de atención."
        ),
        "metadata": {"post_id": "fb_post_092", "created_time": ts(2)},
    },
    {
        "radicado": radicado(4),
        "timestamp_radicacion": ts(1),
        "canal": "IG_DM",
        "anonima": False,
        "ciudadano": {
            "tipo_persona": "juridica",
            "tipo_documento": "nit",
            "numero_documento": "900.441.821-7",
            "nombres": "TechGirls",
            "apellidos": "SAS",
            "genero": "prefiero_no_decirlo",
            "pais": "Colombia",
            "departamento": "Antioquia",
            "ciudad": "Medellín",
            "direccion": "Calle 10 # 43E-31, El Poblado",
            "correo_electronico": "contacto@techgirls.co",
            "telefono": "+576042881100",
            "id_meta": "ig_40078",
        },
        "asunto_principal": "solicitud",
        "atencion_preferencial": "ninguna",
        "autoriza_notificacion_correo": True,
        "descripcion_detallada": (
            "En representación de TechGirls SAS, startup de tecnología educativa fundada por mujeres, "
            "solicitamos información sobre convocatorias de capital semilla disponibles para empresas de "
            "base tecnológica en etapa de crecimiento. Llevamos dos años de operación, contamos con tres "
            "empleadas de tiempo completo y buscamos financiación para el desarrollo de nuestra aplicación "
            "de alfabetización digital para adultos mayores. Queremos saber si existen programas específicos "
            "para empresas lideradas por mujeres y cuáles son los criterios de elegibilidad y fechas de "
            "las próximas convocatorias."
        ),
        "metadata": {"post_id": None, "created_time": ts(1)},
    },
    {
        "radicado": radicado(5),
        "timestamp_radicacion": ts(0),
        "canal": "PORTAL",
        "anonima": False,
        "ciudadano": {
            "tipo_persona": "natural",
            "tipo_documento": "cedula_ciudadania",
            "numero_documento": "98654320",
            "nombres": "Jorge Iván",
            "apellidos": "Ospina Cardona",
            "genero": "masculino",
            "pais": "Colombia",
            "departamento": "Antioquia",
            "ciudad": "Medellín",
            "direccion": "Transversal 39 # 72-18, Robledo",
            "correo_electronico": "jospina.robledo@gmail.com",
            "telefono": "+573015672891",
        },
        "asunto_principal": "reclamo",
        "atencion_preferencial": "adulto_mayor",
        "autoriza_notificacion_correo": False,
        "descripcion_detallada": (
            "Presento reclamo formal por cobro indebido realizado en la ventanilla de atención al ciudadano "
            "del Centro de Servicios Laureles el día 10 de abril de 2026. Me cobraron la suma de cuarenta y "
            "cinco mil pesos ($45.000) por la expedición de un certificado de actividad económica, trámite "
            "que según la Resolución Municipal 0234 de 2025 es completamente gratuito. Adjunto copia del "
            "recibo de pago con número de transacción 20260410-8821. Solicito la devolución del valor cobrado "
            "de forma indebida y que se tomen medidas correctivas con el funcionario responsable."
        ),
        "metadata": {"post_id": None, "created_time": ts(0)},
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
        radicado_val = reg["radicado"]
        asunto = reg["asunto_principal"].upper()
        canal = reg["canal"]
        ciudadano = reg["ciudadano"]
        nombre = f"{ciudadano['nombres']} {ciudadano['apellidos']}"
        print(f"    [{radicado_val}] [{asunto:<10}] [{canal:<8}] {nombre}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
