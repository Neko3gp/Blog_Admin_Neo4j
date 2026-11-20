// 01_schema.cypher — Restricciones del grafo (se pueden ejecutar varias veces).
//
// Modelo (nodos y relaciones):
//   (:User)-[:WROTE]->(:Article)            usuario 1──N artículos
//   (:User)-[:COMMENTED]->(:Comment)        usuario 1──N comentarios
//   (:Article)-[:HAS_COMMENT]->(:Comment)   artículo 1──N comentarios
//   (:Article)-[:HAS_TAG]->(:Tag)           artículos N──N etiquetas
//   (:Article)-[:IN_CATEGORY]->(:Category)  artículos N──N categorías
//
// Cada nodo tiene una propiedad `id` única (texto). Neo4j no genera ids
// autoincrementales como Oracle, así que la app usa randomUUID().

CREATE CONSTRAINT user_id IF NOT EXISTS FOR (n:User) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT user_email IF NOT EXISTS FOR (n:User) REQUIRE n.email IS UNIQUE;
CREATE CONSTRAINT article_id IF NOT EXISTS FOR (n:Article) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT comment_id IF NOT EXISTS FOR (n:Comment) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT tag_id IF NOT EXISTS FOR (n:Tag) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT tag_name IF NOT EXISTS FOR (n:Tag) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT category_id IF NOT EXISTS FOR (n:Category) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT category_name IF NOT EXISTS FOR (n:Category) REQUIRE n.name IS UNIQUE;
