import json
from decimal import Decimal
from datetime import date, datetime
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

# Serializador para convertir tipos de datos de datos a formatos nativos compatibles con JSON.
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


# CONSULTA 1 (MySQL): Informe de Incidencias Completo por Aula y Personal.
# Conecta: Incidencias_Averias, Materiales_Equipos, Aulas_Instalaciones y Personal_Centro.
def export_mysql_analytics():
    print("Ejecutando consulta analítica en MySQL...")
    
    query = """
    SELECT 
        i.id_incidencia,
        m.codigo_inventario AS codigo_material,
        a.nombre AS aula,
        a.ubicacion AS ubicacion_aula,
        CONCAT(p.nombre, ' ', p.apellidos) AS reportado_por,
        p.rol AS rol_reportador,
        i.fecha_reporte,
        i.prioridad,
        i.estado,
        i.descripcion_texto
    FROM Incidencias_Averias i
    INNER JOIN Materiales_Equipos m ON i.id_material = m.id_material
    INNER JOIN Aulas_Instalaciones a ON i.id_aula = a.id_aula
    INNER JOIN Personal_Centro p ON i.id_reportado_por = p.id_personal
    ORDER BY i.fecha_reporte DESC;
    """

    conn = mysql.connector.connect(**CONFIG_MYSQL)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    filename = "analitica_incidencias_mysql.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)
    
    print(f"Exportado exitosamente: {filename} ({len(results)} registros)")


# CONSULTA 2 (MariaDB): Informe Financiero de Mantenimientos y Facturación.
# Conecta: Facturas_Gastos, Mantenimientos_Reparaciones, Proveedores y Materiales_Equipos.
def export_mariadb_analytics():
    print("Ejecutando consulta analítica en MariaDB...")
    
    query = """
    SELECT 
        f.numero_factura,
        f.fecha_emision,
        f.concepto,
        f.importe_total,
        pr.nombre_empresa AS proveedor,
        pr.email_contacto AS email_proveedor,
        m.tipo AS tipo_mantenimiento,
        m.descripcion_trabajo,
        eq.codigo_inventario AS equipo_afectado
    FROM Facturas_Gastos f
    INNER JOIN Proveedores pr ON f.id_proveedor = pr.id_proveedor
    LEFT JOIN Mantenimientos_Reparaciones m ON f.id_mantenimiento = m.id_mantenimiento
    LEFT JOIN Materiales_Equipos eq ON m.id_material = eq.id_material
    ORDER BY f.importe_total DESC;
    """

    conn = mysql.connector.connect(**CONFIG_MARIADB)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()

    filename = "analitica_financiera_mariadb.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)
    
    print(f"Exportado exitosamente: {filename} ({len(results)} registros)")


# CONSULTA 3 (PostgreSQL): Auditoría de Bajas de Inventario y Personal Autorizado.
# Conecta: Bajas_Material, Materiales_Equipos, Categorias_Material, Personal_Centro y Aulas_Instalaciones.
def export_postgres_analytics():
    print("Ejecutando consulta analítica en PostgreSQL...")
    
    query = """
    SELECT 
        b.id_baja,
        b.fecha_baja,
        b.motivo_baja,
        b.coste_reciclaje,
        m.codigo_inventario,
        m.coste_compra AS valor_original,
        c.nombre_categoria,
        a.nombre AS ultima_aula_ubicacion,
        (p.nombre || ' ' || p.apellidos) AS autorizado_por,
        p.rol AS rol_autorizador
    FROM Bajas_Material b
    INNER JOIN Materiales_Equipos m ON b.id_material = m.id_material
    INNER JOIN Categorias_Material c ON m.id_categoria = c.id_categoria
    INNER JOIN Aulas_Instalaciones a ON m.id_aula_actual = a.id_aula
    INNER JOIN Personal_Centro p ON b.id_autorizado_por = p.id_personal
    ORDER BY b.fecha_baja DESC;
    """

    conn = psycopg2.connect(**CONFIG_POSTGRES)
    cursor = conn.cursor()
    cursor.execute(query)
    
    colnames = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    results = [dict(zip(colnames, row)) for row in rows]
    
    cursor.close()
    conn.close()

    filename = "analitica_bajas_postgres.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)
    
    print(f"Exportado exitosamente: {filename} ({len(results)} registros)")


# Ejecución de las tres consultas y exportación de cada resultado en JSON.
def run_export():
    print("Iniciando exportación analítica a JSON...")
    export_mysql_analytics()
    export_mariadb_analytics()
    export_postgres_analytics()
    print("Proceso analítico completado con éxito.")


if __name__ == "__main__":
    run_export()