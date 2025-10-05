# Frontend React avec TypeScript et Material-UI
FROM node:18.20.3-alpine

WORKDIR /app

# Copier les fichiers package
COPY package*.json ./

# Installer les dépendances de production uniquement (pour optimiser la taille)
RUN npm ci --only=production && npm cache clean --force

# Copier le code source
COPY . .

# Copier l'entrypoint runtime qui génère public/env-config.js
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Exposer le port de développement
EXPOSE 3000

# Variables d'environnement pour React
ENV REACT_APP_API_BASE_URL=http://backend:8000

# Entrypoint qui génère env-config puis démarre
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
