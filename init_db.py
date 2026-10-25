import mysql.connector
import psycopg2

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

# Generación sentencias DDL para la creación de tablas.
def get_ddl_queries(is_postgres=False):
    pk_type = "SERIAL PRIMARY KEY" if is_postgres else "INT AUTO_INCREMENT PRIMARY KEY"
    
    return [
        f"""
        CREATE TABLE IF NOT EXISTS Aulas_Instalaciones (
            id_aula {pk_type},
            nombre VARCHAR(100) NOT NULL,
            ubicacion VARCHAR(100),
            capacidad INT
        );
        """,
        f"""
        CREATE TABLE IF NOT EXISTS Categorias_Material (
            id_categoria {pk_type},
            nombre_categoria VARCHAR(100) NOT NULL,
            vida_util_estimada_meses INT
        );
        """,
        f"""
        CREATE TABLE IF NOT EXISTS Personal_Centro (
            id_personal {pk_type},
            nombre VARCHAR(100) NOT NULL,
            apellidos VARCHAR(100) NOT NULL,
            rol VARCHAR(50) NOT NULL,
            telefono VARCHAR(20),
            email VARCHAR(100) UNIQUE
        );
        """,
        f"""
        CREATE TABLE IF NOT EXISTS Proveedores (
            id_proveedor {pk_type},
            nombre_empresa VARCHAR(150) NOT NULL,
            telefono VARCHAR(20),
            email_contacto VARCHAR(100)
        );
        """,
        f"""
        CREATE TABLE IF NOT EXISTS Materiales_Equipos (
            id_material {pk_type},
            codigo_inventario VARCHAR(50) UNIQUE NOT NULL,
            id_categoria INT NOT NULL,
            id_aula_actual INT NOT NULL,
            fecha_adquisicion DATE NOT NULL,
            coste_compra DECIMAL(10,2) NOT NULL,
            estado_conservacion VARCHAR(30) DEFAULT 'Nuevo',
            FOREIGN KEY (id_categoria) REFERENCES Categorias_Material(id_categoria),
            FOREIGN KEY (id_aula_actual) REFERENCES Aulas_Instalaciones(id_aula)
        );
        """,
        f"""
        CREATE TABLE IF NOT EXISTS Horarios_Uso_Aulas (
            id_horario {pk_type},
            id_aula INT NOT NULL,
            id_responsable INT NOT NULL,
            dia_semana VARCHAR(15) NOT NULL,
            hora_inicio TIME NOT NULL,
            hora_fin TIME NOT NULL,
            actividad_o_asignatura VARCHAR(100),
            FOREIGN KEY (id_aula) REFERENCES Aulas_Instalaciones(id_aula),
            FOREIGN KEY (id_responsable) REFERENCES Personal_Centro(id_personal)
        );
        """,
        f"""
        CREATE TABLE IF NOT EXISTS Bajas_Material (
            id_baja {pk_type},
            id_material INT NOT NULL,
            id_autorizado_por INT NOT NULL,
            fecha_baja DATE NOT NULL,
            motivo_baja VARCHAR(100) NOT NULL,
            coste_reciclaje DECIMAL(10,2) DEFAULT 0.00,
            FOREIGN KEY (id_material) REFERENCES Materiales_Equipos(id_material),
            FOREIGN KEY (id_autorizado_por) REFERENCES Personal_Centro(id_personal)
        );
        """,
        f"""
        CREATE TABLE IF NOT EXISTS Incidencias_Averias (
            id_incidencia {pk_type},
            id_material INT NULL,
            id_aula INT NOT NULL,
            id_reportado_por INT NOT NULL,
            fecha_reporte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            descripcion_texto TEXT NOT NULL,
            prioridad VARCHAR(20) DEFAULT 'Media',
            estado VARCHAR(20) DEFAULT 'Pendiente',
            FOREIGN KEY (id_material) REFERENCES Materiales_Equipos(id_material),
            FOREIGN KEY (id_aula) REFERENCES Aulas_Instalaciones(id_aula),
            FOREIGN KEY (id_reportado_por) REFERENCES Personal_Centro(id_personal)
        );
        """,
        f"""
        CREATE TABLE IF NOT EXISTS Mantenimientos_Reparaciones (
            id_mantenimiento {pk_type},
            id_incidencia INT NULL,
            id_material INT NOT NULL,
            id_proveedor INT NOT NULL,
            fecha_intervencion DATE NOT NULL,
            tipo VARCHAR(30) NOT NULL,
            descripcion_trabajo VARCHAR(200) NULL,
            FOREIGN KEY (id_incidencia) REFERENCES Incidencias_Averias(id_incidencia),
            FOREIGN KEY (id_material) REFERENCES Materiales_Equipos(id_material),
            FOREIGN KEY (id_proveedor) REFERENCES Proveedores(id_proveedor)
        );
        """,
        f"""
        CREATE TABLE IF NOT EXISTS Facturas_Gastos (
            id_factura {pk_type},
            id_mantenimiento INT NULL,
            id_material_comprado INT NULL,
            id_proveedor INT NOT NULL,
            numero_factura VARCHAR(50) NOT NULL,
            concepto VARCHAR(200) NOT NULL,
            importe_total DECIMAL(10,2) NOT NULL,
            fecha_emision DATE NOT NULL,
            FOREIGN KEY (id_mantenimiento) REFERENCES Mantenimientos_Reparaciones(id_mantenimiento),
            FOREIGN KEY (id_material_comprado) REFERENCES Materiales_Equipos(id_material),
            FOREIGN KEY (id_proveedor) REFERENCES Proveedores(id_proveedor)
        );
        """
    ]

# MySQL y MariaDB
def init_mysql_like(config, db_name):
    print(f"Creando tablas en {db_name}...")
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        for query in get_ddl_queries(is_postgres=False):
            cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Tablas creadas con éxito en {db_name}.")
    except Exception as e:
        print(f"Error en {db_name}: {e}")

# PostgreSQL
def init_postgres(config):
    print("Creando tablas en PostgreSQL...")
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        for query in get_ddl_queries(is_postgres=True):
            cursor.execute(query)
        conn.commit()
        cursor.close()
        conn.close()
        print("Tablas creadas con éxito en PostgreSQL.")
    except Exception as e:
        print(f"Error en PostgreSQL: {e}")


if __name__ == "__main__":
    init_mysql_like(CONFIG_MYSQL, "MySQL")
    init_mysql_like(CONFIG_MARIADB, "MariaDB")
    init_postgres(CONFIG_POSTGRES)