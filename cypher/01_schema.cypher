// 01_schema.cypher — Restricciones de unicidad del grafo.
//
// Lo ejecuta start.sh (o a mano con cypher-shell) al preparar Neo4j.
// Se puede correr varias veces gracias a "IF NOT EXISTS".
//
// Modelo (nodos y relaciones):
//   (:User)-[:WROTE]->(:Article)            usuario 1──N artículos
//   (:User)-[:COMMENTED]->(:Comment)        usuario 1──N comentarios
//   (:Article)-[:HAS_COMMENT]->(:Comment)   artículo 1──N comentarios
//   (:Article)-[:HAS_TAG]->(:Tag)           artículos N──N etiquetas
//   (:Article)-[:IN_CATEGORY]->(:Category)  artículos N──N categorías
//
// Cada nodo tiene una propiedad `id` única (texto). Neo4j no genera ids
// autoincrementales como Oracle, así que la app usa randomUUID() / uuid4().

// User: id único + email único (no pueden registrarse dos con el mismo correo)
CREATE CONSTRAINT user_id IF NOT EXISTS FOR (n:User) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT user_email IF NOT EXISTS FOR (n:User) REQUIRE n.email IS UNIQUE;

// Article / Comment: solo exigen id único
CREATE CONSTRAINT article_id IF NOT EXISTS FOR (n:Article) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT comment_id IF NOT EXISTS FOR (n:Comment) REQUIRE n.id IS UNIQUE;

// Tag / Category: id único + name único (no dos etiquetas/categorías con el mismo nombre)
CREATE CONSTRAINT tag_id IF NOT EXISTS FOR (n:Tag) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT tag_name IF NOT EXISTS FOR (n:Tag) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT category_id IF NOT EXISTS FOR (n:Category) REQUIRE n.id IS UNIQUE;
CREATE CONSTRAINT category_name IF NOT EXISTS FOR (n:Category) REQUIRE n.name IS UNIQUE;
