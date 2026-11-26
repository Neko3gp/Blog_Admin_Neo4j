// 02_seed.cypher — Datos de ejemplo para demo y pruebas.
//
// ¡ATENCIÓN! Empieza borrando TODO el grafo (MATCH ... DETACH DELETE).
// start.sh solo lo carga si el conteo de nodos es 0.
// No lo ejecutes a mano si quieres conservar datos reales.
//
// Contenido: 3 User, 4 Article, 4 Comment, 2 Category, 4 Tag = 17 nodos.
// IDs cortos (u1, a1, ...) solo para el seed; los registros nuevos usan UUID.

// Borra nodos y relaciones existentes
MATCH (n) DETACH DELETE n;

CREATE
  // ── Usuarios ──
  (u1:User {id: 'u1', name: 'Demo User',    email: 'demo@correo.com'}),
  (u2:User {id: 'u2', name: 'Ana Torres',   email: 'ana@correo.com'}),
  (u3:User {id: 'u3', name: 'Luis Ramírez', email: 'luis@correo.com'}),

  // ── Categorías (name + url/slug) ──
  (c1:Category {id: 'c1', name: 'Programación',    url: 'programacion'}),
  (c2:Category {id: 'c2', name: 'Bases de Datos',  url: 'bases-de-datos'}),

  // ── Etiquetas ──
  (t1:Tag {id: 't1', name: 'neo4j',    url: 'neo4j'}),
  (t2:Tag {id: 't2', name: 'grafos',   url: 'grafos'}),
  (t3:Tag {id: 't3', name: 'python',   url: 'python'}),
  (t4:Tag {id: 't4', name: 'tutorial', url: 'tutorial'}),

  // ── Artículos (title, text, date) ──
  (a1:Article {id: 'a1', title: 'Introducción a Neo4j',
               text: 'Neo4j guarda la información como nodos y relaciones, lo que facilita consultar datos muy conectados.',
               date: datetime('2026-11-10T09:00:00')}),
  (a2:Article {id: 'a2', title: 'Python y bases de datos',
               text: 'El driver oficial de Neo4j para Python permite ejecutar consultas Cypher con parámetros.',
               date: datetime('2026-11-12T16:30:00')}),
  (a3:Article {id: 'a3', title: 'Modelando relaciones con grafos',
               text: 'En un grafo las relaciones ya no son tablas intermedias: son parte del dato.',
               date: datetime('2026-11-15T11:15:00')}),
  (a4:Article {id: 'a4', title: 'Mi primer blog con CustomTkinter',
               text: 'Pasos para construir una interfaz de escritorio sencilla con CustomTkinter.',
               date: datetime('2026-11-17T20:00:00')}),

  // ── Relación User → Article (quién escribió) ──
  (u1)-[:WROTE]->(a1),
  (u2)-[:WROTE]->(a2),
  (u2)-[:WROTE]->(a3),
  (u3)-[:WROTE]->(a4),

  // ── Article → Category (N–N) ──
  (a1)-[:IN_CATEGORY]->(c2),
  (a2)-[:IN_CATEGORY]->(c1),
  (a2)-[:IN_CATEGORY]->(c2),
  (a3)-[:IN_CATEGORY]->(c2),
  (a4)-[:IN_CATEGORY]->(c1),

  // ── Article → Tag (N–N) ──
  (a1)-[:HAS_TAG]->(t1),
  (a1)-[:HAS_TAG]->(t2),
  (a2)-[:HAS_TAG]->(t1),
  (a2)-[:HAS_TAG]->(t3),
  (a3)-[:HAS_TAG]->(t2),
  (a3)-[:HAS_TAG]->(t4),
  (a4)-[:HAS_TAG]->(t3),
  (a4)-[:HAS_TAG]->(t4),

  // ── Comentarios: User -[:COMMENTED]-> Comment <-[:HAS_COMMENT]- Article ──
  (u2)-[:COMMENTED]->(:Comment {id: 'm1', content: 'Muy buena introducción, gracias.',
                                date: datetime('2026-11-10T12:00:00')})<-[:HAS_COMMENT]-(a1),
  (u3)-[:COMMENTED]->(:Comment {id: 'm2', content: '¿Se puede usar con Docker?',
                                date: datetime('2026-11-11T08:45:00')})<-[:HAS_COMMENT]-(a1),
  (u1)-[:COMMENTED]->(:Comment {id: 'm3', content: 'Justo lo que necesitaba para el proyecto.',
                                date: datetime('2026-11-13T10:20:00')})<-[:HAS_COMMENT]-(a2),
  (u1)-[:COMMENTED]->(:Comment {id: 'm4', content: 'Me gusta la comparación con las tablas.',
                                date: datetime('2026-11-16T19:05:00')})<-[:HAS_COMMENT]-(a3);
