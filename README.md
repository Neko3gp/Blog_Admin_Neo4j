# Administrador de Blog con Neo4j

Aplicación de escritorio en Python y CustomTkinter para administrar artículos, comentarios, usuarios, categorías y etiquetas. La información se guarda en Neo4j y se consulta con Cypher.

Proyecto final de Bases de Datos Avanzadas. Esta guía sigue la organización de [Blog_Admin](https://github.com/Neko3gp/Blog_Admin), adaptada al funcionamiento de esta versión con grafos.

## Qué incluye

- Feed con orden por fecha y filtros por categoría y etiqueta.
- Publicación, edición y eliminación de artículos.
- Selección de varias categorías y etiquetas para cada artículo.
- Comentarios: consulta, creación, edición y eliminación.
- Consulta y registro de usuarios.
- Consulta, creación, edición y eliminación de categorías y etiquetas.
- Neo4j en Docker, datos de ejemplo y pruebas de conexión e integración.

La aplicación es de escritorio; Neo4j Browser es una herramienta aparte para consultar y visualizar la base. La app no implementa inicio de sesión ni permisos por usuario: elegir un autor sirve para asociarlo al contenido.

## Requisitos

- Docker Desktop instalado y en ejecución, o Docker Engine con Docker Compose.
- Python 3.11 o superior con Tkinter; en macOS, Tcl/Tk 8.6 o superior.
- Una sesión gráfica para abrir la interfaz.
- Git si se descargará el proyecto mediante clonación.
- Puertos locales `7474` y `7687` disponibles.

No hace falta instalar Neo4j fuera de Docker. Las dependencias Python están en [app/requirements.txt](app/requirements.txt): `neo4j` y `customtkinter`.

## Inicio rápido en macOS

Desde la raíz del proyecto:

```bash
chmod +x start.sh install_python.sh
./start.sh
```

El script:

1. Comprueba que Docker esté disponible.
2. Levanta el contenedor y espera a que esté saludable.
3. Aplica las restricciones de unicidad.
4. Carga los datos de ejemplo únicamente si no hay ningún nodo.
5. Crea `app/.venv` e instala dependencias si ese entorno todavía no existe.
6. Ejecuta la prueba de conexión.

Después abre la aplicación:

```bash
cd app
TK_SILENCE_DEPRECATION=1 .venv/bin/python main_gui.py
```

Si el entorno ya existía y cambiaste las dependencias, actualízalas con `app/.venv/bin/python -m pip install -r app/requirements.txt` desde la raíz.

Si falla Tk o aparece una ventana vacía en macOS, ejecuta desde la raíz:

```bash
./install_python.sh
./start.sh
cd app
TK_SILENCE_DEPRECATION=1 .venv/bin/python main_gui.py
```

`install_python.sh` descarga CPython 3.12 para macOS, lo instala en `.python/` y recrea `app/.venv`. Está preparado para Apple Silicon e Intel.

## Instalación manual

Estos pasos permiten preparar cada parte por separado.

### 1. Obtener el proyecto

```bash
git clone https://github.com/Neko3gp/Blog_Admin_Neo4j.git
cd Blog_Admin_Neo4j
```

Si descargaste un ZIP, extráelo y abre una terminal en la carpeta que contiene `docker-compose.yml`.

### 2. Levantar Neo4j

```bash
docker compose up -d
docker compose ps
```

Espera a que `blog_neo4j` aparezca como `healthy`. Para revisar el arranque:

```bash
docker logs -f blog_neo4j
```

Puedes salir del seguimiento con Ctrl+C; el contenedor continúa funcionando.

### 3. Preparar el grafo

Desde la raíz, en Bash (macOS o Linux):

```bash
docker exec -i blog_neo4j cypher-shell -u neo4j -p TU_CONTRASENA < cypher/01_schema.cypher
```

El esquema crea restricciones y puede aplicarse varias veces sin borrar datos.

Solo en una base nueva o si deseas reemplazar todo su contenido por los ejemplos:

```bash
docker exec -i blog_neo4j cypher-shell -u neo4j -p TU_CONTRASENA < cypher/02_seed.cypher
```

**El archivo `02_seed.cypher` borra todos los nodos y relaciones antes de insertar los ejemplos.** No lo ejecutes para actualizar una base cuyos datos deseas conservar.

En Windows PowerShell, los comandos equivalentes son:

```powershell
Get-Content -Raw -Encoding UTF8 cypher/01_schema.cypher | docker exec -i blog_neo4j cypher-shell -u neo4j -p TU_CONTRASENA
# Solo para una base nueva o un reinicio intencional de sus datos:
Get-Content -Raw -Encoding UTF8 cypher/02_seed.cypher | docker exec -i blog_neo4j cypher-shell -u neo4j -p TU_CONTRASENA
```

Los ejemplos contienen 3 usuarios, 4 artículos, 4 comentarios, 2 categorías y 4 etiquetas: 17 nodos en total.

### 4. Preparar Python y abrir la app

En macOS o Linux:

```bash
cd app
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python test_conexion.py
.venv/bin/python main_gui.py
```

En Windows PowerShell:

```powershell
cd app
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe test_conexion.py
.\.venv\Scripts\python.exe main_gui.py
```

Usa un Python 3.11 o superior. En Linux, si falta Tkinter, instala el paquete correspondiente de tu distribución (habitualmente `python3-tk`).

### Volver a abrir y detener

En las siguientes sesiones, basta con iniciar Docker, ejecutar `docker compose up -d` desde la raíz y abrir `app/main_gui.py` con el Python del entorno virtual.

Para detener la base conservando los datos:

```bash
docker compose down
```

Los datos permanecen en el volumen `neo4j_data`.

## Uso de la aplicación

| Pantalla o acción | Cómo se usa |
|---|---|
| Inicio | Muestra los artículos; permite ordenar de reciente a antiguo o al revés. |
| Filtros | Selecciona categoría y/o etiqueta. Usa Todas/Todos para quitar el filtro correspondiente. |
| Detalle | Abre una tarjeta para leer el artículo y sus comentarios. |
| Publicar artículo | Completa título y texto, elige un autor existente y marca las categorías y etiquetas que quieras. |
| Editar artículo | Desde el detalle, pulsa Editar; puedes cambiar texto, título, autor y asociaciones. |
| Eliminar artículo | Desde el detalle, pulsa Eliminar y confirma. También se borran sus comentarios. |
| Comentarios | Elige un usuario y escribe el contenido; los botones de lápiz y cruz permiten editar o eliminar. |
| Usuarios | Consulta los usuarios y registra uno con nombre y correo. No hay edición ni eliminación de usuarios en la interfaz. |
| Categorías y Etiquetas | Registra un nombre; puedes editarlo o eliminarlo. El slug de URL se genera a partir del nombre. |
| Menú | El botón ☰ muestra u oculta la barra lateral. |

El título, texto y autor del artículo son obligatorios; las categorías y etiquetas pueden quedar vacías. Los comentarios no pueden estar vacíos. Los correos de usuario y los nombres de categorías y etiquetas deben ser únicos.

Al borrar una categoría o etiqueta se eliminan sus relaciones con artículos, pero los artículos permanecen.

### Recorrido de ejemplo

1. Abre Usuarios y registra un autor con un correo nuevo.
2. Crea una categoría y una etiqueta.
3. Publica un artículo con ese autor y esas asociaciones.
4. Localízalo en Inicio utilizando los filtros.
5. Abre el detalle, agrega un comentario y prueba su edición.
6. Edita el artículo y comprueba el cambio al volver al feed.

## Modelo del grafo

Un **nodo** representa un registro (por ejemplo, un artículo). Una **propiedad** guarda un dato del nodo (como el título). Una **relación** conecta dos nodos y expresa su vínculo.

| Nodo | Propiedades | Restricciones del esquema |
|---|---|---|
| `User` | `id`, `name`, `email` | ID y correo únicos |
| `Article` | `id`, `title`, `text`, `date` | ID único |
| `Comment` | `id`, `content`, `date` | ID único |
| `Tag` | `id`, `name`, `url` | ID y nombre únicos |
| `Category` | `id`, `name`, `url` | ID y nombre únicos |

| Origen | Relación | Destino | Significado |
|---|---|---|---|
| `User` | `WROTE` | `Article` | El usuario escribió el artículo |
| `User` | `COMMENTED` | `Comment` | El usuario escribió el comentario |
| `Article` | `HAS_COMMENT` | `Comment` | El comentario pertenece al artículo |
| `Article` | `HAS_TAG` | `Tag` | El artículo tiene esa etiqueta |
| `Article` | `IN_CATEGORY` | `Category` | El artículo está en esa categoría |

Los artículos pueden tener varias etiquetas y categorías. En Neo4j esas asociaciones son relaciones directas, por lo que no se necesitan las tablas intermedias de la versión Oracle.

Los nuevos IDs son UUID: el artículo los genera con `uuid.uuid4()` en Python y los otros tipos con `randomUUID()` en Cypher. Los IDs cortos como `u1` se usan únicamente en los ejemplos.

Las fechas nuevas se crean con `datetime()`; Docker configura la zona `America/Chihuahua`. La interfaz muestra año, mes, día, hora y minutos. Editar un artículo o comentario no cambia su fecha original.

## Arquitectura y archivos

La interfaz llama funciones de `app/db.py`; estas buscan consultas por nombre en `cypher/consultas.cypher` y las ejecutan con el driver oficial de Neo4j.

| Archivo o carpeta | Responsabilidad |
|---|---|
| [docker-compose.yml](docker-compose.yml) | Neo4j 5 Community, puertos, volumen, zona horaria y comprobación de salud |
| [start.sh](start.sh) | Arranque, restricciones, carga inicial y entorno Python |
| [install_python.sh](install_python.sh) | Preparación de Python con Tk para macOS |
| [cypher/01_schema.cypher](cypher/01_schema.cypher) | Restricciones de unicidad |
| [cypher/02_seed.cypher](cypher/02_seed.cypher) | Reemplazo del grafo por datos de ejemplo |
| [cypher/consultas.cypher](cypher/consultas.cypher) | Consultas utilizadas por la aplicación |
| [cypher/03_demo_grafo.cypher](cypher/03_demo_grafo.cypher) | Consultas de demostración para Neo4j Browser |
| [app/db.py](app/db.py) | Driver, carga de consultas, transacciones, fechas y mensajes de error |
| [app/main_gui.py](app/main_gui.py) | Inicio de la ventana y navegación |
| [app/views/feed.py](app/views/feed.py) | Listado y filtros de artículos |
| [app/views/article_detail.py](app/views/article_detail.py) | Detalle, comentarios y eliminación del artículo |
| [app/views/new_article.py](app/views/new_article.py) | Formulario compartido para crear y editar artículos |
| [app/views/users.py](app/views/users.py) | Listado y alta de usuarios |
| [app/views/taxonomy.py](app/views/taxonomy.py) | Gestión compartida de categorías y etiquetas |
| [app/widgets/](app/widgets/) | Tarjetas, chips y selectores reutilizables |
| [app/theme.py](app/theme.py) | Colores y estilos compartidos |
| [app/requirements.txt](app/requirements.txt) | Dependencias de Python |
| [app/test_conexion.py](app/test_conexion.py) | Comprobación de conexión |
| [app/test_integration.py](app/test_integration.py) | Comprobación de las operaciones con datos temporales |

### Cómo se ejecuta una consulta

Cada consulta comienza con `// @nombre`:

```cypher
// @usuarios_listar
MATCH (u:User)
RETURN u.id AS id, u.name AS name, u.email AS email
ORDER BY u.name;
```

Desde Python:

```python
from db import consultar, ejecutar

usuarios = consultar("usuarios_listar")
ejecutar("usuario_crear", name="Ana", email="ana.nueva@correo.com")
```

Este ejemplo se ejecuta desde `app/` y la segunda llamada crea un usuario.

- `consultar(nombre, **params)`: devuelve una lista de diccionarios.
- `ejecutar(nombre, **params)`: realiza una escritura.
- `ejecutar_varias(pasos)`: agrupa escrituras en una transacción; si ocurre un error, se revierten juntas.

Al guardar un artículo, se crea o actualiza el nodo y se reemplazan sus relaciones con etiquetas y categorías dentro de una transacción. Los parámetros como `$user_id` se envían separados del texto de la consulta.

### Catálogo de consultas

| Área | Nombres en consultas.cypher |
|---|---|
| Usuarios | `usuarios_listar`, `usuario_crear` |
| Artículos | `articulos_listar`, `articulo_crear`, `articulo_actualizar`, `articulo_eliminar` |
| Asociaciones | `articulo_asignar_etiquetas`, `articulo_asignar_categorias` |
| Comentarios | `comentarios_listar`, `comentario_crear`, `comentario_actualizar`, `comentario_eliminar` |
| Categorías | `categorias_listar`, `categoria_crear`, `categoria_actualizar`, `categoria_eliminar` |
| Etiquetas | `etiquetas_listar`, `etiqueta_crear`, `etiqueta_actualizar`, `etiqueta_eliminar` |

`articulos_listar` recibe `categoria` y `etiqueta`; con `None` no aplica el filtro correspondiente. La consulta devuelve los artículos del más reciente al más antiguo y la interfaz invierte esa lista cuando se elige el orden contrario.

### Diferencias con la versión Oracle

| Versión Oracle | Versión Neo4j |
|---|---|
| Tablas y filas | Nodos con etiquetas y propiedades |
| Claves foráneas y tablas intermedias | Relaciones directas |
| SQL y paquetes PL/SQL | Consultas Cypher por nombre |
| Driver `oracledb` | Driver `neo4j` |
| Puerto 1521 | Bolt 7687 y Browser 7474 |
| Texto CLOB | Propiedades de texto |
| Identificadores del modelo relacional | UUID para registros nuevos |

Neo4j es una base de grafos; esta versión no utiliza los scripts ni los paquetes PL/SQL del proyecto Oracle.

## Credenciales y conexión local

| Parámetro | Valor |
|---|---|
| Neo4j Browser | `http://localhost:7474` |
| URI del driver Python | `bolt://localhost:7687` |
| Usuario | `neo4j` |
| Contraseña | Consulta el valor configurado en `app/db.py` y `NEO4J_AUTH` |
| Contenedor | `blog_neo4j` |
| Volumen declarado en Compose | `neo4j_data` |

En los comandos de esta guía, reemplaza `TU_CONTRASENA` por la contraseña de tu entorno local. El marcador no es una contraseña funcional.

Son valores de desarrollo. La autenticación aparece en `docker-compose.yml`, `app/db.py` y `start.sh`; también se usa en los comandos de esta guía.

Si cambias la contraseña, actualiza esas referencias. Cambiar `NEO4J_AUTH` en Compose no sustituye la contraseña de una base ya inicializada en un volumen existente.

## Neo4j Browser y consultas de demostración

Abre [Neo4j Browser](http://localhost:7474), conecta con las credenciales locales y ejecuta por separado las consultas de `cypher/03_demo_grafo.cypher`.

Para visualizar los nodos conectados:

```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m;
```

Para contar todos los nodos, incluidos los que no tienen relaciones:

```cypher
MATCH (n)
RETURN count(n) AS total_nodos;
```

El archivo de demostración también incluye artículos con autores y clasificación, artículos más comentados, artículos relacionados por etiquetas y actividad de usuarios. Estas consultas son de lectura y no forman parte del arranque de la GUI.

## Pruebas y comprobaciones

Con Neo4j saludable y las restricciones aplicadas, desde `app/`:

```bash
.venv/bin/python test_conexion.py
.venv/bin/python test_integration.py
.venv/bin/python -m compileall -q .
```

En Windows, usa `.\.venv\Scripts\python.exe` en lugar de `.venv/bin/python`.

- La prueba de conexión verifica que se pueda acceder a Neo4j.
- La integración comprueba usuarios y rechazo de correos duplicados, categorías, etiquetas, artículos, filtros, asociaciones y comentarios.
- La compilación comprueba la sintaxis Python; no comprueba la conexión ni la interfaz.

La integración utiliza nombres temporales con un sufijo aleatorio y elimina sus datos al terminar correctamente. Puede repetirse; si falla antes de la limpieza, puede dejar datos temporales. No sustituye una revisión visual de las pantallas.

## Reiniciar los datos

**Este procedimiento elimina el contenido actual del grafo.** Úsalo solo si deseas recuperar los ejemplos y no necesitas conservar lo guardado.

Con Neo4j en ejecución, desde la raíz y en Bash:

```bash
docker exec -i blog_neo4j cypher-shell -u neo4j -p TU_CONTRASENA < cypher/02_seed.cypher
```

Otra opción es eliminar el volumen completo y preparar todo otra vez:

```bash
docker compose down -v
./start.sh
```

El segundo comando corresponde al arranque en macOS. En otros entornos, repite la instalación manual. Para detener el servicio sin borrar datos usa únicamente `docker compose down`, sin `-v`.

## Solución de problemas

| Problema | Qué revisar |
|---|---|
| Docker no está listo | Abre Docker Desktop y ejecuta `docker info`. Después repite `docker compose up -d`. |
| El arranque no termina | Revisa `docker compose ps` y `docker logs blog_neo4j`; el script espera mientras el estado no sea saludable. |
| No se puede conectar a Neo4j | Comprueba el contenedor, el puerto 7687 y los valores de `app/db.py`. Ejecuta `test_conexion.py`. |
| Error de autenticación | Verifica la contraseña de la base existente; un volumen conserva su configuración anterior. |
| Puerto ocupado | Libera 7474/7687 o cambia el puerto del host en Compose. Si cambias el de Bolt, ajusta la URI de Python; si cambias el HTTP, usa la nueva URL del Browser. |
| `ModuleNotFoundError` | Instala `requirements.txt` usando el mismo Python del entorno virtual que ejecuta la app. |
| Ventana vacía o error de Tk en macOS | Comprueba Tk y usa `install_python.sh` si el intérprete no es compatible. |
| `No display name` o error de pantalla | Ejecuta la app dentro de una sesión gráfica, no en una terminal remota sin pantalla. |
| No aparecen artículos | Quita los filtros y verifica que existan nodos Article conectados con un autor por WROTE. |
| Faltan ejemplos tras ejecutar start.sh | El script solo carga ejemplos cuando no hay ningún nodo. No reconstruye automáticamente una base parcialmente llena. |
| Correo o nombre duplicado | Usa otro correo de usuario o nombre de categoría/etiqueta; el esquema impide esos duplicados. |
| Error por nombre de consulta | Verifica que el nombre usado en Python coincida con el marcador `// @nombre` del archivo Cypher. |

Para revisar la versión de Tcl/Tk desde `app/`:

```bash
.venv/bin/python -c "import tkinter as tk; print(tk.Tcl().eval('info patchlevel'))"
```

## Desarrollo y mantenimiento

- Conserva los nombres de consultas y los campos devueltos que utilizan las vistas.
- Define las consultas en `cypher/consultas.cypher` y pasa valores mediante parámetros.
- Si cambias restricciones, aplica `01_schema.cypher` y revisa los datos existentes.
- Reinicia la aplicación después de modificar el archivo de consultas: se carga al importar `db.py`.
- Tras cambios funcionales, ejecuta conexión e integración y revisa las pantallas afectadas.
- No uses el archivo de datos de ejemplo como una migración: reemplaza todo el grafo.
- Mantén las credenciales reales fuera del repositorio.
