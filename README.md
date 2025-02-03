# Rapport sur l'Analyse des Données GPS et Climatiques

## Introduction
Ce projet porte sur l'analyse des données GPS, climatiques et d'activités auto-déclarées recueillies sur une semaine. Les objectifs incluent la segmentation, la visualisation, le nettoyage et l'analyse des trajectoires, ainsi que l'évaluation des activités par rapport aux données collectées.

### Données Utilisées
- **Données GPS** : Coordonnées spatiales collectées à haute fréquence.
- **Données Climatiques** : Paramètres à échantillonnage par minute (PM2.5, PM10, NO2, température, humidité).
- **Données d'Activités** : Changements contextuels enregistrés manuellement.

## Méthodologie

### Question 1 : Chargement des Données
#### Approche
1. **Lecture des fichiers CSV** :
   - Données GPS, climatiques et d'activités chargées via la librairie pandas.
   - Normalisation des horodatages pour assurer la cohérence temporelle.
2. **Validation des données** :
   - Vérification de la complétude des colonnes essentielles (timestamps, latitude, longitude, etc.).
   - Conversion des formats irréguliers en un format standard uniforme.

#### Résultats
- **GPS** :
  - 81 308 points collectés sur 7 jours.
  - Données prêtes pour une segmentation temporelle.
- **Climat** :
  - Données étendues à 8 jours en raison de l'échantillonnage à haute fréquence.
- **Activités** :
  - Alignement temporel avec les données GPS, préparant les activités à des analyses croisées.

### Question 2 : Segmentation des Données par Jour
#### Approche
1. **Filtrage Temporel** :
   - Application d'un filtre basé sur les dates uniques extraites des timestamps.
2. **Segmentation** :
   - Découpage des données en blocs journaliers.
3. **Validation** :
   - Comptage des jours uniques dans chaque fichier pour assurer l'intégrité des segments.

#### Résultats
- **GPS** :
  - 7 jours uniques confirmés (échantillons : 2019-10-21 à 2019-10-28, excluant le 2019-10-27).
- **Climat** :
  - 8 jours, reflétant un échantillonnage plus complet.
- **Activités** :
  - 7 jours alignés avec les segments GPS.

### Question 3 : Transformation en Types Spatiaux et Visualisation
#### Approche
1. **Conversion en Types Spatiaux** :
   - Utilisation de **GeoPandas** pour convertir les données GPS en types géographiques (Points).
   - Création de trajectoires spatiotemporelles à l'aide de **MovingPandas**.
2. **Visualisation des Trajectoires** :
   - Représentation des trajectoires journalières.
   - Cartographie des trajets combinés pour analyser les zones fréquentées.
3. **Exportation** :
   - Génération de fichiers GeoJSON pour une analyse future.

### Question 4 : Nettoyage des Trajectoires et Validation Visuelle
#### Approche
1. **Calcul de la Vitesse** :
   - La vitesse entre chaque point GPS est calculée en utilisant la distance de Haversine et les différences temporelles.
   - Les vitesses excessives (>150 km/h) sont filtrées.
2. **Lissage des Trajectoires** :
   - Application d'une moyenne mobile sur les coordonnées GPS pour réduire les fluctuations dues au bruit.
3. **Filtrage des Données avec DBSCAN** :
   - DBSCAN est utilisé pour identifier et supprimer les points aberrants dans les données GPS.
   - Chaque jour est traité séparément, avec conversion des coordonnées géographiques en mètres pour une meilleure précision.

### Question 5 : Détection des Arrêts et Déplacements
#### Approche
1. **Définition des Paramètres** :
   - Distance seuil pour identifier un arrêt : 5 mètres.
   - Durée seuil pour confirmer un arrêt : 30 secondes.
2. **Calcul des Arrêts et Déplacements** :
   - Identification des arrêts en fonction des seuils de distance et de durée.
   - Assignation d'un identifiant unique à chaque segment (arrêt ou déplacement).

### Question 6 : Segmentation Basée sur les Arrêts et Déplacements
#### Approche
1. **Création des Segments** :
   - Chaque arrêt et déplacement est associé à un identifiant de segment unique.
   - Détermination des temps de début et de fin pour chaque segment.
2. **Propagation aux Données Climatiques et d'Activités** :
   - Utilisation de la fonction `merge_asof` pour associer chaque segment aux données climatiques et d'activités correspondantes.
   - Ajustement des tolérances temporelles pour maximiser les correspondances.

### Question 7 : Validation des Arrêts Détectés par Rapport aux Activités Auto-Reportées
#### Approche
1. **Fusion des Données Détectées et Déclarées** :
   - Comparaison des arrêts détectés avec les arrêts auto-reportés en utilisant un appariement temporel précis.
   - Utilisation de `merge_asof` avec une tolérance de 2 minutes pour lier les événements GPS aux déclarations manuelles.
2. **Optimisation des Seuils de Détection** :
   - Ajustement des seuils de distance et de durée d'arrêt en testant différentes configurations.
   - Sélection des paramètres optimaux en maximisant le taux d'accord entre les arrêts détectés et déclarés.
3. **Analyse des Discordances (Mismatches)** :
   - Identification des écarts entre les arrêts auto-reportés et les arrêts détectés automatiquement.
   - Vérification des erreurs potentielles de détection à l'aide de visualisations des désaccords.
4. **Calcul du Taux d’Accord** :
   - Création d’une colonne binaire `agreement` indiquant si un arrêt détecté correspond à un arrêt auto-reporté.
   - Calcul du pourcentage de correspondance entre les deux sources.

### Résultats Globaux
- **Taux d'Accord Global** : 69.09 % des arrêts détectés coïncident avec les arrêts auto-reportés.
- **Erreurs de Détection** :
  - Nombre total de mismatches : 17.
  - Des erreurs surviennent principalement lorsque les arrêts auto-reportés sont de très courte durée ou mal alignés temporellement avec les données GPS.
- **Optimisation des Paramètres** :
  - Seuil optimal trouvé : arrêt détecté si la distance < **5 mètres** et la durée > **5 secondes**.



# 📂 Analyse des Trajectoires et Arrêts
# MobilityDB Analysis - Trajectories and Stops


## 🔍 Bilan des Questions 9 à 14

### **👉 Question 9  Create & Populate Tables**
### ✅ Create the `trajectories` Table
```sql
CREATE TABLE trajectories (
    id SERIAL PRIMARY KEY,
    traj_id TEXT,
    geometry GEOMETRY(LineString, 4326),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    is_stop BOOLEAN
);
```

### ✅ Create the `json_import` Table
```sql
CREATE TABLE json_import (
    id SERIAL PRIMARY KEY,
    data JSONB
);
```

### ✅ Load the MF-JSON Data into `json_import`
```sql
INSERT INTO json_import (data)
SELECT jsonb_array_elements(pg_read_file('/tmp/trajectories_mf.json')::jsonb);
```

### ✅ Insert Data into `trajectories` Table
```sql
INSERT INTO trajectories (traj_id, geometry, start_time, end_time, is_stop)
SELECT
    data->>'id' AS traj_id,
    ST_GeomFromGeoJSON(
        jsonb_build_object(
            'type', 'LineString',
            'coordinates', data->'geometry'->'coordinates'
        )::TEXT
    ) AS geometry,
    (data->'properties'->>'start_time')::TIMESTAMP AS start_time,
    (data->'properties'->>'end_time')::TIMESTAMP AS end_time,
    (data->'properties'->>'is_stop')::BOOLEAN AS is_stop
FROM json_import;
```
---
### **👉 Question 10: Calcul des Centroides et des Distances des Segments d'Arrêt**
#### 🌟 Objectif :
Déterminer la localisation centrale de chaque arrêt, sa durée et l'incertitude de sa position via la distance maximale par rapport à son enveloppe convexe.

#### 📝 Requête SQL :
```sql
SELECT
    id AS stop_id,
    ST_Centroid(geometry) AS centroid,
    start_time,
    end_time,
    end_time - start_time AS duration,
    ST_MaxDistance(geometry, ST_Envelope(geometry)) AS max_bbox_distance
FROM trajectories
WHERE is_stop = TRUE;
```
#### 📊 Analyse des Résultats :
- Chaque **stop_id** représente un segment d'arrêt identifié.
- **ST_Centroid(geometry)** permet d'obtenir un point central approximatif de l'arrêt.
- **ST_MaxDistance()** donne la distance maximale entre le centroid et l'enveloppe convexe, indiquant le niveau d'incertitude de la position de l'arrêt.
- Exemples :
  - `stop_id = 1` a duré **5min 56s** avec une incertitude de **5.67e-6 degrés**.
  - `stop_id = 23` a duré **6h11min**, possiblement une résidence.

---
### **👉 Question 11: Identification des Arrêts Récurrents**
#### 🌟 Objectif :
Associer les arrêts proches et dont les boîtes englobantes s'intersectent sous une même **stop_id**.

#### 📝 Requête SQL :
```sql
WITH stop_clusters AS (
    SELECT
        t1.id AS stop1_id,
        t2.id AS stop2_id,
        ST_Distance(ST_Centroid(t1.geometry), ST_Centroid(t2.geometry)) AS centroid_distance,
        ST_Intersects(ST_Envelope(t1.geometry), ST_Envelope(t2.geometry)) AS bbox_intersection
    FROM trajectories t1
    JOIN trajectories t2 ON t1.id < t2.id
    WHERE t1.is_stop = TRUE AND t2.is_stop = TRUE
)
UPDATE trajectories
SET stop_id = stop1_id
FROM stop_clusters
WHERE trajectories.id = stop_clusters.stop2_id
AND centroid_distance < 50 -- Seulement si les stops sont à moins de 50m
AND bbox_intersection = TRUE;
```
#### 📊 Analyse des Résultats :
- **201 arrêts ont été regroupés** sous des identifiants communs.
- Exemples :
  - `stop_id = 1` (45 visites)
  - `stop_id = 178` (36 visites)

---
### **👉 Question 12: Classement des Arrêts par Fréquence et Durée**
#### 🌟 Objectif :
Identifier les arrêts les plus visités et les plus longs.

#### 📝 Requêtes SQL :
**Classement par Fréquence :**
```sql
SELECT stop_id, COUNT(*) AS visit_count
FROM trajectories
WHERE is_stop = TRUE
GROUP BY stop_id
ORDER BY visit_count DESC;
```
**Classement par Durée Totale :**
```sql
SELECT stop_id, SUM(end_time - start_time) AS total_duration
FROM trajectories
WHERE is_stop = TRUE
GROUP BY stop_id
ORDER BY total_duration DESC;
```
#### 📊 Analyse :
- **Stop_id 1** est le plus visité (**45 visites**).
- **Stop_id 269** a la plus longue durée cumulée (**12h13min**).

**Attribution des labels "Home" et "Work" :**
```sql
UPDATE trajectories
SET stop_label = 'Home'
WHERE stop_id = (SELECT stop_id FROM trajectories WHERE is_stop = TRUE GROUP BY stop_id ORDER BY COUNT(*) DESC LIMIT 1);

UPDATE trajectories
SET stop_label = 'Work'
WHERE stop_id = (SELECT stop_id FROM trajectories WHERE is_stop = TRUE GROUP BY stop_id ORDER BY COUNT(*) DESC OFFSET 1 LIMIT 1);
```

---
### **👉 Question 13: Classement des Trajectoires Mobiles par Distance et Durée**
#### 🌟 Objectif :
Trouver les trajets les plus longs en distance et en temps.

#### 📝 Requêtes SQL :
**Distance Totale :**
```sql
SELECT id, SUM(ST_Length(geometry::geography)) AS total_distance
FROM trajectories
WHERE is_stop = FALSE
GROUP BY id
ORDER BY total_distance DESC;
```
**Durée Totale :**
```sql
SELECT id, SUM(end_time - start_time) AS total_duration
FROM trajectories
WHERE is_stop = FALSE
GROUP BY id
ORDER BY total_duration DESC;
```
#### 📊 Analyse :
- Le trajet `id = 409` est le plus long (**57.2 km**, **9h52min**).
- Le trajet `id = 314` est le 2ᵗʰ plus long (**15.4 km**, **3h03min**).

---
### **👉 Question 14: Identification des Trajectoires Répétées**
#### 🌟 Objectif :
Trouver des trajectoires similaires selon différents critères.

#### 📝 Requêtes SQL :
**Distances Similaires :**
```sql
SELECT t1.id, t2.id,
       ABS(ST_Length(t1.geometry::geography) - ST_Length(t2.geometry::geography)) AS distance_diff
FROM trajectories t1
JOIN trajectories t2 ON t1.id < t2.id
WHERE t1.is_stop = FALSE AND t2.is_stop = FALSE
ORDER BY distance_diff
LIMIT 10;
```
**Points de Départ et d'Arrivée Similaires :**
```sql
SELECT t1.id AS traj1, t2.id AS traj2
FROM trajectories t1
JOIN trajectories t2
ON t1.id < t2.id
WHERE t1.is_stop = FALSE AND t2.is_stop = FALSE
AND ST_DWithin(ST_StartPoint(t1.geometry)::geography, ST_StartPoint(t2.geometry)::geography, 100)
AND ST_DWithin(ST_EndPoint(t1.geometry)::geography, ST_EndPoint(t2.geometry)::geography, 100)
ORDER BY traj1, traj2;
```
**Distance de Hausdorff :**
```sql
SELECT t1.id AS traj1, t2.id AS traj2,
       ST_HausdorffDistance(t1.geometry, t2.geometry) AS shape_distance
FROM trajectories t1
JOIN trajectories t2 ON t1.id < t2.id
WHERE t1.is_stop = FALSE AND t2.is_stop = FALSE
ORDER BY shape_distance
LIMIT 10;
```
#### 📊 Analyse :
- Plusieurs trajets **exactement identiques** ont été détectés (**Hausdorff Distance = 0**).

---
# MobilityDB Analysis: Air Quality Score (AQS) and Temporal Comparisons

## **9️⃣ Create & Populate Tables**

### **1️⃣ Create the `trajectories` Table**
```sql
CREATE TABLE trajectories (
    id SERIAL PRIMARY KEY,
    traj_id TEXT,
    geometry GEOMETRY(LineString, 4326),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    is_stop BOOLEAN
);
```

### **2️⃣ Create the `json_import` Table**
```sql
CREATE TABLE json_import (
    id SERIAL PRIMARY KEY,
    data JSONB
);
```

### **3️⃣ Load the MF-JSON Data into `json_import`**
```sql
INSERT INTO json_import (data)
SELECT jsonb_array_elements(pg_read_file('/tmp/trajectories_mf.json')::jsonb);
```

### **4️⃣ Insert Data into `trajectories` Table**
```sql
INSERT INTO trajectories (traj_id, geometry, start_time, end_time, is_stop)
SELECT
    data->>'id' AS traj_id,
    ST_GeomFromGeoJSON(
        jsonb_build_object(
            'type', 'LineString',
            'coordinates', data->'geometry'->'coordinates'
        )::TEXT
    ) AS geometry,
    (data->'properties'->>'start_time')::TIMESTAMP AS start_time,
    (data->'properties'->>'end_time')::TIMESTAMP AS end_time,
    (data->'properties'->>'is_stop')::BOOLEAN AS is_stop
FROM json_import;
```

---

## **15️⃣ Compute Air Quality Score (AQS)**
### **Normalize PM2.5, PM10, and NO2 and compute AQS**
```sql
WITH normalized AS (
    SELECT *,
        (PM2_5 - MIN(PM2_5) OVER()) / NULLIF(MAX(PM2_5) OVER() - MIN(PM2_5) OVER(), 0) AS norm_PM2_5,
        (PM10 - MIN(PM10) OVER()) / NULLIF(MAX(PM10) OVER() - MIN(PM10) OVER(), 0) AS norm_PM10,
        (NO2 - MIN(NO2) OVER()) / NULLIF(MAX(NO2) OVER() - MIN(NO2) OVER(), 0) AS norm_NO2
    FROM trajectories
)
SELECT id, start_time, end_time,
       (norm_PM2_5 + norm_PM10 + norm_NO2) / 3 AS AQS
FROM normalized;
```

---

## **16️⃣ Rank Days by Ascending Cumulated AQS**
### **Aggregate AQS per day and rank in ascending order**
```sql
WITH daily_aqs AS (
    SELECT
        DATE(start_time) AS day,
        SUM((PM2_5 - MIN(PM2_5) OVER()) / NULLIF(MAX(PM2_5) OVER() - MIN(PM2_5) OVER(), 0) +
            (PM10 - MIN(PM10) OVER()) / NULLIF(MAX(PM10) OVER() - MIN(PM10) OVER(), 0) +
            (NO2 - MIN(NO2) OVER()) / NULLIF(MAX(NO2) OVER() - MIN(NO2) OVER(), 0)) / 3 AS total_AQS
    FROM trajectories
    GROUP BY day
)
SELECT day, total_AQS
FROM daily_aqs
ORDER BY total_AQS ASC;
```

---

## **17️⃣ Compare AQS Between Day/Night & Stops/Moves**
### **Compute AQS separately for day, night, stops, and moves**
```sql
WITH aqs_by_period AS (
    SELECT
        CASE
            WHEN EXTRACT(HOUR FROM start_time) BETWEEN 6 AND 18 THEN 'Day'
            ELSE 'Night'
        END AS time_period,
        is_stop,
        AVG((PM2_5 - MIN(PM2_5) OVER()) / NULLIF(MAX(PM2_5) OVER() - MIN(PM2_5) OVER(), 0) +
            (PM10 - MIN(PM10) OVER()) / NULLIF(MAX(PM10) OVER() - MIN(PM10) OVER(), 0) +
            (NO2 - MIN(NO2) OVER()) / NULLIF(MAX(NO2) OVER() - MIN(NO2) OVER(), 0)) / 3 AS avg_AQS,
        MIN((PM2_5 - MIN(PM2_5) OVER()) / NULLIF(MAX(PM2_5) OVER() - MIN(PM2_5) OVER(), 0) +
            (PM10 - MIN(PM10) OVER()) / NULLIF(MAX(PM10) OVER() - MIN(PM10) OVER(), 0) +
            (NO2 - MIN(NO2) OVER()) / NULLIF(MAX(NO2) OVER() - MIN(NO2) OVER(), 0)) / 3 AS min_AQS,
        MAX((PM2_5 - MIN(PM2_5) OVER()) / NULLIF(MAX(PM2_5) OVER() - MIN(PM2_5) OVER(), 0) +
            (PM10 - MIN(PM10) OVER()) / NULLIF(MAX(PM10) OVER() - MIN(PM10) OVER(), 0) +
            (NO2 - MIN(NO2) OVER()) / NULLIF(MAX(NO2) OVER() - MIN(NO2) OVER(), 0)) / 3 AS max_AQS
    FROM trajectories
    GROUP BY time_period, is_stop
)
SELECT time_period, is_stop, avg_AQS, min_AQS, max_AQS
FROM aqs_by_period
ORDER BY time_period, is_stop;
```

---



