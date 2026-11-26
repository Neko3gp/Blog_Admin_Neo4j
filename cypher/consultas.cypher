// consultas.cypher — Catálogo de consultas que usa la aplicación.
//
// Convención:
//   Cada bloque empieza con "// @nombre" y termina en ";".
//   app/db.py las carga en un diccionario y las ejecuta por nombre.
//   Los parámetros van como $algo (ej. $name, $user_id) y los manda Python.
//
// Equivalente conceptual a los paquetes PL/SQL de la versión Oracle.


// ═════════════ Usuarios ═════════════

// @usuarios_listar
// Lista todos los User (pantalla Usuarios y combos de autor).
MATCH (u:User)
RETURN u.id AS id, u.name AS name, u.email AS email
ORDER BY u.name;

// @usuario_crear
// Crea un User. El email es único (restricción user_email): si ya existe → error.
CREATE (:User {id: randomUUID(), name: $name, email: $email});


// ═════════════ Artículos ═════════════

// @articulos_listar
// Feed: cada artículo con autor, categorías y etiquetas.
// $categoria / $etiqueta opcionales (null = no filtran).
MATCH (u:User)-[:WROTE]->(a:Article)
WHERE ($categoria IS NULL OR EXISTS { (a)-[:IN_CATEGORY]->(:Category {name: $categoria}) })
  AND ($etiqueta IS NULL OR EXISTS { (a)-[:HAS_TAG]->(:Tag {name: $etiqueta}) })
RETURN a.id AS id,
       a.title AS title,
       a.text AS text,
       a.date AS date,
       u.id AS author_id,
       u.name AS author,
       [(a)-[:IN_CATEGORY]->(c:Category) | c.name] AS categories,
       [(a)-[:IN_CATEGORY]->(c:Category) | c.id] AS category_ids,
       [(a)-[:HAS_TAG]->(t:Tag) | t.name] AS tags,
       [(a)-[:HAS_TAG]->(t:Tag) | t.id] AS tag_ids
ORDER BY a.date DESC;

// @articulo_crear
// Crea Article y lo enlaza con el autor mediante WROTE. La fecha es datetime() del servidor.
MATCH (u:User {id: $user_id})
CREATE (u)-[:WROTE]->(:Article {id: $id, title: $title, text: $text, date: datetime()});

// @articulo_actualizar
// Actualiza título/texto y mueve la relación WROTE si cambió el autor.
MATCH (a:Article {id: $id})
MATCH (u:User {id: $user_id})
OPTIONAL MATCH (:User)-[viejo:WROTE]->(a)
DELETE viejo
CREATE (u)-[:WROTE]->(a)
SET a.title = $title, a.text = $text;

// @articulo_asignar_etiquetas
// Reemplaza TODAS las HAS_TAG del artículo por las de $tag_ids (lista vacía = ninguna).
MATCH (a:Article {id: $id})
OPTIONAL MATCH (a)-[viejo:HAS_TAG]->()
DELETE viejo
WITH DISTINCT a
OPTIONAL MATCH (t:Tag) WHERE t.id IN $tag_ids
WITH a, collect(t) AS etiquetas
FOREACH (e IN etiquetas | MERGE (a)-[:HAS_TAG]->(e));

// @articulo_asignar_categorias
// Igual que etiquetas, pero con IN_CATEGORY y $category_ids.
MATCH (a:Article {id: $id})
OPTIONAL MATCH (a)-[viejo:IN_CATEGORY]->()
DELETE viejo
WITH DISTINCT a
OPTIONAL MATCH (c:Category) WHERE c.id IN $category_ids
WITH a, collect(c) AS categorias
FOREACH (k IN categorias | MERGE (a)-[:IN_CATEGORY]->(k));

// @articulo_eliminar
// Borra el Article y sus Comment. DETACH también limpia WROTE/HAS_TAG/IN_CATEGORY.
MATCH (a:Article {id: $id})
OPTIONAL MATCH (a)-[:HAS_COMMENT]->(c:Comment)
DETACH DELETE a, c;


// ═════════════ Comentarios ═════════════

// @comentarios_listar
// Comentarios de un artículo con el nombre del autor (recorrido Article→Comment←User).
MATCH (:Article {id: $article_id})-[:HAS_COMMENT]->(c:Comment)<-[:COMMENTED]-(u:User)
RETURN c.id AS id, c.content AS content, c.date AS date, u.name AS author
ORDER BY c.date;

// @comentario_crear
// Crea Comment y las dos relaciones: User-COMMENTED→Comment←HAS_COMMENT-Article.
MATCH (u:User {id: $user_id})
MATCH (a:Article {id: $article_id})
CREATE (u)-[:COMMENTED]->(:Comment {id: randomUUID(), content: $content, date: datetime()})<-[:HAS_COMMENT]-(a);

// @comentario_actualizar
// Solo cambia el texto; la fecha original se conserva.
MATCH (c:Comment {id: $id})
SET c.content = $content;

// @comentario_eliminar
// Borra un Comment y sus relaciones incidentes.
MATCH (c:Comment {id: $id})
DETACH DELETE c;


// ═════════════ Categorías ═════════════

// @categorias_listar
MATCH (c:Category)
RETURN c.id AS id, c.name AS name, c.url AS url
ORDER BY c.name;

// @categoria_crear
CREATE (:Category {id: randomUUID(), name: $name, url: $url});

// @categoria_actualizar
MATCH (c:Category {id: $id})
SET c.name = $name, c.url = $url;

// @categoria_eliminar
// Quita el nodo y sus IN_CATEGORY; los artículos NO se borran.
MATCH (c:Category {id: $id})
DETACH DELETE c;


// ═════════════ Etiquetas ═════════════

// @etiquetas_listar
MATCH (t:Tag)
RETURN t.id AS id, t.name AS name, t.url AS url
ORDER BY t.name;

// @etiqueta_crear
CREATE (:Tag {id: randomUUID(), name: $name, url: $url});

// @etiqueta_actualizar
MATCH (t:Tag {id: $id})
SET t.name = $name, t.url = $url;

// @etiqueta_eliminar
// Quita el nodo y sus HAS_TAG; los artículos NO se borran.
MATCH (t:Tag {id: $id})
DETACH DELETE t;
