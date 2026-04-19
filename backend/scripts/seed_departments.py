"""
Seedea la tabla departments con las 30 secretarías/subsecretarías de la Alcaldía de Medellín.
Uso: uv run python -m scripts.seed_departments
"""
import json
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DEPARTMENTS = [
  {
    "id": "despacho_alcalde",
    "name": "Despacho del Alcalde",
    "type": "SECRETARIA",
    "aliases": ["alcalde", "despacho del alcalde", "oficina del alcalde"],
    "scope": "Dirección superior de la administración municipal y representación del municipio.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_privada",
    "name": "Secretaría Privada",
    "type": "SECRETARIA",
    "aliases": ["privada", "secretaria privada"],
    "scope": "Apoyo directo al Despacho del Alcalde y coordinación de la agenda del alcalde.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "vicealcaldia_gobernabilidad_seguridad",
    "name": "Vicealcaldía de Gobernabilidad y Seguridad",
    "type": "SECRETARIA",
    "aliases": ["gobernabilidad", "seguridad", "vicealcaldia seguridad"],
    "scope": "Coordinación de políticas de gobierno, seguridad y convivencia ciudadana.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "vicealcaldia_habitat_movilidad_infraestructura_sostenibilidad",
    "name": "Vicealcaldía de Hábitat, Movilidad, Infraestructura y Sostenibilidad",
    "type": "SECRETARIA",
    "aliases": ["habitat", "movilidad", "infraestructura", "sostenibilidad"],
    "scope": "Coordinación del desarrollo físico, ambiental y de movilidad de la ciudad.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "vicealcaldia_salud_inclusion_familia",
    "name": "Vicealcaldía de Salud, Inclusión y Familia",
    "type": "SECRETARIA",
    "aliases": ["salud", "inclusion", "familia"],
    "scope": "Coordinación de políticas sociales, salud pública, familia e inclusión.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "vicealcaldia_educacion_cultura_participacion_recreacion_deporte",
    "name": "Vicealcaldía de Educación, Cultura, Participación, Recreación y Deporte",
    "type": "SECRETARIA",
    "aliases": ["educacion", "cultura", "participacion ciudadana", "recreacion", "deporte"],
    "scope": "Coordinación de educación, cultura, participación ciudadana y deporte.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "vicealcaldia_gestion_territorial",
    "name": "Vicealcaldía de Gestión Territorial",
    "type": "SECRETARIA",
    "aliases": ["gestion territorial", "territorial"],
    "scope": "Planeación y ordenamiento del territorio municipal.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "vicealcaldia_creacion_desarrollo_economico",
    "name": "Vicealcaldía de Creación y Desarrollo Económico",
    "type": "SECRETARIA",
    "aliases": ["creacion", "desarrollo economico", "vicealcaldia economica"],
    "scope": "Coordinación de políticas de desarrollo económico y fomento empresarial.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_gobierno",
    "name": "Secretaría de Gobierno y Gestión del Gabinete",
    "type": "SECRETARIA",
    "aliases": ["gobierno", "gabinete", "secretaria de gobierno"],
    "scope": "Coordinación política y relaciones con el Concejo; espacio público; orden.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_seguridad_convivencia",
    "name": "Secretaría de Seguridad y Convivencia",
    "type": "SECRETARIA",
    "aliases": ["seguridad ciudadana", "convivencia", "policia municipal"],
    "scope": "Políticas de seguridad urbana, convivencia y articulación con Policía Nacional.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_hacienda",
    "name": "Secretaría de Hacienda",
    "type": "SECRETARIA",
    "aliases": ["hacienda", "impuestos", "predial", "industria y comercio", "tesoreria"],
    "scope": "Gestión fiscal, tributaria y financiera del municipio.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_educacion",
    "name": "Secretaría de Educación",
    "type": "SECRETARIA",
    "aliases": ["educacion publica", "colegios", "instituciones educativas"],
    "scope": "Administración de la educación preescolar, básica y media en el municipio.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_salud",
    "name": "Secretaría de Salud",
    "type": "SECRETARIA",
    "aliases": ["salud publica", "hospitales", "regimen subsidiado", "sisben salud"],
    "scope": "Rectoría de la salud pública municipal y aseguramiento en salud.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_inclusion_social_familia_derechos_humanos",
    "name": "Secretaría de Inclusión Social, Familia y Derechos Humanos",
    "type": "SECRETARIA",
    "aliases": ["inclusion social", "derechos humanos", "familia", "poblacion vulnerable"],
    "scope": "Atención a poblaciones vulnerables, familia y protección de derechos humanos.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_las_mujeres",
    "name": "Secretaría de las Mujeres",
    "type": "SECRETARIA",
    "aliases": ["mujeres", "equidad de genero", "violencia de genero"],
    "scope": "Políticas de equidad de género y protección frente a violencias contra la mujer.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_juventud",
    "name": "Secretaría de la Juventud",
    "type": "SECRETARIA",
    "aliases": ["juventud", "jovenes"],
    "scope": "Políticas públicas de juventud y programas para la población joven.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_cultura_ciudadana",
    "name": "Secretaría de Cultura Ciudadana",
    "type": "SECRETARIA",
    "aliases": ["cultura", "bibliotecas", "casas de la cultura"],
    "scope": "Promoción de cultura, arte, patrimonio, lectura y convivencia cultural.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_participacion_ciudadana",
    "name": "Secretaría de Participación Ciudadana",
    "type": "SECRETARIA",
    "aliases": ["participacion", "jac", "juntas de accion comunal", "presupuesto participativo"],
    "scope": "Fomento de la participación ciudadana, JAC y presupuesto participativo.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_infraestructura_fisica",
    "name": "Secretaría de Infraestructura Física",
    "type": "SECRETARIA",
    "aliases": ["infraestructura", "obras publicas", "vias", "andenes"],
    "scope": "Construcción y mantenimiento de infraestructura pública y vial.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_movilidad",
    "name": "Secretaría de Movilidad",
    "type": "SECRETARIA",
    "aliases": ["movilidad", "transito", "licencias de conduccion", "comparendos", "semaforos"],
    "scope": "Regulación del tránsito, transporte público y movilidad urbana.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_medio_ambiente",
    "name": "Secretaría de Medio Ambiente",
    "type": "SECRETARIA",
    "aliases": ["medio ambiente", "ambiental", "arboles", "fauna"],
    "scope": "Gestión ambiental, fauna, flora urbana y calidad del aire.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_gestion_territorio",
    "name": "Secretaría de Gestión y Control Territorial",
    "type": "SECRETARIA",
    "aliases": ["control territorial", "licencias de construccion", "urbanismo"],
    "scope": "Control urbanístico, licencias de construcción y uso del suelo.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_desarrollo_economico",
    "name": "Secretaría de Desarrollo Económico",
    "type": "SECRETARIA",
    "aliases": ["desarrollo economico", "emprendimiento", "empleo", "empresas"],
    "scope": "Fomento del desarrollo económico, empleo, emprendimiento y competitividad.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_gestion_humana_servicio_ciudadania",
    "name": "Secretaría de Gestión Humana y Servicio a la Ciudadanía",
    "type": "SECRETARIA",
    "aliases": ["gestion humana", "servicio a la ciudadania", "atencion al ciudadano", "pqrsd"],
    "scope": "Gestión del talento humano municipal y atención/PQRSD a la ciudadanía.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_comunicaciones",
    "name": "Secretaría de Comunicaciones",
    "type": "SECRETARIA",
    "aliases": ["comunicaciones", "prensa"],
    "scope": "Comunicación pública institucional y relaciones con medios.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "secretaria_suministros_servicios",
    "name": "Secretaría de Suministros y Servicios",
    "type": "SECRETARIA",
    "aliases": ["suministros", "contratacion", "servicios administrativos"],
    "scope": "Adquisición de bienes y servicios y gestión logística del municipio.",
    "parent_id": None,
    "contact": {}
  },
  {
    "id": "desarrollo_economico__creacion_fortalecimiento_empresarial",
    "name": "Subsecretaría de Creación y Fortalecimiento Empresarial",
    "type": "SUBSECRETARIA",
    "aliases": ["creacion empresarial", "fortalecimiento empresarial", "emprendimiento"],
    "scope": "Apoyo a la creación y fortalecimiento de empresas y emprendedores.",
    "parent_id": "secretaria_desarrollo_economico",
    "contact": {}
  },
  {
    "id": "desarrollo_economico__banco_distrital",
    "name": "Banco Distrital de las Oportunidades",
    "type": "SUBSECRETARIA",
    "aliases": ["banco distrital", "banco de las oportunidades", "credito distrital"],
    "scope": "Acceso a microcrédito y servicios financieros para emprendedores.",
    "parent_id": "secretaria_desarrollo_economico",
    "contact": {}
  },
  {
    "id": "desarrollo_economico__productividad_competitividad",
    "name": "Subsecretaría de Productividad, Competitividad y Relaciones Internacionales",
    "type": "SUBSECRETARIA",
    "aliases": ["productividad", "competitividad", "relaciones internacionales"],
    "scope": "Promoción de productividad, competitividad y cooperación internacional.",
    "parent_id": "secretaria_desarrollo_economico",
    "contact": {}
  },
  {
    "id": "desarrollo_economico__turismo",
    "name": "Subsecretaría de Turismo",
    "type": "SUBSECRETARIA",
    "aliases": ["turismo"],
    "scope": "Promoción turística y regulación del sector turismo en Medellín.",
    "parent_id": "secretaria_desarrollo_economico",
    "contact": {}
  }
]

DEPT_ORG_ID = {
    "secretaria_desarrollo_economico": 1,
    "despacho_alcalde": 2,
    "secretaria_privada": 3,
    "vicealcaldia_gobernabilidad_seguridad": 4,
    "vicealcaldia_habitat_movilidad_infraestructura_sostenibilidad": 5,
    "vicealcaldia_salud_inclusion_familia": 6,
    "vicealcaldia_educacion_cultura_participacion_recreacion_deporte": 7,
    "vicealcaldia_gestion_territorial": 8,
    "vicealcaldia_creacion_desarrollo_economico": 9,
    "secretaria_gobierno": 10,
    "secretaria_seguridad_convivencia": 11,
    "secretaria_hacienda": 12,
    "secretaria_educacion": 13,
    "secretaria_salud": 14,
    "secretaria_inclusion_social_familia_derechos_humanos": 15,
    "secretaria_las_mujeres": 16,
    "secretaria_juventud": 17,
    "secretaria_cultura_ciudadana": 18,
    "secretaria_participacion_ciudadana": 19,
    "secretaria_infraestructura_fisica": 20,
    "secretaria_movilidad": 21,
    "secretaria_medio_ambiente": 22,
    "secretaria_gestion_territorio": 23,
    "secretaria_gestion_humana_servicio_ciudadania": 24,
    "secretaria_comunicaciones": 25,
    "secretaria_suministros_servicios": 26,
    "desarrollo_economico__creacion_fortalecimiento_empresarial": 27,
    "desarrollo_economico__banco_distrital": 28,
    "desarrollo_economico__productividad_competitividad": 29,
    "desarrollo_economico__turismo": 30,
}

SQL = """
INSERT INTO departments (id, name, type, aliases, scope, parent_id, contact, organization_id)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (id) DO UPDATE SET
    name            = EXCLUDED.name,
    type            = EXCLUDED.type,
    aliases         = EXCLUDED.aliases,
    scope           = EXCLUDED.scope,
    parent_id       = EXCLUDED.parent_id,
    contact         = EXCLUDED.contact,
    organization_id = EXCLUDED.organization_id;
"""

def main():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()

    # Insertar primero los que no tienen parent (para respetar la FK)
    ordered = [d for d in DEPARTMENTS if d["parent_id"] is None] + \
              [d for d in DEPARTMENTS if d["parent_id"] is not None]

    for d in ordered:
        cur.execute(SQL, (
            d["id"],
            d["name"],
            d["type"],
            d["aliases"],
            d["scope"],
            d["parent_id"],
            json.dumps(d["contact"], ensure_ascii=False),
            DEPT_ORG_ID[d["id"]],
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"✓ {len(DEPARTMENTS)} departamentos insertados/actualizados.")

if __name__ == "__main__":
    main()
