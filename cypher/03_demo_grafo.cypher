// 03_demo_grafo.cypher — Consultas para probar en Neo4j Browser (http://localhost:7474)
// y tomar capturas para el reporte. No las usa la aplicación.

// 1. Todo el grafo (en Neo4j Browser se dibuja con nodos y relaciones)
MATCH (n)-[r]->(m) RETURN n, r, m;

// 2. Artículos con su autor, categorías y etiquetas
MATCH (u:User)-[:WROTE]->(a:Article)
RETURN a.title AS articulo,
       u.name AS autor,
       [(a)-[:IN_CATEGORY]->(c) | c.name] AS categorias,
       [(a)-[:HAS_TAG]->(t) | t.name] AS etiquetas
ORDER BY a.date DESC;

// 3. Artículos más comentados
MATCH (a:Article)
RETURN a.title AS articulo, size([(a)-[:HAS_COMMENT]->(c) | c]) AS comentarios
ORDER BY comentarios DESC;

// 4. Artículos relacionados con "Introducción a Neo4j" (comparten etiquetas)
MATCH (:Article {title: 'Introducción a Neo4j'})-[:HAS_TAG]->(t:Tag)<-[:HAS_TAG]-(otro:Article)
RETURN otro.title AS articulo_relacionado, collect(t.name) AS etiquetas_en_comun
ORDER BY size(etiquetas_en_comun) DESC;

// 5. Actividad de cada usuario
MATCH (u:User)
RETURN u.name AS usuario,
       size([(u)-[:WROTE]->(a) | a]) AS articulos,
       size([(u)-[:COMMENTED]->(c) | c]) AS comentarios
ORDER BY articulos DESC;
