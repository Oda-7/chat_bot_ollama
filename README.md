# 🤖 ChatBot avec Clean Architecture - Documentation Complète

## 📋 Vue d'ensemble

Système de chatbot moderne utilisant **FastAPI**, **React**, **PostgreSQL** suivant les principes de **Clean Architecture** et **SOLID**.

### 🎯 Objectifs

- ✅ **Clean Architecture** avec séparation des couches
- ✅ **Backend FastAPI** avec authentification JWT
- ✅ **Chatbot IA** avec Ollama et RAG (Retrieval-Augmented Generation)
- ✅ **Base de données PostgreSQL** avec préfixe `t7_`
- ⏳ **Frontend React** (prévu)

---

## 🏗️ Architecture Clean

### Structure des Dossiers

```
backend/
├── app/
│   ├── core/           # 🎛️ Configuration, sécurité, logging (exceptions, logging, sécurity, settings)
│   ├── domain/         # 🏛️ Entités métier (entities, interfaces, constants)
│   ├── infrastructure/ # 🔧 Accès données, services externes (repostirories, services)
│   ├── application/    # 📋 Services métier, use cases (commands, queries, dto, validators)
│   └── api/           # 🌐 Contrôleurs REST API (endpoints)
├── logs/              # 📝 Logs de l'application
├── venv/              # 🐍 Environnement Python
└── requirements.txt   # 📦 Dépendances
```

### Backend

- **FastAPI 0.104.1** : Framework REST moderne et rapide
- **SQLAlchemy 2.0.23** : ORM pour PostgreSQL
- **Alembic 1.12.1** : Migrations de base de données
- **PostgreSQL + pgvector** : Base de données avec support embeddings
- **Argon2** : Hachage sécurisé des mots de passe
- **JWT** : Authentification stateless
- **Loguru** : Logging structuré

### IA & RAG

- **Ollama 0.1.8** : Runtime pour modèles LLM locaux
- **LangChain 0.0.350** : Framework pour applications IA
- **ChromaDB 0.4.18** : Base vectorielle pour RAG
- **Sentence-Transformers** : Génération d'embeddings

### Infrastructure

- **Docker** : Conteneurisation PostgreSQL
- **pgAdmin** : Interface graphique base de données

---

## 🚀 Installation Automatique (RECOMMANDÉ)

### Démarrage en Une Commande

````powershell
# Cloner le projet
git clone <repo-url>
cd chatbot

## 🔐 Configuration des Variables d'Environnement

#### 1. Copiez le template

```bash
cp .env.example .env
```

#### 2. Personnalisez les valeurs

Éditez le fichier `.env` et remplacez les valeurs par défaut :

- **Mots de passe** : Changez TOUS les mots de passe
- **Clés secrètes** : Générez de nouvelles clés pour la production


# Run de l'application
docker compose -up --build


# Run de l'application
docker compose -up --build
````
