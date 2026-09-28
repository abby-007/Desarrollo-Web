from pathlib import Path

from conexion.conexion import obtener_conexion


def inicializar_bd():
    archivo_sql = Path(__file__).parent / "sql" / "esquema.sql"

    sql = archivo_sql.read_text(encoding="utf-8")

    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql)

        conexion.commit()

        print("Base de datos inicializada correctamente.")

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


if __name__ == "__main__":
    inicializar_bd()