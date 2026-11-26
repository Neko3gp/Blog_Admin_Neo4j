"""Capa de acceso a Neo4j.

Las vistas de la GUI NO escriben Cypher a mano.
Solo llaman a estas funciones por nombre de consulta:

  consultar("nombre", param=valor)    → lectura; devuelve lista de dicts
  ejecutar("nombre", param=valor)     → escritura (crear / actualizar / borrar)
  ejecutar_varias([(nombre, params)]) → varias escrituras en UNA transacción

Flujo:
  Vista → consultar/ejecutar → busca texto en CONSULTAS → driver → Neo4j
"""

from pathlib import Path

from neo4j import GraphDatabase
from neo4j.exceptions import ConstraintError

# Deben coincidir con NEO4J_AUTH en docker-compose.yml
URI = "bolt://localhost:7687"  # puerto Bolt (el driver Python usa este, no el 7474)
USUARIO = "neo4j"
PASSWORD = "admin12345"

# consultas.cypher vive un nivel arriba de app/
ARCHIVO_CONSULTAS = Path(__file__).resolve().parent.parent / "cypher" / "consultas.cypher"

# Un solo driver para toda la app; la conexión real ocurre en la primera consulta.
_driver = GraphDatabase.driver(URI, auth=(USUARIO, PASSWORD))


def _cargar_consultas():
    """Parsea consultas.cypher y arma un diccionario {nombre: texto_cypher}.

    Cada bloque empieza con '// @nombre' y termina en ';'.
    Las líneas que empiezan con '//' (comentarios) se ignoran dentro del bloque.
    """
    consultas, nombre = {}, None
    for linea in ARCHIVO_CONSULTAS.read_text(encoding="utf-8").splitlines():
        if linea.startswith("// @"):
            # Nueva consulta: el nombre es lo que sigue a "// @"
            nombre = linea[4:].strip()
            consultas[nombre] = []
        elif nombre and not linea.startswith("//"):
            # Acumula el cuerpo Cypher (omite comentarios)
            consultas[nombre].append(linea)
    # Une las líneas y quita el ';' final (execute_query no lo necesita)
    return {n: "\n".join(lineas).strip().rstrip(";") for n, lineas in consultas.items()}


# Se carga una sola vez al importar este módulo
CONSULTAS = _cargar_consultas()


def consultar(consulta, /, **params):
    """Ejecuta una consulta de LECTURA y devuelve lista de diccionarios.

    Ejemplo: consultar("usuarios_listar")
             consultar("articulos_listar", categoria=None, etiqueta="neo4j")
    """
    registros, _, _ = _driver.execute_query(CONSULTAS[consulta], parameters_=params)
    return [registro.data() for registro in registros]


def ejecutar(consulta, /, **params):
    """Ejecuta una consulta de ESCRITURA (CREATE / SET / DELETE).

    Ejemplo: ejecutar("usuario_crear", name="Ana", email="ana@correo.com")
    """
    _driver.execute_query(CONSULTAS[consulta], parameters_=params)


def ejecutar_varias(pasos):
    """Ejecuta varias escrituras en una sola transacción (todo o nada).

    Se usa al guardar un artículo: crear/actualizar + asignar tags + categorías.
    Si falla un paso, Neo4j revierte los anteriores.

    `pasos` es una lista de (nombre_consulta, {parametros}).
    """
    def trabajo(tx):
        for consulta, params in pasos:
            tx.run(CONSULTAS[consulta], params).consume()

    with _driver.session() as sesion:
        sesion.execute_write(trabajo)


def verificar_conexion():
    """Comprueba que Neo4j responde (usada por test_conexion.py y start.sh)."""
    _driver.verify_connectivity()


def formatear_fecha(fecha):
    """Convierte el datetime de Neo4j a texto 'AAAA-MM-DD HH:MM' para la UI."""
    return str(fecha)[:16].replace("T", " ") if fecha else ""


def mensaje_error(error):
    """Traduce errores de Neo4j a un mensaje corto para messagebox."""
    if isinstance(error, ConstraintError):
        # Violación de unicidad (email o nombre de categoría/etiqueta repetido)
        return "Ya existe un registro con ese valor (email o nombre repetido)."
    return str(error).split("\n")[0]
