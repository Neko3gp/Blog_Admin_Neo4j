"""Prueba mínima de que Python puede hablar con Neo4j.

Uso (desde app/):
  .venv/bin/python test_conexion.py

start.sh la ejecuta al final del arranque.
Si falla, la GUI tampoco podrá leer datos.
"""

from db import consultar, verificar_conexion

verificar_conexion()
print("Conexión OK")
print("  Usuarios:", len(consultar("usuarios_listar")))
print("  Artículos:", len(consultar("articulos_listar", categoria=None, etiqueta=None)))
