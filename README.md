# Brazilian E-Commerce ETL

Pipeline ETL pour transformer les données Olist (e-commerce brésilien) en entrepôt de données analytique.

## Architecture

```
Bronze (CSV) → Silver (Nettoyage) → Gold (Star Schema)
```

- **Bronze** : Extraction des 9 fichiers CSV bruts
- **Silver** : Nettoyage, validation, enrichissement
- **Gold** : Modèle en étoile (6 dimensions, 6 faits) dans PostgreSQL

## Données Sources (Bronze)

| Table | Description |
|-------|-------------|
| orders | Commandes avec statut et dates (achat, approbation, livraison) |
| customers | Clients avec localisation (ville, état, code postal) |
| sellers | Vendeurs avec localisation |
| products | Catalogue produits (catégorie, poids, dimensions) |
| order_items | Détail des articles par commande (prix, frais de port) |
| order_payments | Paiements (type, mensualités, montant) |
| order_reviews | Avis clients (note 1-5, commentaire) |
| geolocation | Coordonnées GPS par code postal |
| category_translation | Traduction des catégories PT → EN |

## Modèle Gold

### Dimensions

| Table | Description |
|-------|-------------|
| dim_date | Calendrier (année, mois, trimestre, saison, weekend) |
| dim_product_categories | Catégories avec stats (nb produits, prix moyen) |
| dim_customers | Clients enrichis (nb commandes, total dépensé, panier moyen) |
| dim_products | Produits avec performance (quantité vendue, CA) |
| dim_sellers | Vendeurs avec performance (CA, note moyenne) |
| dim_geography | Géolocalisation (coordonnées, nb clients/vendeurs) |

### Faits

| Table | Description |
|-------|-------------|
| fact_orders | Commandes avec métriques (montant, livraison, retard) |
| fact_order_items | Articles commandés (prix, frais de port) |
| fact_daily_sales | Ventes agrégées par jour |
| fact_customer_lifetime | Valeur vie client, segmentation |
| fact_product_performance | Performance par produit (ventes, note moyenne) |
| fact_category_performance | Performance par catégorie (CA, classement) |

## Installation

```bash
# Environnement
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Base de données
psql -U postgres -c "CREATE DATABASE brazilian_ecommerce_db;"
```

## Utilisation

```bash
python main.py
```

## Structure

```
├── config/             # Configuration DB
├── data/raw/           # CSV sources
├── docs/               # Documentation détaillée
├── sql/                # Scripts SQL par couche
├── src/
│   ├── bronze/         # Extraction
│   ├── silver/         # Nettoyage (9 transformers)
│   ├── gold/           # Agrégation Star Schema
│   └── loaders/        # Chargement PostgreSQL
└── main.py
```

## Documentation

- [Règles de nettoyage](docs/cleaning_rules.md)
- [Modèle de données](docs/data_model.md)
- [Pipeline ETL](docs/etl_pipeline.md)
- [Tables Gold détaillées](docs/tables_gold.md)

## Stack

Python 3.12 · Pandas · PostgreSQL · SQLAlchemy · Loguru

---

Dataset : [Olist Brazilian E-Commerce (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
