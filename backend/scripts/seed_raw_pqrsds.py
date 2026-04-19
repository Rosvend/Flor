"""
Genera 10 PQRSD raw variadas y las carga al endpoint /api/v1/ingest/raw.
Uso: python -m scripts.seed_raw_pqrsds [--url http://localhost:8000]
"""

import sys
import json
from datetime import datetime, timezone, timedelta
import random
import httpx
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = sys.argv[2] if "--url" in sys.argv else "http://localhost:8000"
ENDPOINT = f"{BACKEND_URL}/api/v1/ingest/raw"

CANALES = ["FB_DM", "IG_DM", "MAIL"]


def _ts(days_ago: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat()


REGISTROS = [
    {
        "canal": "FB_DM",
        "usuario": {"nombre": "Carlos Mendoza", "id_meta": "fb_10001"},
        "contenido": (
            "Buenos días, me dirijo a ustedes para solicitar información sobre los programas de emprendimiento "
            "que ofrece la Secretaría de Desarrollo Económico. Soy dueño de una pequeña panadería en el barrio "
            "Laureles y me gustaría acceder a capacitaciones y posibles líneas de crédito para expandir mi negocio. "
            "¿Cuáles son los requisitos y cómo puedo inscribirme? Quedo pendiente de su respuesta."
        ),
        "metadata": {"post_id": "fb_post_001", "created_time": _ts(0)},
    },
    {
        "canal": "IG_DM",
        "usuario": {"nombre": None, "id_meta": "ig_anon_20023"},
        "contenido": (
            "Llevo tres meses esperando una respuesta a mi solicitud de subsidio para mi microempresa de confecciones. "
            "Radiqué el caso en febrero y nadie me ha contestado. El número de radicado es 2026-FEB-04421. "
            "Esto es una falta de respeto con los ciudadanos que confiamos en las instituciones. Exijo una respuesta "
            "formal y un plazo claro de resolución."
        ),
        "metadata": {"post_id": None, "created_time": _ts(1)},
    },
    {
        "canal": "MAIL",
        "usuario": {"nombre": "Valentina Torres", "id_meta": None},
        "contenido": (
            "Estimados, por medio del presente correo quiero denunciar una presunta irregularidad en la adjudicación "
            "de contratos de la Subsecretaría de Creación y Fortalecimiento Empresarial. Se rumorea que los contratos "
            "de capacitación del primer trimestre se asignaron sin licitación pública a una empresa vinculada a un "
            "funcionario. Solicito que se abra una investigación formal y se me informe sobre el procedimiento."
        ),
        "metadata": {"post_id": None, "created_time": _ts(1)},
    },
    {
        "canal": "FB_DM",
        "usuario": {"nombre": "Andrés Felipe Ríos", "id_meta": "fb_10045"},
        "contenido": (
            "Buenas tardes. Quiero sugerir que la Alcaldía implemente un mercado digital donde los emprendedores "
            "locales puedan vender sus productos sin intermediarios. He visto modelos similares en Bogotá y Cali "
            "que han tenido muy buenos resultados. Creo que esto podría generar empleo y visibilidad para los "
            "pequeños negocios de Medellín. Quedo atento a si existe algún canal para formalizar esta propuesta."
        ),
        "metadata": {"post_id": "fb_post_002", "created_time": _ts(2)},
    },
    {
        "canal": "IG_DM",
        "usuario": {"nombre": "Luisa Carmona", "id_meta": "ig_30078"},
        "contenido": (
            "Hice un curso de panadería artesanal con el programa Medellín Emprende en enero de este año. "
            "El instructor llegaba tarde constantemente, el material prometido nunca se entregó completo y el local "
            "donde se realizaron las clases no tenía condiciones adecuadas de ventilación. Quiero presentar una "
            "queja formal por la baja calidad del servicio y pedir que se evalúe a los proveedores antes de renovar "
            "contratos con ellos."
        ),
        "metadata": {"post_id": None, "created_time": _ts(2)},
    },
    {
        "canal": "MAIL",
        "usuario": {"nombre": "Jorge Iván Ospina", "id_meta": None},
        "contenido": (
            "Señores Alcaldía, me permito reclamar por el cobro indebido que me realizaron en la ventanilla del "
            "Centro de Servicio al Ciudadano de Laureles el pasado 10 de abril. Me cobraron $45.000 por un trámite "
            "que según la resolución 0234 de 2025 es completamente gratuito. Adjunto copia del recibo. "
            "Solicito la devolución del dinero y que se capacite mejor al personal encargado."
        ),
        "metadata": {"post_id": None, "created_time": _ts(3)},
    },
    {
        "canal": "FB_DM",
        "usuario": {"nombre": None, "id_meta": "fb_anon_50091"},
        "contenido": (
            "Necesito saber si hay convocatorias abiertas para capital semilla dirigidas a mujeres emprendedoras "
            "en el sector de tecnología. Tengo una startup de dos años con tres empleadas y estamos buscando "
            "financiación para desarrollar nuestra aplicación móvil. ¿Existe algún programa específico para "
            "empresas de base tecnológica lideradas por mujeres? Por favor indiquen requisitos y fechas límite."
        ),
        "metadata": {"post_id": "fb_post_003", "created_time": _ts(4)},
    },
    {
        "canal": "IG_DM",
        "usuario": {"nombre": "Sebastián Guerrero", "id_meta": "ig_40012"},
        "contenido": (
            "Les escribo para quejarme del trato recibido por parte de un servidor público en la oficina de "
            "Emprendimiento de la Alpujarra el día 15 de abril. La funcionaria de nombre Sandra fue grosera, "
            "me interrumpió varias veces y me dijo que mi proyecto no tenía futuro sin haberlo revisado. "
            "Este tipo de actitudes desaniman a los ciudadanos. Espero que se tomen medidas correctivas."
        ),
        "metadata": {"post_id": None, "created_time": _ts(5)},
    },
    {
        "canal": "MAIL",
        "usuario": {"nombre": "María Cecilia Londoño", "id_meta": None},
        "contenido": (
            "Cordial saludo. Solicito información actualizada sobre los convenios vigentes entre la Secretaría "
            "de Desarrollo Económico y el Banco Distrital para créditos a microempresarios del sector informal. "
            "Específicamente necesito saber tasas de interés, montos máximos, plazos y documentación requerida. "
            "Tengo un negocio de arepas en Ciudad del Río y quisiera formalizar mi empresa con apoyo institucional."
        ),
        "metadata": {"post_id": None, "created_time": _ts(6)},
    },
    {
        "canal": "FB_DM",
        "usuario": {"nombre": "Ricardo Palacio", "id_meta": "fb_10099"},
        "contenido": (
            "Quiero sugerir que los talleres de emprendimiento se realicen también en horarios nocturnos o los "
            "fines de semana, ya que muchos de nosotros tenemos trabajos de tiempo completo y no podemos asistir "
            "entre semana. Actualmente los programas de la Alcaldía están diseñados para personas que no trabajan "
            "en jornada completa, lo cual excluye a quienes queremos emprender como segunda actividad económica."
        ),
        "metadata": {"post_id": "fb_post_004", "created_time": _ts(7)},
    },
]


def main():
    # Parchar timestamps en tiempo de ejecución
    for i, r in enumerate(REGISTROS):
        r["metadata"]["created_time"] = _ts(i % 8)

    print(f"\n{'='*55}")
    print(f"  Seed raw PQRSDs → {ENDPOINT}")
    print(f"{'='*55}")
    print(f"  Registros a enviar: {len(REGISTROS)}")

    resp = httpx.post(ENDPOINT, json=REGISTROS, timeout=30)
    resp.raise_for_status()
    result = resp.json()

    stored_keys = result["stored_keys"]
    print(f"  ✓ {len(stored_keys)} registros almacenados:\n")
    for key, reg in zip(stored_keys, REGISTROS):
        canal = reg["canal"]
        contenido = reg["contenido"][:55]
        print(f"    [{canal:<7}] {key[:30]}... | \"{contenido}\"")

    print(f"\n{'='*55}\n")


if __name__ == "__main__":
    main()
