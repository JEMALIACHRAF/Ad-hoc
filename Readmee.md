# 📊 Benchmark des Approches Utilisées dans Deux Articles

## 📌 Présentation des Articles

### **Article 1** : *Extracting Data from Text and Querying it via KGQA and BESt Queries* (Université de Cagliari)  
- Propose une approche pour l'extraction d'informations structurées à partir de textes non annotés et l'interrogation de ces données à l'aide de techniques avancées.
- Utilise la bibliothèque **OKgraph** pour extraire automatiquement des **graphes de connaissances (KG)**.
- Introduit des méthodes avancées de requêtage des KG via **Knowledge Graph Question Answering (KGQA)** et **By-Example Structured Queries (BEStQ)**.

### **Article 2** : *Simple Method for Ontology Automatic Extraction from Documents* (Institut Technologique Aéronautique, Brésil)  
- Propose une méthode simple et rapide pour l'extraction automatique d'ontologies à partir de documents.
- Utilise des techniques comme **l’analyse sémantique latente (LSA)**, **le clustering hiérarchique** et **WordNet** pour structurer l’information.
- Génère une **ontologie OWL standardisée** manipulable par des outils d'édition.

---

## 📌 Approches Utilisées pour l'Extraction d'Information

| Critère | Article 1 (OKgraph - KG Extraction) | Article 2 (Extraction Ontologique) |
|---------|-------------------------------------|-------------------------------------|
| **Type d’Information Extraite** | Graphe de connaissances (KG) | Ontologie OWL |
| **Méthodologie Principale** | - Extraction non supervisée basée sur les **word embeddings**.<br>- Exploitation des relations géométriques entre vecteurs. | - **Latent Semantic Analysis (LSA)** pour identifier les concepts.<br>- **Clustering hiérarchique** pour organiser les concepts.<br>- **WordNet** pour enrichir les relations. |
| **Tâches NLP** | - **Set Expansion** : Étendre une liste d’entités (ex: villes d’Italie).<br>- **Set Labeling** : Déterminer la classe d’un ensemble d’entités.<br>- **Relation Expansion** : Trouver des relations implicites entre paires d’entités.<br>- **Relation Labeling** : Identifier la nature des relations entre entités. | - Détection de **concepts-clés** à partir d’un corpus.<br>- Structuration des concepts sous forme de taxonomie.<br>- Génération automatique de **relations sémantiques** grâce à WordNet. |
| **Niveau de Supervision** | Complètement **non supervisé** (aucun besoin d’annotations). | Semi-supervisé (WordNet apporte une base lexicale). |
| **Formats Supportés** | Texte brut uniquement. | Texte brut et **documents XML**. |

### 💡 **Exemple d’Application**
- **Article 1 (OKgraph)** : Si on donne les mots *Milan*, *Rome*, *Bari*, l’algorithme de set expansion pourrait trouver *Turin*, *Venise*, etc.
- **Article 2 (Ontology Extraction)** : À partir d’un corpus de critiques de films, l’algorithme pourrait identifier des concepts comme *Action Movie*, *Crime Thriller*, *Hollywood*, et les organiser sous forme d’une hiérarchie.

---

## 📌 Approches Utilisées pour l’Interrogation des Données

| Critère | Article 1 (KGQA & BEStQ) | Article 2 (OWL Querying) |
|---------|--------------------------|--------------------------|
| **Méthodes de Requête** | - **KGQA (Knowledge Graph Question Answering)** : Traduction d'une question en langage naturel en requête SPARQL.<br>- **BEStQ (By-Example Structured Queries)** : Formulaire de type infobox pour interagir avec le graphe. | - Requêtage des ontologies via des outils standard OWL/SWRL.<br>- Compatibilité avec **Protégé** et autres éditeurs ontologiques. |
| **Modèle d’Utilisation** | Interaction utilisateur via des questions en **langage naturel** ou des formulaires structurés. | Manipulation via des éditeurs ontologiques et des requêtes **SPARQL**. |
| **Cas d’Utilisation** | Recherche intuitive d’informations dans une base de connaissances (ex: "Quelle est la capitale de l'Italie ?"). | Extraction de connaissances structurées pour intégration dans des systèmes experts ou moteurs de recherche. |

### 💡 **Exemple d’Application**
- **Article 1 (KGQA & BEStQ)** : L’utilisateur peut poser la question *"Quels sont les maires des villes en Toscane ?"*, et obtenir une réponse directement.
- **Article 2 (OWL Querying)** : Un expert en ontologies peut interroger une base OWL pour identifier des liens entre concepts.

---

## 📌 Forces et Faiblesses

| Critère | Article 1 (OKgraph - KGQA & BEStQ) | Article 2 (Ontology Extraction) |
|---------|-------------------------------------|-------------------------------------|
| **Forces** | - **Approche totalement non supervisée**.<br>- Permet d’extraire des relations implicites et de répondre en langage naturel.<br>- Intégration avec des **graphes de connaissances** existants. | - Facile à implémenter et adaptable à plusieurs **types de documents**.<br>- Résultat sous format OWL standard, exploitable dans des environnements professionnels.<br>- Exploitation de WordNet pour améliorer la qualité des relations sémantiques. |
| **Faiblesses** | - Fonctionne uniquement sur **texte brut**, pas de support pour XML ou bases de données structurées.<br>- Nécessite un entraînement sur un **large corpus**. | - **Moins interactif**, nécessite des requêtes formelles OWL.<br>- Dépendance à **WordNet**, qui peut ne pas couvrir tous les concepts. |

---

# 📌 Processus Détaillé des Deux Approches avec Exemples Concrets d’Inputs/Outputs
_(D’après les articles fournis)_

---

## 🔷 Article 1 : Extraction et Interrogation de Graphes de Connaissances avec OKgraph

### 🔹 Diagramme de Séquence
```mermaid
sequenceDiagram
    participant Utilisateur
    participant OKgraph
    participant NLP_Tools
    participant WordEmbeddings
    participant RDF_Store

    Utilisateur->>+NLP_Tools: Texte brut (documents, articles, corpus)
    NLP_Tools->>+OKgraph: Tokens et texte nettoyé (suppression stopwords, lemmatisation)
    OKgraph->>+WordEmbeddings: Génération des vecteurs de mots (Word2Vec, FastText)
    WordEmbeddings->>+OKgraph: Modèle d’embeddings (représentation vectorielle)
    OKgraph->>+OKgraph: Set Expansion (génération d’entités similaires)
    OKgraph->>+OKgraph: Set Labeling (assignation de catégories aux entités)
    OKgraph->>+OKgraph: Relation Expansion (détection de relations entre entités)
    OKgraph->>+OKgraph: Relation Labeling (nommage des relations)
    OKgraph->>+RDF_Store: Construction et stockage du Graphe de Connaissance (RDF, triples SPARQL)
    Utilisateur->>+OKgraph: Requête en langage naturel (ex: "Quelle est la capitale de l'Italie ?")
    OKgraph->>+RDF_Store: Traduction en requête SPARQL et exécution
    RDF_Store->>Utilisateur: Résultats formatés (ex: "Rome")
```

---

## 🔷 Article 2 : Extraction Automatique d’Ontologies à partir de Documents

### 🔹 Diagramme de Séquence
```mermaid
sequenceDiagram
    participant Utilisateur
    participant Preprocessing
    participant LSA_Clustering
    participant WordNet
    participant OWL_Store

    Utilisateur->>+Preprocessing: Texte brut/XML (corpus de documents, bases de données textuelles)
    Preprocessing->>+Preprocessing: Tokenisation, suppression des stopwords, TF-IDF
    Preprocessing->>+LSA_Clustering: Matrice terme-document générée
    LSA_Clustering->>+LSA_Clustering: Application de LSA (extraction de concepts latents)
    LSA_Clustering->>+LSA_Clustering: Clustering hiérarchique des concepts
    LSA_Clustering->>+WordNet: Vérification et enrichissement des concepts via WordNet (synonymes, hyperonymes)
    WordNet->>+OWL_Store: Génération et structuration de l’ontologie OWL
    Utilisateur->>+OWL_Store: Requête SPARQL sur l’ontologie (ex: "Quels films appartiennent au genre Thriller ?")
    OWL_Store->>Utilisateur: Résultats formatés (ex: "Inception, The Dark Knight")
```

---

## 📌 Conclusion et Recommandation

Les deux articles proposent des approches efficaces mais avec des objectifs différents :

- **Si l’objectif est d’extraire et d’interroger des connaissances sous forme de graphes de connaissances**, alors **l’approche OKgraph (Article 1)** est idéale, surtout si l'on veut **interagir en langage naturel**.
- **Si l’objectif est de construire des ontologies exploitables dans un système expert ou via OWL**, alors **l’approche basée sur LSA, clustering et WordNet (Article 2)** est plus appropriée.

### 🚀 **Recommandation**
- **Pour des applications orientées grand public** (ex: assistants IA, moteurs de réponse en langage naturel), privilégier **OKgraph et KGQA**.
- **Pour des applications orientées entreprise ou domaine spécifique** (ex: systèmes de gestion des connaissances, recherche sémantique avancée), privilégier **l’extraction ontologique via LSA et clustering**.

---

## 🎯 **Prochaines Étapes**
- **Tester l'intégration de OKgraph avec une base de données** pour voir sa robustesse.
- **Comparer les performances des requêtes SPARQL vs OWL** sur un même ensemble de données.
- **Explorer d'autres ontologies de référence** pour améliorer la qualité des relations extraites.

---

## 🔗 **Références**
- **[OKgraph Library](https://github.com/atzori/okgraph)**
- **[WordNet Project](https://wordnet.princeton.edu/)**
- **[Protégé - OWL Editor](https://protege.stanford.edu/)**


