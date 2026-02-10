[← Retour au README](../README.md)
<p align="center">
	<img src="simplon_logo.png" alt="Simplon Logo" width="180"/>
</p>

---

**Auteur : Kaouter Rhazlani**  
Formation : Simplon Data Engineer P1 (2025-2027)

---
# Tables Gold - Guide Détaillé

Ce document explique chaque table du modèle Gold.

---

## Star Schema

C'est une organisation des données en étoile :
- Au centre : les **tables de faits** (les événements avec des chiffres)
- Autour : les **tables de dimensions** (le contexte : qui, quoi, où, quand)

Ça permet de faire des analyses croisées facilement. Par exemple : "ventes par région et par mois".

---

## Dimensions

### dim_date

Calendrier généré automatiquement entre la première et la dernière commande.

| Colonne | Description |
|---------|-------------|
| date_id | Identifiant au format YYYYMMDD (ex: 20170515) |
| date | La date elle-même |
| year | Année |
| quarter | Trimestre (1 à 4) |
| month | Mois (1 à 12) |
| month_name | Nom du mois (January, February...) |
| week | Numéro de semaine |
| day | Jour du mois |
| day_name | Nom du jour (Monday, Tuesday...) |
| day_of_week | Numéro du jour (0 = lundi) |
| is_weekend | Vrai si samedi ou dimanche |
| is_month_start | Vrai si premier jour du mois |
| is_month_end | Vrai si dernier jour du mois |
| year_month | Format YYYY-MM |
| year_quarter | Format YYYY-Q1, YYYY-Q2... |

---

### dim_product_categories

Liste des catégories de produits avec leur traduction.

| Colonne | Description |
|---------|-------------|
| category_id | Identifiant auto-généré |
| product_category_name | Nom en portugais |
| product_category_name_english | Nom en anglais |
| general_category | Groupe général (electronics, fashion, home_garden, etc.) |

Les groupes généraux regroupent les catégories similaires :
- **furniture** : meubles, décoration, literie
- **electronics** : ordinateurs, téléphones, électroménager
- **fashion** : vêtements, chaussures, accessoires
- **home_garden** : maison, jardin, animaux
- **entertainment** : sports, jouets, musique
- **beauty_health** : beauté, santé, bébé
- **food_drinks** : alimentation, boissons
- **books_stationery** : livres, papeterie
- **auto** : automobile
- **other** : reste

---

### dim_customers

Liste des clients avec leur localisation.

| Colonne | Description |
|---------|-------------|
| customer_id | Identifiant technique du client |
| customer_unique_id | Identifiant unique (un client peut avoir plusieurs customer_id) |
| zip_code | Code postal |
| city | Ville |
| state | État brésilien (sigle : SP, RJ, MG...) |
| region | Région du Brésil (Southeast, South, Northeast...) |

---

### dim_products

Catalogue des produits avec leurs caractéristiques physiques.

| Colonne | Description |
|---------|-------------|
| product_id | Identifiant du produit |
| category_id | Lien vers dim_product_categories |
| category_name | Catégorie du produit |
| weight_g | Poids en grammes |
| length_cm | Longueur en centimètres |
| height_cm | Hauteur en centimètres |
| width_cm | Largeur en centimètres |
| volume_cm3 | Volume calculé (longueur × hauteur × largeur) |
| photos_qty | Nombre de photos du produit |

---

### dim_sellers

Liste des vendeurs avec leur localisation.

| Colonne | Description |
|---------|-------------|
| seller_id | Identifiant du vendeur |
| zip_code | Code postal |
| city | Ville |
| state | État brésilien |
| region | Région du Brésil |

---

### dim_geography

Liste des 27 états brésiliens avec leur région et population.

| Colonne | Description |
|---------|-------------|
| state_code | Sigle de l'état (SP, RJ, MG...) |
| region_name | Région (Southeast, South, Northeast, North, Center-West) |
| population | Population de l'état |

---

## Faits

### fact_order_items

Chaque ligne = un article dans une commande. C'est le niveau le plus détaillé.

| Colonne | Description |
|---------|-------------|
| order_id | Identifiant de la commande |
| order_item_id | Numéro de l'article dans la commande (1, 2, 3...) |
| product_id | Lien vers dim_products |
| seller_id | Lien vers dim_sellers |
| customer_id | Lien vers dim_customers |
| date_id | Lien vers dim_date |
| price | Prix de l'article |
| freight_value | Frais de livraison de l'article |
| total_price | Prix + frais de livraison |

---

### fact_orders

Chaque ligne = une commande. Agrège les informations des articles et paiements.

| Colonne | Description |
|---------|-------------|
| order_id | Identifiant de la commande |
| customer_id | Lien vers dim_customers |
| date_id | Lien vers dim_date |
| order_status | Statut (delivered, canceled, shipped...) |
| total_items | Nombre d'articles dans la commande |
| order_amount | Montant total des articles |
| payment_amount | Montant total payé |
| delivery_days | Nombre de jours de livraison |
| is_late | Vrai si livraison en retard par rapport à l'estimation |

---

### fact_daily_sales

Agrégation des ventes par jour. Une ligne = un jour.

| Colonne | Description |
|---------|-------------|
| date_id | Lien vers dim_date |
| total_orders | Nombre de commandes ce jour |
| unique_customers | Nombre de clients différents ce jour |
| total_revenue | Revenu total du jour |
| avg_delivery_days | Délai moyen de livraison des commandes du jour |

---

### fact_customer_lifetime

Métriques cumulées par client. Une ligne = un client.

| Colonne | Description |
|---------|-------------|
| customer_unique_id | Identifiant unique du client |
| total_orders | Nombre total de commandes passées |
| lifetime_value | Montant total dépensé |
| avg_order_value | Montant moyen par commande |
| cancellation_rate | Pourcentage de commandes annulées |
| customer_segment | Segment marketing (voir ci-dessous) |
| state | État du client |
| region | Région du client |

**Segments clients** (basés sur la récence et la fréquence d'achat) :
- **Champions** : Achat dans les 30 derniers jours ET au moins 3 commandes
- **Loyal** : Au moins 3 commandes
- **Potential Loyalists** : Achat dans les 60 derniers jours
- **At Risk** : Achat dans les 90 derniers jours
- **Needs Attention** : Reste

---

### fact_product_performance

Performance de chaque produit. Une ligne = un produit.

| Colonne | Description |
|---------|-------------|
| product_id | Identifiant du produit |
| category_id | Lien vers dim_product_categories |
| total_orders | Nombre de commandes contenant ce produit |
| total_units_sold | Nombre total d'unités vendues |
| total_revenue | Revenu total généré |
| avg_price | Prix moyen de vente |
| avg_review_score | Note moyenne des avis (1 à 5) |

---

### fact_category_performance

Performance de chaque catégorie. Une ligne = une catégorie.

| Colonne | Description |
|---------|-------------|
| category_id | Identifiant de la catégorie |
| category_name | Nom de la catégorie en anglais |
| general_category | Groupe général |
| total_products | Nombre de produits dans la catégorie |
| total_revenue | Revenu total de la catégorie |
| revenue_share_pct | Part du revenu total (en pourcentage) |
| revenue_rank | Classement par revenu (1 = meilleure catégorie) |
