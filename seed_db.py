import random
from datetime import datetime
from faker import Faker
import mysql.connector
import psycopg2

# ==============================================================================
# PROVIDERS DE FAKER UTILIZADOS EN ESTE SCRIPT:
# 1. fake.name()                  -> Nombres del personal
# 2. fake.last_name()             -> Apellidos del personal
# 3. fake.email()                 -> Correos electrónicos
# 4. fake.phone_number()          -> Teléfonos de contacto
# 5. fake.company()               -> Nombre de empresas
# 6. fake.bothify()               -> Códigos únicos de inventario y facturas
# 7. fake.date_between()          -> Fechas de adquisición, intervención y facturas
# 8. fake.date_time_between()     -> Fechas y horas de reportes de incidencias
# 9. fake.random_element()        -> Selección de roles, prioridades y estados
# 10. fake.random_int()           -> Capacidades de aulas y vidas útiles
# 11. fake.pydecimal()            -> Costes exactos con decimales
# 12. fake.sentence()             -> Conceptos, motivos y descripciones
# ==============================================================================

fake = Faker('es_ES')

# Configuraciones de conexión.
CONFIG_MYSQL = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "rootpassword",
    "database": "gestion_instituto"
}

CONFIG_MARIADB = {
    "host": "localhost",
    "port": 3307,
    "user": "root",
    "password": "rootpassword",
    "database": "gestion_instituto"
}

CONFIG_POSTGRES = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "rootpassword",
    "database": "gestion_instituto"
}

# Función principal de inserción de datos sintéticos.
def seed_database(cursor, is_postgres=False):
    ph = "%s" if is_postgres else "%s"

    # 1. Aulas_Instalaciones
    aulas_ids = []
    for i in range(1, 11):
        nombre = f"Aula {100 + i}"
        ubicacion = f"Planta {fake.random_int(min=0, max=3)}"
        capacidad = fake.random_int(min=15, max=40)
        query = f"INSERT INTO Aulas_Instalaciones (nombre, ubicacion, capacidad) VALUES ({ph}, {ph}, {ph})"
        cursor.execute(query, (nombre, ubicacion, capacidad))
        aulas_ids.append(cursor.lastrowid if hasattr(cursor, 'lastrowid') and cursor.lastrowid else i)

    # 2. Categorias_Material
    categorias_ids = []
    categorias = ["Informática", "Audiovisual", "Mobiliario", "Laboratorio", "Deportes"]
    for cat in categorias:
        vida_util = fake.random_int(min=24, max=120)
        query = f"INSERT INTO Categorias_Material (nombre_categoria, vida_util_estimada_meses) VALUES ({ph}, {ph})"
        cursor.execute(query, (cat, vida_util))
        categorias_ids.append(cursor.lastrowid if hasattr(cursor, 'lastrowid') and cursor.lastrowid else len(categorias_ids) + 1)

    # 3. Personal_Centro
    personal_ids = []
    roles = ["Profesor", "Administrativo", "Técnico IT", "Conserje", "Directivo"]
    for _ in range(15):
        nombre = fake.name()
        apellidos = fake.last_name() + " " + fake.last_name()
        rol = fake.random_element(elements=roles)
        telefono = fake.phone_number()[:20]
        email = fake.email()
        query = f"INSERT INTO Personal_Centro (nombre, apellidos, rol, telefono, email) VALUES ({ph}, {ph}, {ph}, {ph}, {ph})"
        cursor.execute(query, (nombre, apellidos, rol, telefono, email))
        personal_ids.append(cursor.lastrowid if hasattr(cursor, 'lastrowid') and cursor.lastrowid else len(personal_ids) + 1)

    # 4. Proveedores
    proveedores_ids = []
    for _ in range(8):
        empresa = fake.company()
        telefono = fake.phone_number()[:20]
        email = fake.email()
        query = f"INSERT INTO Proveedores (nombre_empresa, telefono, email_contacto) VALUES ({ph}, {ph}, {ph})"
        cursor.execute(query, (empresa, telefono, email))
        proveedores_ids.append(cursor.lastrowid if hasattr(cursor, 'lastrowid') and cursor.lastrowid else len(proveedores_ids) + 1)

    # 5. Materiales_Equipos
    materiales_ids = []
    estados = ["Nuevo", "Bueno", "Regular", "Mal estado"]
    for i in range(25):
        codigo = fake.bothify(text="MAT-####-??").upper()
        cat_id = random.choice(categorias_ids)
        aula_id = random.choice(aulas_ids)
        fecha_adq = fake.date_between(start_date='-3y', end_date='today')
        coste = float(fake.pydecimal(left_digits=3, right_digits=2, positive=True, min_value=50, max_value=800))
        estado = fake.random_element(elements=estados)
        query = f"INSERT INTO Materiales_Equipos (codigo_inventario, id_categoria, id_aula_actual, fecha_adquisicion, coste_compra, estado_conservacion) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})"
        cursor.execute(query, (codigo, cat_id, aula_id, fecha_adq, coste, estado))
        materiales_ids.append(cursor.lastrowid if hasattr(cursor, 'lastrowid') and cursor.lastrowid else i + 1)

    # 6. Horarios_Uso_Aulas
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    for _ in range(15):
        aula_id = random.choice(aulas_ids)
        resp_id = random.choice(personal_ids)
        dia = fake.random_element(elements=dias)
        h_inicio = f"{random.randint(8, 14):02d}:00:00"
        h_fin = f"{int(h_inicio[:2]) + 2:02d}:00:00"
        actividad = fake.sentence(nb_words=3)
        query = f"INSERT INTO Horarios_Uso_Aulas (id_aula, id_responsable, dia_semana, hora_inicio, hora_fin, actividad_o_asignatura) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})"
        cursor.execute(query, (aula_id, resp_id, dia, h_inicio, h_fin, actividad))

    # 7. Bajas_Material
    bajas_mat_ids = random.sample(materiales_ids, k=3)
    for mat_id in bajas_mat_ids:
        personal_id = random.choice(personal_ids)
        fecha_baja = fake.date_between(start_date='-1y', end_date='today')
        motivo = fake.sentence(nb_words=5)
        coste_rec = float(fake.pydecimal(left_digits=2, right_digits=2, min_value=0, max_value=50))
        query = f"INSERT INTO Bajas_Material (id_material, id_autorizado_por, fecha_baja, motivo_baja, coste_reciclaje) VALUES ({ph}, {ph}, {ph}, {ph}, {ph})"
        cursor.execute(query, (mat_id, personal_id, fecha_baja, motivo, coste_rec))

    # 8. Incidencias_Averias
    incidencias_ids = []
    prioridades = ["Baja", "Media", "Alta", "Crítica"]
    estados_inc = ["Pendiente", "En proceso", "Resuelta"]
    for _ in range(12):
        mat_id = random.choice(materiales_ids)
        aula_id = random.choice(aulas_ids)
        persona_id = random.choice(personal_ids)
        fecha_rep = fake.date_time_between(start_date='-6m', end_date='now')
        desc = fake.sentence(nb_words=8)
        prioridad = fake.random_element(elements=prioridades)
        estado = fake.random_element(elements=estados_inc)
        query = f"INSERT INTO Incidencias_Averias (id_material, id_aula, id_reportado_por, fecha_reporte, descripcion_texto, prioridad, estado) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})"
        cursor.execute(query, (mat_id, aula_id, persona_id, fecha_rep, desc, prioridad, estado))
        incidencias_ids.append(cursor.lastrowid if hasattr(cursor, 'lastrowid') and cursor.lastrowid else len(incidencias_ids) + 1)

    # 9. Mantenimientos_Reparaciones
    mantenimientos_ids = []
    tipos_mant = ["Preventivo", "Correctivo", "Sustitución"]
    for _ in range(8):
        inc_id = random.choice(incidencias_ids)
        mat_id = random.choice(materiales_ids)
        prov_id = random.choice(proveedores_ids)
        fecha_int = fake.date_between(start_date='-5m', end_date='today')
        tipo = fake.random_element(elements=tipos_mant)
        desc_trabajo = fake.sentence(nb_words=6)
        query = f"INSERT INTO Mantenimientos_Reparaciones (id_incidencia, id_material, id_proveedor, fecha_intervencion, tipo, descripcion_trabajo) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})"
        cursor.execute(query, (inc_id, mat_id, prov_id, fecha_int, tipo, desc_trabajo))
        mantenimientos_ids.append(cursor.lastrowid if hasattr(cursor, 'lastrowid') and cursor.lastrowid else len(mantenimientos_ids) + 1)

    # 10. Facturas_Gastos
    for _ in range(10):
        mant_id = random.choice(mantenimientos_ids) if random.choice([True, False]) else None
        mat_comprado_id = random.choice(materiales_ids) if not mant_id else None
        prov_id = random.choice(proveedores_ids)
        num_factura = fake.bothify(text="FAC-2024-#####")
        concepto = fake.sentence(nb_words=4)
        importe = float(fake.pydecimal(left_digits=4, right_digits=2, min_value=100, max_value=1500))
        fecha_emision = fake.date_between(start_date='-4m', end_date='today')
        query = f"INSERT INTO Facturas_Gastos (id_mantenimiento, id_material_comprado, id_proveedor, numero_factura, concepto, importe_total, fecha_emision) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})"
        cursor.execute(query, (mant_id, mat_comprado_id, prov_id, num_factura, concepto, importe, fecha_emision))

# Gestión ciclo de conexiones.
def run_seed():

    # MySQL
    print("Poblando MySQL...")
    conn = mysql.connector.connect(**CONFIG_MYSQL)
    cursor = conn.cursor()
    seed_database(cursor, is_postgres=False)
    conn.commit()
    cursor.close()
    conn.close()

    # MariaDB
    print("Poblando MariaDB...")
    conn = mysql.connector.connect(**CONFIG_MARIADB)
    cursor = conn.cursor()
    seed_database(cursor, is_postgres=False)
    conn.commit()
    cursor.close()
    conn.close()

    # PostgreSQL
    print("Poblando PostgreSQL...")
    conn = psycopg2.connect(**CONFIG_POSTGRES)
    cursor = conn.cursor()
    seed_database(cursor, is_postgres=True)
    conn.commit()
    cursor.close()
    conn.close()

    print("Población completada con éxito en las 3 bases de datos.")


if __name__ == "__main__":
    run_seed()