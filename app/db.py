"""Conexión a Neo4j y ejecución de las consultas de cypher/consultas.cypher.

Las vistas solo usan tres funciones:
  consultar("nombre", param=valor)   → lee y devuelve una lista de diccionarios
  ejecutar("nombre", param=valor)    → escribe (crear / actualizar / borrar)
  ejecutar_varias([(nombre, params)])→ varias escrituras en UNA transacción
"""

from pathlib import Path

from neo4j import GraphDatabase
from neo4j.exceptions import ConstraintError

# Credenciales = docker-compose.yml (NEO4J_AUTH)
URI = "bolt://localhost:7687"
USUARIO = "neo4j"
PASSWORD = "admin12345"

ARCHIVO_CONSULTAS = Path(__file__).resolve().parent.parent / "cypher" / "consultas.cypher"

# El driver se crea una sola vez; se conecta hasta la primera consulta.
_driver = GraphDatabase.driver(URI, auth=(USUARIO, PASSWORD))


def _cargar_consultas():
    """Lee consultas.cypher y arma {nombre: texto}. Cada consulta inicia con '// @nombre'."""
    consultas, nombre = {}, None
    for linea in ARCHIVO_CONSULTAS.read_text(encoding="utf-8").splitlines():
        if linea.startswith("// @"):
            nombre = linea[4:].strip()
            consultas[nombre] = []
        elif nombre and not linea.startswith("//"):
            consultas[nombre].append(linea)
    return {n: "\n".join(lineas).strip().rstrip(";") for n, lineas in consultas.items()}


CONSULTAS = _cargar_consultas()


def consultar(consulta, /, **params):
    """Ejecuta una consulta de lectura y devuelve una lista de diccionarios."""
    registros, _, _ = _driver.execute_query(CONSULTAS[consulta], parameters_=params)
    return [registro.data() for registro in registros]


def ejecutar(consulta, /, **params):
    """Ejecuta una consulta de escritura (CREATE / SET / DELETE)."""
    _driver.execute_query(CONSULTAS[consulta], parameters_=params)


def ejecutar_varias(pasos):
    """Ejecuta varias escrituras en una sola transacción: o se guardan todas o ninguna.
    `pasos` es una lista de (nombre_consulta, {parametros})."""
    def trabajo(tx):
        for consulta, params in pasos:
            tx.run(CONSULTAS[consulta], params).consume()

    with _driver.session() as sesion:
        sesion.execute_write(trabajo)


def verificar_conexion():
    _driver.verify_connectivity()


def formatear_fecha(fecha):
    """datetime de Neo4j → 'AAAA-MM-DD HH:MM'."""
    return str(fecha)[:16].replace("T", " ") if fecha else ""


def mensaje_error(error):
    """Texto corto para mostrar en un messagebox."""
    if isinstance(error, ConstraintError):
        return "Ya existe un registro con ese valor (email o nombre repetido)."
    return str(error).split("\n")[0]
