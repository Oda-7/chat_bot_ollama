#!/bin/bash
set -e

# Script d'entrypoint : attend postgres, applique les migrations Alembic, puis démarre uvicorn

POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-chatbot_user}"

echo "Entrypoint démarré"
echo "Vérification de la DB avec host=$POSTGRES_HOST db=$POSTGRES_DB user=$POSTGRES_USER"

# Attendre que la base soit disponible
until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
  echo "Attente de la disponibilité de la base de données..."
  sleep 2
done

echo "Base de données disponible, exécution des migrations Alembic..."
if command -v alembic >/dev/null 2>&1; then
  echo "Exécution d'alembic upgrade head (logs -> /app/logs/alembic.log)"
  mkdir -p /app/logs
  if ! alembic upgrade head > /app/logs/alembic.log 2>&1; then
    echo "Échec de l'exécution d'alembic upgrade head, voir /app/logs/alembic.log" >&2
    echo "--- ALEMBIC LOG START ---" >&2
    sed -n '1,200p' /app/logs/alembic.log >&2 || true
    echo "--- ALEMBIC LOG END ---" >&2
    exit 1
  fi
else
  echo "alembic introuvable dans le conteneur, vérifier l'image" >&2
fi

echo "Démarrage de uvicorn"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    echo "--- ALEMBIC LOG START ---" >&2
    sed -n '1,200p' /app/logs/alembic.log >&2 || true
    echo "--- ALEMBIC LOG END ---" >&2
    exit 1
  fi
else
  echo "alembic introuvable dans le conteneur, vérifier l'image" >&2
fi

echo "Démarrage de uvicorn"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
