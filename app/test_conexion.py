"""Prueba mínima: conecta con Neo4j y muestra cuántos artículos y usuarios hay."""

from db import consultar, verificar_conexion

verificar_conexion()
print("Conexión OK")
print("  Usuarios:", len(consultar("usuarios_listar")))
print("  Artículos:", len(consultar("articulos_listar", categoria=None, etiqueta=None)))
