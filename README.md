# 📂 Analyse des Trajectoires et Arrêts
# MobilityDB Analysis - Trajectories and Stops


## 🔍 Bilan des Questions 9 à 14

### **👉 Question 9: Calcul des Centroides et des Distances des Segments d'Arrêt**
## 1️⃣ Create & Populate Tables

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
### 📅 **Prochaine étape : Question 15 (Air Quality Score - AQS) !** 🚀

