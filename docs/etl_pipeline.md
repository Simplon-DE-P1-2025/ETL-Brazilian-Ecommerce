## Configuration
- Les paramètres de connexion à la base de données sont définis dans le fichier `config/settings.py` et peuvent être surchargés via des variables d'environnement à partir du .env (voir `.env.example` exemplaire de .env).
	>  Utilisez le fichier `.env.example` comme modèle pour créer votre propre `.env`.
	>  le fichier `.env` est fourni pour faciliter la configuration des variables d'environnement nécessaires..

- Le paramètre `CHUNK_SIZE` permet de contrôler la taille des lots lors de l'insertion en base (par défaut : 10 000 lignes). Modifiez-le dans `config/settings.py` selon vos besoins pour optimiser les performances lors du chargement massif de données.
	> Adaptez `CHUNK_SIZE` selon la capacité de votre machine et la taille des jeux de données.

- Toute la journalisation est désormais assurée par la librairie [loguru](https://github.com/Delgan/loguru), qui offre une gestion moderne et centralisée des logs.


[← Retour au README](../README.md)

# Pipeline ETL

Architecture Medallion en 3 couches.

## Vue d'ensemble

```
CSV (9 fichiers) → Bronze → Silver → Gold → PostgreSQL
```

## Bronze

Extraction brute des CSV sans transformation.

Fichiers sources :
- `olist_orders_dataset.csv` (environ 100k lignes)
- `olist_customers_dataset.csv` (~100k)
- `olist_order_items_dataset.csv` (~112k)
- `olist_order_payments_dataset.csv` (~104k)
- `olist_order_reviews_dataset.csv` (~100k)
- `olist_products_dataset.csv` (~33k)
- `olist_sellers_dataset.csv` (~3k)
- `olist_geolocation_dataset.csv` (~1M)
- `product_category_name_translation.csv` (~71)

Module : `src/bronze/csv_extractor.py`

## Silver

Nettoyage et enrichissement.

Chaque table a son transformer dans `src/silver/cleaners/` :
- `orders_transformer.py` : filtrage temporel, imputation dates
- `customers_transformer.py` : validation codes postaux, états
- `products_transformer.py` : imputation poids/dimensions par catégorie
- etc.

Après transformation, `processor.py` filtre les orphelins pour garantir l'intégrité référentielle.

## Gold

Modélisation Star Schema.

`src/gold/aggregator.py` crée 12 tables :
- 6 dimensions : dim_date, dim_product_categories, dim_customers, dim_products, dim_sellers, dim_geography
- 6 faits : fact_order_items, fact_orders, fact_daily_sales, fact_customer_lifetime, fact_product_performance, fact_category_performance

## Chargement

`src/loaders/postgres_loader.py` charge les DataFrames dans PostgreSQL (schéma `gold`).

## Exécution

```bash
python main.py
```

Output :
```
[INFO] 9 datasets extracted successfully.
[INFO] 9 datasets cleaned successfully.
[INFO] 12 gold tables created successfully.
```