import os
import psycopg2


def obtener_conexion():
    """
    Conecta a PostgreSQL.
    En Render utiliza DATABASE_URL.
    En el equipo local utiliza las variables PGHOST, PGPORT,
    PGDATABASE, PGUSER y PGPASSWORD.
    """

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg2.connect(database_url)

    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        database=os.getenv("PGDATABASE", "ferreteria"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "137905")
    )