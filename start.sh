#!/usr/bin/env bash
# Levanta Neo4j, carga los archivos Cypher y prepara el entorno Python.
set -euo pipefail
cd "$(dirname "$0")"

CYPHER="docker exec -i blog_neo4j cypher-shell -u neo4j -p admin12345"

echo "==> Verificando Docker..."
if ! docker info >/dev/null 2>&1; then
  echo "Docker no está listo. Abre Docker Desktop y vuelve a ejecutar este script."
  open -a Docker 2>/dev/null || open /Applications/Docker.app || true
  exit 1
fi

echo "==> Levantando Neo4j (docker compose up -d)..."
docker compose up -d

echo "==> Esperando que Neo4j esté saludable (la 1ª vez puede tardar un par de minutos)..."
until [ "$(docker inspect -f '{{.State.Health.Status}}' blog_neo4j 2>/dev/null)" = "healthy" ]; do
  sleep 5
  echo "    ...aún inicializando..."
done
echo "==> Neo4j listo."

echo "==> Aplicando restricciones (cypher/01_schema.cypher)..."
$CYPHER < cypher/01_schema.cypher

# Los datos de ejemplo solo se cargan si el grafo está vacío (02_seed.cypher borra todo).
NODOS=$($CYPHER --format plain "MATCH (n) RETURN count(n)" </dev/null | tail -n 1)
if [ "$NODOS" = "0" ]; then
  echo "==> Grafo vacío: cargando datos de ejemplo (cypher/02_seed.cypher)..."
  $CYPHER < cypher/02_seed.cypher
else
  echo "    El grafo ya tiene datos; se omiten los datos de ejemplo."
fi

echo "==> Preparando entorno Python..."
cd app
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
.venv/bin/python test_conexion.py

echo ""
echo "Listo. Para abrir la GUI:"
echo "  cd app && TK_SILENCE_DEPRECATION=1 .venv/bin/python main_gui.py"
