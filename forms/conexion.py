import psycopg2


def obtener_conexion():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="ferreteria",
        user="postgres",
        password="TU_CONTRASEÑA"
    )