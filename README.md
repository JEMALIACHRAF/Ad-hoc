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
1. **Méthodologie** :
   -Lecture des fichiers CSV :
    Chargement des données GPS, climatiques et d'activités avec pandas.
    Conversion des timestamps en format standardisé.
   -Validation des données :
    Vérification de la présence des colonnes essentielles (latitude, longitude, timestamps, etc.).
    Suppression des valeurs manquantes.
2. **Résultats** :
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
1. **Calcul de la vitesse entre points GPS**
   -Pour chaque point GPS, la distance entre lui et le point précédent est calculée à l’aide de la formule de Haversine.
   -Le temps écoulé entre les points est également mesuré.
   -Une distribution des vitesses est analysée pour détecter les anomalies.
2. **Filtrage des vitesses aberrantes**
   -Une seuil de 150 km/h est appliqué :
      Tous les points avec une vitesse calculée supérieure à ce seuil sont considérés comme aberrants et supprimés.
3. **Lissage des trajectoires**
   -Une moyenne mobile est appliquée sur les coordonnées GPS pour réduire les variations dues au bruit des capteurs GPS.
   -L'objectif est d’obtenir des trajectoires plus fluides et naturelles.
3. **Filtrage des points aberrants avec DBSCAN**
   -DBSCAN (Density-Based Spatial Clustering of Applications with Noise) est utilisé pour identifier les outliers :
      Il regroupe les points denses et élimine ceux qui ne font pas partie de groupes cohérents.
      Les coordonnées GPS sont converties en mètres pour assurer une meilleure précision.
   -Les valeurs aberrantes isolées (erreurs GPS ou artefacts de localisation) sont supprimées.
   
### Question 5 : Détection des Arrêts et Déplacements
#### Approche
1. **Définition des critères d’arrêt**
   -Un arrêt est défini comme une position stationnaire où l’utilisateur ne se déplace pas pendant un certain temps.
   -Deux paramètres clés sont utilisés :
         Distance seuil : 5 mètres .
         Durée seuil : 30 secondes .
2. **Calcul des distances successives entre points GPS**
   -La formule de Haversine est utilisée pour mesurer la distance entre chaque point GPS et le suivant.
   -Si la distance est inférieure à 5 mètres, on considère qu’il n’y a pas eu de mouvement significatif.
3. **Identification des périodes d’arrêt**
   -Pour chaque point GPS, on vérifie :
      Si l’utilisateur est resté dans un rayon de 5 mètres.
      Si la durée d’immobilité dépasse 30 secondes.
   -Si ces deux conditions sont remplies, le point est marqué comme un arrêt.
4. **Classification des segments en arrêts ou déplacements**
   -Une colonne "is_stop" est ajoutée aux données :
       True si l’utilisateur est à l’arrêt.
       False s’il est en mouvement.
   -Chaque segment est ainsi étiqueté comme arrêt ou déplacement.
   
### Question 6 : Segmentation Basée sur les Arrêts et Déplacements
#### Approche
1. **Création des segments d'arrêt et de déplacement**
   -Utilisation des résultats de la question 5 pour séparer les données en périodes d’arrêt (is_stop=True) et périodes de déplacement (is_stop=False).
   -Chaque segment reçoit un identifiant unique qui permet de l’identifier comme un arrêt ou un déplacement.
2. **Détermination des temps de début et de fin pour chaque segment**
   -Pour chaque arrêt, on stocke :
       start_time (premier point de l’arrêt).
       end_time (dernier point de l’arrêt).
   -Pour chaque déplacement, on stocke les temps de début et de fin de la séquence.
3. **Propagation aux données climatiques et d'activités**
   -Fusion temporelle des données GPS avec les données climatiques et d’activités en utilisant merge_asof().
   -Ajustement des tolérances temporelles pour maximiser les correspondances entre les arrêts/déplacements et les enregistrements climatiques.
   
### Question 7 : Validation des Arrêts Détectés par Rapport aux Activités Auto-Reportées
#### Approche
1. **Fusion des données détectées et auto-reportées**
   -Comparaison des arrêts détectés (is_stop=True) avec les activités auto-reportées enregistrées séparément.
   -Utilisation de merge_asof() pour associer chaque arrêt GPS aux activités manuellement déclarées, avec une tolérance temporelle de 2 minutes pour aligner les événements.
2. **Lissage des trajectoires avec le filtre de Kalman**
   -Application d'un filtrage de Kalman pour réduire le bruit GPS avant de détecter les arrêts.
   -Le filtre de Kalman est utilisé pour :
         Corriger les sauts anormaux des coordonnées GPS.
         Lisser la trajectoire en prenant en compte l’historique du mouvement.
   -Résultat attendu : une meilleure détection des arrêts et une réduction des faux positifs.
3. **Analyse des écarts entre les arrêts détectés et les activités auto-reportées**
   -Vérification des cas où :
         Un arrêt a été détecté, mais aucune activité n’a été déclarée.
          Une activité a été déclarée, mais aucun arrêt n’a été détecté.
   -Comparaison des durées et des localisations des arrêts.
4. **Optimisation des seuils de détection**
   -Test de différentes valeurs de distance et de durée d'arrêt pour maximiser le taux d’accord.
   -Comparaison des résultats avec et sans filtrage de Kalman.
5. **Analyse des discordances (mismatches)**
   -Identification des erreurs de détection :
         Cas où un arrêt court est ignoré car la durée est trop faible.
         Erreurs de localisation dues aux imprécisions GPS (réduites grâce à Kalman).
   -Création d’une colonne agreement :
          1 si l’arrêt détecté correspond à une activité déclarée.
          0 sinon.
6. **Calcul du taux d’accord entre détection et auto-report**
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


---
# MobilityDB Analysis: Air Quality Score (AQS) and Temporal Comparisons

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



