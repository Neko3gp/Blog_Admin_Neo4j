// consultas.cypher — Todas las consultas que usa la aplicación.
//
// Cada consulta empieza con una línea "// @nombre" y termina en ";".
// Python (app/db.py) las busca por nombre y les pasa los parámetros ($algo).
// Es el equivalente a los paquetes PL/SQL de la versión Oracle.


// ───────────── Usuarios ─────────────

// @usuarios_listar
MATCH (u:User)
RETURN u.id AS id, u.name AS name, u.email AS email
ORDER BY u.name;

// @usuario_crear
// El email es único (restricción user_email): si ya existe, Neo4j lanza un error.
CREATE (:User {id: randomUUID(), name: $name, email: $email});


// ───────────── Artículos ─────────────

// @articulos_listar
// Devuelve cada artículo con su autor, categorías y etiquetas.
// $categoria y $etiqueta son opcionales: con null no filtran.
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
// Crea el artículo y lo conecta con su autor.
MATCH (u:User {id: $user_id})
CREATE (u)-[:WROTE]->(:Article {id: $id, title: $title, text: $text, date: datetime()});

// @articulo_actualizar
// Cambia título y texto; si cambió el autor, mueve la relación WROTE.
MATCH (a:Article {id: $id})
MATCH (u:User {id: $user_id})
OPTIONAL MATCH (:User)-[viejo:WROTE]->(a)
DELETE viejo
CREATE (u)-[:WROTE]->(a)
SET a.title = $title, a.text = $text;

// @articulo_asignar_etiquetas
// Reemplaza las etiquetas del artículo por las de $tag_ids (lista vacía = ninguna).
MATCH (a:Article {id: $id})
OPTIONAL MATCH (a)-[viejo:HAS_TAG]->()
DELETE viejo
WITH DISTINCT a
OPTIONAL MATCH (t:Tag) WHERE t.id IN $tag_ids
WITH a, collect(t) AS etiquetas
FOREACH (e IN etiquetas | MERGE (a)-[:HAS_TAG]->(e));

// @articulo_asignar_categorias
// Reemplaza las categorías del artículo por las de $category_ids.
MATCH (a:Article {id: $id})
OPTIONAL MATCH (a)-[viejo:IN_CATEGORY]->()
DELETE viejo
WITH DISTINCT a
OPTIONAL MATCH (c:Category) WHERE c.id IN $category_ids
WITH a, collect(c) AS categorias
FOREACH (k IN categorias | MERGE (a)-[:IN_CATEGORY]->(k));

// @articulo_eliminar
// Borra el artículo y sus comentarios (el DETACH quita también sus relaciones).
MATCH (a:Article {id: $id})
OPTIONAL MATCH (a)-[:HAS_COMMENT]->(c:Comment)
DETACH DELETE a, c;


// ───────────── Comentarios ─────────────

// @comentarios_listar
MATCH (:Article {id: $article_id})-[:HAS_COMMENT]->(c:Comment)<-[:COMMENTED]-(u:User)
RETURN c.id AS id, c.content AS content, c.date AS date, u.name AS author
ORDER BY c.date;

// @comentario_crear
MATCH (u:User {id: $user_id})
MATCH (a:Article {id: $article_id})
CREATE (u)-[:COMMENTED]->(:Comment {id: randomUUID(), content: $content, date: datetime()})<-[:HAS_COMMENT]-(a);

// @comentario_actualizar
MATCH (c:Comment {id: $id})
SET c.content = $content;

// @comentario_eliminar
MATCH (c:Comment {id: $id})
DETACH DELETE c;


// ───────────── Categorías ─────────────

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
MATCH (c:Category {id: $id})
DETACH DELETE c;


// ───────────── Etiquetas ─────────────

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
MATCH (t:Tag {id: $id})
DETACH DELETE t;
