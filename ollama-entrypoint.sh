#!/bin/sh
echo "Démarrage du serveur Ollama..."
ollama serve &
sleep 10
echo "Téléchargement du modèle mistral:7b..."
ollama pull mistral:7b
wait