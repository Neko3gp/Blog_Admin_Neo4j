// 03_demo_grafo.cypher — Consultas SOLO para Neo4j Browser (http://localhost:7474).
// Sirven para capturas del reporte y para mostrar el grafo en la presentación.
// La aplicación NO las usa (la app lee consultas.cypher vía db.py).
//
// Cómo usarlas: abre Browser, conéctate (neo4j / admin12345) y pega UNA consulta a la vez.

// 1) Dibuja nodos y relaciones conectados (vista visual del grafo)
MATCH (n)-[r]->(m) RETURN n, r, m;

// 2) Artículos con autor, categorías y etiquetas (tabla)
MATCH (u:User)-[:WROTE]->(a:Article)
RETURN a.title AS articulo,
       u.name AS autor,
       [(a)-[:IN_CATEGORY]->(c) | c.name] AS categorias,
       [(a)-[:HAS_TAG]->(t) | t.name] AS etiquetas
ORDER BY a.date DESC;

// 3) Ranking de artículos por número de comentarios
MATCH (a:Article)
RETURN a.title AS articulo, size([(a)-[:HAS_COMMENT]->(c) | c]) AS comentarios
ORDER BY comentarios DESC;

// 4) Artículos “relacionados” porque comparten etiquetas con uno dado
MATCH (:Article {title: 'Introducción a Neo4j'})-[:HAS_TAG]->(t:Tag)<-[:HAS_TAG]-(otro:Article)
RETURN otro.title AS articulo_relacionado, collect(t.name) AS etiquetas_en_comun
ORDER BY size(etiquetas_en_comun) DESC;

// 5) Actividad por usuario: cuántos artículos escribió y cuántos comentarios hizo
MATCH (u:User)
RETURN u.name AS usuario,
       size([(u)-[:WROTE]->(a) | a]) AS articulos,
       size([(u)-[:COMMENTED]->(c) | c]) AS comentarios
ORDER BY articulos DESC;
