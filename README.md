# Documentation du Système RAG basé sur des Microservices

## Table des Matières
- [1. Introduction](#1-introduction)
- [2. Architecture du Système](#2-architecture-du-système)
- [3. Rôle de chaque Microservice](#3-rôle-de-chaque-microservice)
  - [3.1 Chat Agent Service](#31-chat-agent-service)
  - [3.2 Indexing Service](#32-indexing-service)
  - [3.3 Media Service](#33-media-service)
  - [3.4 Module Partagé](#34-module-partagé)
- [4. Déploiement et Tests](#4-déploiement-et-tests)
  - [4.1 Déploiement avec Kubernetes](#41-déploiement-avec-kubernetes)
  - [4.2 Tests des Services](#42-tests-des-services)
- [5. Interaction des Services](#5-interaction-des-services)

---

## 1. Introduction

Ce document décrit un système RAG (Retrieval-Augmented Generation) basé sur une architecture de microservices. Il inclut une vue d'ensemble des composants, leur rôle, les étapes de déploiement, et la manière dont les services interagissent pour fournir des réponses enrichies aux utilisateurs.

## 2. Architecture du Système

Le système est composé de trois microservices principaux et d’un module partagé :
- **Chat Agent Service** : Agent conversationnel.
- **Indexing Service** : Service d'indexation de documents.
- **Media Service** : Service de traitement multimédia.
- **Module Partagé** : Gestion des index vectoriels.

### Diagramme de l’Architecture
```plaintext
                           ┌──────────────────────────┐
                           │  Client Utilisateur      │
                           └──────────┬──────────────┘
                                      │
                        ┌─────────────▼──────────────┐
                        │  Chat Agent Service        │
                        │  (chat_agent_service.py)   │
                        └───────┬───────────┬───────┘
                                │           │
                  ┌─────────────▼───┐    ┌──▼───────────────┐
                  │Indexing Service │    │ Media Service    │
                  │(indexing_serv.) │    │ (media_service)  │
                  └─────────────┬───┘    └──┬───────────────┘
                                │           │
                       ┌────────▼───────────▼───────┐
                       │  Stockage et Index Vector. │
                       │  (vector_index_utils.py)  │
                       └───────────────────────────┘
```

---

## 3. Rôle de chaque Microservice

### 3.1 **Chat Agent Service**

- **Fichier principal** : `chat_agent_service.py`
- **Rôle** :
  - Fournir un agent conversationnel qui répond aux requêtes utilisateur.
  - Utiliser un modèle LLM (GPT-3.5 Turbo) et un agent ReAct pour analyser et répondre aux requêtes.
  - Intégrer un moteur de recherche sémantique pour extraire les informations pertinentes des documents indexés.
- **Points clés** :
  - Modèle LLM configuré avec des embeddings HuggingFace.
  - Réponses enrichies avec contexte.

---

### 3.2 **Indexing Service**

- **Fichier principal** : `indexing_service.py`
- **Rôle** :
  - Gérer l’indexation de documents PDF, TXT et Markdown.
  - Transformer les documents en représentations vectorielles.
  - Ajouter ces représentations à un index vectoriel centralisé.
- **Fonctionnalités clés** :
  - Traitement automatique des documents avec des pipelines de transformation.
  - Gestion des métadonnées pour chaque document indexé.

---

### 3.3 **Media Service**

- **Fichier principal** : `media_service.py`
- **Rôle** :
  - Télécharger et analyser les contenus multimédias (vidéos, images).
  - Extraire des données (audio, frames, transcription) pour créer des documents textuels.
  - Indexer ces données pour une recherche ultérieure.
- **Fonctionnalités clés** :
  - Intégration avec Google Cloud Vision pour l’OCR.
  - Génération de notes détaillées à partir de vidéos.

---

### 3.4 **Module Partagé : Gestion des Index Vectoriels**

- **Fichier principal** : `vector_index_utils.py`
- **Rôle** :
  - Fournir une interface pour créer, mettre à jour et récupérer l'index vectoriel.
  - Assurer un stockage persistant et une utilisation partagée entre les services.
- **Fonctionnalités clés** :
  - Embeddings basés sur Hugging Face.
  - Pipeline d’ingestion configuré pour une segmentation optimisée des documents.

---

## 4. Déploiement et Tests

### 4.1 Déploiement avec Kubernetes

Les services sont déployés via des manifestes YAML, chacun décrivant un déploiement et un service Kubernetes associé.

#### **Commandes de Déploiement**
```sh
kubectl apply -f shared-volume.yml
kubectl apply -f indexing-service-deployment.yml
kubectl apply -f media-service-deployment.yml
kubectl apply -f chat-agent-service-deployment.yml
```

#### **Fichiers YAML Principaux**
- **Indexing Service** : `indexing-service-deployment.yml`
- **Chat Agent Service** : `chat-agent-service-deployment.yml`
- **Media Service** : `media-service-deployment.yml`
- **Volume Partagé** : `shared-volume.yml`

### 4.2 Tests des Services

Utilisez cURL ou Postman pour interagir avec chaque service :

#### **Indexer un Document**
```sh
curl -X POST "http://indexing-service:8001/indexing/ingest" -F "file=@test.pdf"
```

#### **Poser une Question au Chat Agent**
```sh
curl -X POST "http://chat-agent-service:8003/chat/chat-with-agent" -H "Content-Type: application/json" -d '{"query": "Quels documents sont disponibles ?"}'
```

#### **Indexer une Vidéo via le Media Service**
```sh
curl -X POST "http://media-service:8002/media/process-and-index" -H "Content-Type: application/json" -d '{"url": "https://youtube.com/video"}'
```

---

## 5. Interaction des Services

### Flux d’Interaction

1. **Indexation** : Les documents soumis via le `Indexing Service` sont transformés et ajoutés à l’index vectoriel.
2. **Requête Utilisateur** : Les utilisateurs posent des questions au `Chat Agent Service`.
3. **Recherche Sémantique** : Le `Chat Agent Service` interroge l’index vectoriel pour récupérer les documents pertinents.
4. **Génération de Réponses** : Les réponses sont générées en tenant compte du contexte des documents récupérés.
5. **Traitement Multimédia** : Le `Media Service` traite les vidéos et images pour enrichir les données indexées.

### Points Clés
- **Persistant** : Les données restent accessibles grâce à l’index partagé.
- **Optimisé** : Les pipelines garantissent une recherche rapide et pertinente.
- **Scalable** : Kubernetes permet une montée en charge selon les besoins.

---

### Merci d’utiliser notre système RAG pour une gestion intelligente des connaissances.

