#!/bin/sh
set -e

echo "Génération de public/env-config.js à partir des variables d'environnement..."


# Détection du mode pour choisir l'URL du backend
if [ "${NODE_ENV:-development}" = "production" ]; then
  API_BASE_URL="http://backend:8000"
else
  API_BASE_URL="http://localhost:8000"
fi

cat > /app/public/env-config.js <<EOF
window.__ENV = {
  REACT_APP_API_BASE_URL: "${API_BASE_URL}"
};
EOF

echo "Fichier public/env-config.js créé :"
ls -l /app/public/env-config.js || true

if [ "${NODE_ENV:-development}" = "production" ]; then
  echo "Mode production: servir le build statique"
  npm run build
  npm install -g serve >/dev/null 2>&1 || true
  exec serve -s build -l 3000
else
  echo "Mode développement: démarrage de npm start"
  exec npm start
fi