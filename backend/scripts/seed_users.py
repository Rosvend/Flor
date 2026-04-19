"""
Seedea usuarios de prueba conectados a departamentos via organization_id.

Mapeo fijo (reproducible):
  organization_id 1  → secretaria_desarrollo_economico  (default del sistema)
  organization_id 2+ → demás departamentos en orden de la lista

Crea:
  - 5 usuarios en secretaria_desarrollo_economico (org_id=1)
  - 1 usuario en cada uno de 10 departamentos escogidos al azar

Uso: uv run python -m scripts.seed_users
"""
import os
import random
import uuid

import psycopg2
from dotenv import load_dotenv
import bcrypt

load_dotenv()

# ── Mapeo departamento → organization_id ────────────────────────────────────
# secretaria_desarrollo_economico siempre es org_id=1 (coincide con los datos existentes)
DEPT_ORG_MAP: dict[str, int] = {
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

DEPT_LABEL: dict[str, str] = {
    "secretaria_desarrollo_economico": "DesarrolloEconomico",
    "despacho_alcalde": "Alcalde",
    "secretaria_privada": "Privada",
    "vicealcaldia_gobernabilidad_seguridad": "Gobernabilidad",
    "vicealcaldia_habitat_movilidad_infraestructura_sostenibilidad": "Habitat",
    "vicealcaldia_salud_inclusion_familia": "SaludInclusion",
    "vicealcaldia_educacion_cultura_participacion_recreacion_deporte": "Educacion",
    "vicealcaldia_gestion_territorial": "GestionTerritorial",
    "vicealcaldia_creacion_desarrollo_economico": "ViceEconomica",
    "secretaria_gobierno": "Gobierno",
    "secretaria_seguridad_convivencia": "Seguridad",
    "secretaria_hacienda": "Hacienda",
    "secretaria_educacion": "SecEducacion",
    "secretaria_salud": "Salud",
    "secretaria_inclusion_social_familia_derechos_humanos": "Inclusion",
    "secretaria_las_mujeres": "Mujeres",
    "secretaria_juventud": "Juventud",
    "secretaria_cultura_ciudadana": "Cultura",
    "secretaria_participacion_ciudadana": "Participacion",
    "secretaria_infraestructura_fisica": "Infraestructura",
    "secretaria_movilidad": "Movilidad",
    "secretaria_medio_ambiente": "MedioAmbiente",
    "secretaria_gestion_territorio": "ControlTerritorial",
    "secretaria_gestion_humana_servicio_ciudadania": "GestionHumana",
    "secretaria_comunicaciones": "Comunicaciones",
    "secretaria_suministros_servicios": "Suministros",
    "desarrollo_economico__creacion_fortalecimiento_empresarial": "Emprendimiento",
    "desarrollo_economico__banco_distrital": "BancoDistrital",
    "desarrollo_economico__productividad_competitividad": "Productividad",
    "desarrollo_economico__turismo": "Turismo",
}

INSERT_SQL = """
INSERT INTO users (id, nombre, correo_electronico, password_hash, organization_id)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (correo_electronico) DO UPDATE SET
    nombre          = EXCLUDED.nombre,
    password_hash   = EXCLUDED.password_hash,
    organization_id = EXCLUDED.organization_id;
"""

DEFAULT_PASSWORD = "Flor2026!"

def make_user(nombre: str, correo: str, org_id: int) -> tuple:
    return (
        str(uuid.uuid4()),
        nombre,
        correo,
        bcrypt.hashpw(DEFAULT_PASSWORD.encode(), bcrypt.gensalt()).decode(),
        org_id,
    )

def main():
    random.seed(42)  # reproducible

    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()

    users: list[tuple] = []

    # ── 5 usuarios de Secretaría de Desarrollo Económico (org_id=1) ──────────
    for i in range(1, 6):
        label = DEPT_LABEL["secretaria_desarrollo_economico"]
        correo = f"funcionario{i}.{label.lower()}@medellin.gov.co"
        nombre = f"Funcionario {i} – Desarrollo Económico"
        users.append(make_user(nombre, correo, 1))

    # ── 1 usuario por cada uno de 10 departamentos al azar ───────────────────
    otros_depts = [d for d in DEPT_ORG_MAP if d != "secretaria_desarrollo_economico"]
    seleccionados = random.sample(otros_depts, 10)

    for dept_id in seleccionados:
        org_id = DEPT_ORG_MAP[dept_id]
        label  = DEPT_LABEL[dept_id]
        correo = f"funcionario.{label.lower()}@medellin.gov.co"
        nombre = f"Funcionario – {label}"
        users.append(make_user(nombre, correo, org_id))

    for u in users:
        cur.execute(INSERT_SQL, u)

    conn.commit()
    cur.close()
    conn.close()

    print(f"✓ {len(users)} usuarios insertados/actualizados. Contraseña: {DEFAULT_PASSWORD}")
    print()
    print("Departamentos seleccionados al azar:")
    for dept_id in seleccionados:
        print(f"  org_id={DEPT_ORG_MAP[dept_id]:2d}  {dept_id}")
    print()
    print("Usuarios Desarrollo Económico (org_id=1):")
    for i in range(1, 6):
        print(f"  funcionario{i}.desarrolloeconomico@medellin.gov.co")

if __name__ == "__main__":
    main()
