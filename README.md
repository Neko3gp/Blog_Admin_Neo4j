# Administrador de Blog con Neo4j

Aplicación de escritorio en Python (CustomTkinter) para administrar un blog guardado en una **base de datos de grafos Neo4j**, consultada con **Cypher**.
Proyecto final de Bases de Datos Avanzadas.

## Modelo del grafo

```
(:User)-[:WROTE]->(:Article)             un usuario escribe N artículos
(:User)-[:COMMENTED]->(:Comment)         un usuario escribe N comentarios
(:Article)-[:HAS_COMMENT]->(:Comment)    un artículo tiene N comentarios
(:Article)-[:HAS_TAG]->(:Tag)            artículos N──N etiquetas
(:Article)-[:IN_CATEGORY]->(:Category)   artículos N──N categorías
```

| Nodo | Propiedades |
|---|---|
| `User` | id, name, email (único) |
| `Article` | id, title, text, date |
| `Comment` | id, content, date |
| `Tag` / `Category` | id, name (único), url |

Las relaciones muchos-a-muchos ya no necesitan tablas intermedias: son relaciones directas entre nodos.

## Qué incluye

- Feed de artículos con orden por fecha y filtros por categoría y etiqueta.
- Detalle de artículo con comentarios (crear, editar, eliminar).
- Publicar, editar y eliminar artículos con selección múltiple de etiquetas y categorías.
- Alta de usuarios y CRUD de categorías y etiquetas.

## Estructura

```
.
├── docker-compose.yml        # Neo4j en Docker
├── start.sh                  # Arranque automático (Docker + Cypher + entorno Python)
├── install_python.sh         # Python con Tcl/Tk para macOS (si la GUI sale vacía)
├── cypher/
│   ├── 01_schema.cypher      # Restricciones (ids y emails únicos)
│   ├── 02_seed.cypher        # Datos de ejemplo
│   ├── consultas.cypher      # TODAS las consultas que usa la app (una por nombre)
│   └── 03_demo_grafo.cypher  # Consultas para probar en Neo4j Browser y tomar capturas
└── app/
    ├── db.py                 # Conexión a Neo4j: consultar(), ejecutar(), ejecutar_varias()
    ├── main_gui.py           # Ventana principal y navegación
    ├── views/                # feed, article_detail, new_article, users, taxonomy
    ├── widgets/              # tarjetas, chips y combo
    ├── theme.py
    ├── test_conexion.py
    └── test_integration.py
```

### Cómo se conecta Python con Cypher

`cypher/consultas.cypher` guarda cada consulta con un nombre:

```cypher
// @usuarios_listar
MATCH (u:User)
RETURN u.id AS id, u.name AS name, u.email AS email
ORDER BY u.name;
```

y las vistas la llaman por ese nombre, pasando parámetros:

```python
usuarios = consultar("usuarios_listar")                       # lista de diccionarios
ejecutar("usuario_crear", name="Ana", email="ana@correo.com")  # escritura
```

Guardar un artículo (con sus etiquetas y categorías) usa `ejecutar_varias`, que agrupa varias consultas en **una sola transacción**.

## Inicio rápido (macOS)

Requisitos: Docker Desktop abierto y Python 3.11+ (con Tcl/Tk 8.6+).

```
chmod +x start.sh install_python.sh
./start.sh
```

`start.sh` levanta Neo4j, aplica las restricciones, carga los datos de ejemplo si el grafo está vacío, crea el entorno virtual y prueba la conexión. Después:

```
cd app
TK_SILENCE_DEPRECATION=1 .venv/bin/python main_gui.py
```

Si la ventana sale vacía, ejecuta primero `./install_python.sh` (el Python de Command Line Tools trae Tk 8.5).

## Neo4j Browser

Abre <http://localhost:7474> con usuario `neo4j` y contraseña `admin12345`, y ejecuta las consultas de `cypher/03_demo_grafo.cypher`. La primera (`MATCH (n)-[r]->(m) RETURN n, r, m`) dibuja todo el grafo.

## Pruebas

Desde `app/`:

```
.venv/bin/python test_conexion.py
.venv/bin/python test_integration.py   # ejecuta todas las consultas; se puede repetir
```

## Reiniciar los datos

Para volver al estado inicial: `docker exec -i blog_neo4j cypher-shell -u neo4j -p admin12345 < cypher/02_seed.cypher`
(o `docker compose down -v` y `./start.sh` para borrar el volumen completo).

## Credenciales (solo desarrollo local)

| Parámetro | Valor |
|---|---|
| Bolt | `bolt://localhost:7687` |
| Usuario | `neo4j` |
| Contraseña | `admin12345` |

Están en `docker-compose.yml` y `app/db.py`; si cambias una, cambia la otra.
