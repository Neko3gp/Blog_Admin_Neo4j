"""Prueba de integración: ejecuta TODAS las consultas de cypher/consultas.cypher contra Neo4j.
Crea datos temporales con prefijo 'test-' y los borra al final, así que se puede repetir."""

import uuid

from db import _driver, consultar, ejecutar, ejecutar_varias
from neo4j.exceptions import ConstraintError

sufijo = uuid.uuid4().hex[:8]
email = f"test-{sufijo}@correo.com"


def comprobar(condicion, mensaje):
    print(("OK   " if condicion else "FALLA"), mensaje)
    assert condicion, mensaje


# Usuarios
ejecutar("usuario_crear", name=f"test-{sufijo}", email=email)
usuario = next(u for u in consultar("usuarios_listar") if u["email"] == email)
comprobar(True, "usuario_crear / usuarios_listar")
try:
    ejecutar("usuario_crear", name="otro", email=email)
    comprobar(False, "email duplicado debe fallar")
except ConstraintError:
    comprobar(True, "email duplicado rechazado por la restricción")

# Categoría y etiqueta
ejecutar("categoria_crear", name=f"test-cat-{sufijo}", url="test")
ejecutar("etiqueta_crear", name=f"test-tag-{sufijo}", url="test")
cat = next(c for c in consultar("categorias_listar") if c["name"] == f"test-cat-{sufijo}")
tag = next(t for t in consultar("etiquetas_listar") if t["name"] == f"test-tag-{sufijo}")
ejecutar("categoria_actualizar", id=cat["id"], name=f"test-cat2-{sufijo}", url="test2")
ejecutar("etiqueta_actualizar", id=tag["id"], name=f"test-tag2-{sufijo}", url="test2")
comprobar(any(c["name"] == f"test-cat2-{sufijo}" for c in consultar("categorias_listar")), "categoria_actualizar")
comprobar(any(t["name"] == f"test-tag2-{sufijo}" for t in consultar("etiquetas_listar")), "etiqueta_actualizar")

# Artículo (crear con etiqueta y categoría en una transacción)
art_id = str(uuid.uuid4())
ejecutar_varias([
    ("articulo_crear", {"id": art_id, "title": f"test-{sufijo}", "text": "texto", "user_id": usuario["id"]}),
    ("articulo_asignar_etiquetas", {"id": art_id, "tag_ids": [tag["id"]]}),
    ("articulo_asignar_categorias", {"id": art_id, "category_ids": [cat["id"]]}),
])
art = next(a for a in consultar("articulos_listar", categoria=None, etiqueta=None) if a["id"] == art_id)
comprobar(art["author"] == f"test-{sufijo}" and art["tag_ids"] == [tag["id"]] and art["category_ids"] == [cat["id"]],
          "articulo_crear + asignar etiquetas/categorías")
comprobar(len(consultar("articulos_listar", categoria=f"test-cat2-{sufijo}", etiqueta=None)) == 1, "filtro por categoría")
comprobar(len(consultar("articulos_listar", categoria=None, etiqueta=f"test-tag2-{sufijo}")) == 1, "filtro por etiqueta")

# Editar: nuevo título y sin etiquetas
ejecutar_varias([
    ("articulo_actualizar", {"id": art_id, "title": "editado", "text": "nuevo", "user_id": usuario["id"]}),
    ("articulo_asignar_etiquetas", {"id": art_id, "tag_ids": []}),
    ("articulo_asignar_categorias", {"id": art_id, "category_ids": [cat["id"]]}),
])
art = next(a for a in consultar("articulos_listar", categoria=None, etiqueta=None) if a["id"] == art_id)
comprobar(art["title"] == "editado" and art["tags"] == [] and len(art["categories"]) == 1, "articulo_actualizar")

# Comentarios
ejecutar("comentario_crear", content="hola", user_id=usuario["id"], article_id=art_id)
comentario = consultar("comentarios_listar", article_id=art_id)[0]
comprobar(comentario["content"] == "hola" and comentario["author"] == f"test-{sufijo}", "comentario_crear / listar")
ejecutar("comentario_actualizar", id=comentario["id"], content="editado")
comprobar(consultar("comentarios_listar", article_id=art_id)[0]["content"] == "editado", "comentario_actualizar")
ejecutar("comentario_crear", content="otro", user_id=usuario["id"], article_id=art_id)
ejecutar("comentario_eliminar", id=comentario["id"])
comprobar(len(consultar("comentarios_listar", article_id=art_id)) == 1, "comentario_eliminar")

# Borrar: el artículo se lleva sus comentarios
ejecutar("articulo_eliminar", id=art_id)
comprobar(consultar("comentarios_listar", article_id=art_id) == [], "articulo_eliminar (borra sus comentarios)")

# Limpieza de lo creado por la prueba
ejecutar("categoria_eliminar", id=cat["id"])
ejecutar("etiqueta_eliminar", id=tag["id"])
_driver.execute_query("MATCH (u:User {id: $id}) DETACH DELETE u", id=usuario["id"])  # el usuario no tiene consulta de borrado en la app
print("\nTodas las pruebas pasaron y los datos de prueba se borraron.")
