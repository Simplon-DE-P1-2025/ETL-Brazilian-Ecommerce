[← Retour au README](../README.md)
<p align="center">
	<img src="simplon_logo.png" alt="Simplon Logo" width="180"/>
</p>

---

**Auteur : Kaouter Rhazlani**  
Formation : Simplon Data Engineer P1 (2025-2027)

---
# Règles de Nettoyage

## Filtrage Temporel

On garde uniquement la période **2017-01-01 → 2018-08-31**.

Pourquoi :
- Avant 2017 : données incomplètes (1 commande en sept 2016)
- Après août 2018 : quasi uniquement des commandes annulées

## Intégrité Référentielle

Après filtrage des orders, on supprime les orphelins dans les tables liées :

| Table | Orphelins supprimés |
|-------|---------------------|
| customers | ~349 |
| payments | ~365 |
| reviews | ~13 |
| order_items | ~371 |

## Par Table

### Orders
- Dates manquantes → imputation avec délai médian
- Dates incohérentes (livraison < achat) → NaT
- Statuts invalides → 'processing' (valeur neutre qui ne fausse pas les stats de livraison ni d'annulation)

### Customers / Sellers
- Doublons → suppression
- Code postal hors [01000, 99999] → exclus
- État hors des 27 états brésiliens → exclus

### Products
- Catégorie manquante → 'unknown'
- Poids = 0 → médiane de la catégorie
- Dimensions manquantes → médiane par catégorie

### Payments
- Types valides : credit_card, boleto, voucher, debit_card
- Montants négatifs → 0
- Mensualités hors [1, 24] → ramenées aux bornes (0 devient 1, 36 devient 24)

### Reviews
- Score hors [1-5] → NaN
- Commentaires manquants → chaîne vide

### Order Items
- Prix/frais négatifs → 0

### Geolocation
- Coordonnées invalides → exclus
- Agrégation par code postal (moyenne)

## Métriques Ajoutées

### Orders

| Métrique | Calcul | Utilité |
|----------|--------|---------|
| `delivery_days` | Date livraison - Date achat | Mesurer le délai de livraison réel |
| `delivery_delta_days` | Date livraison - Date estimée | Savoir si livré en avance ou en retard |
| `is_delivered` | Vrai si statut = 'delivered' | Filtrer les commandes terminées |
| `is_late` | Vrai si delivery_delta_days > 0 | Identifier les retards de livraison |
| `delivery_time_category` | Fast (≤5j), Medium (5-15j), Long (>15j) | Catégoriser la rapidité de livraison |
| `purchase_season` | Été/Automne/Hiver/Printemps (hémisphère sud) | Analyser la saisonnalité des ventes |
| `purchase_day_type` | Weekend ou Weekday | Comparer comportement semaine vs weekend |
| `purchase_time_of_day` | Morning/Afternoon/Evening/Night | Identifier les pics horaires d'achat |

### Products

| Métrique | Calcul | Utilité |
|----------|--------|---------|
| `product_volume_cm3` | Longueur × Hauteur × Largeur | Estimer l'encombrement pour la logistique |

### Customers/Sellers

| Métrique | Calcul | Utilité |
|----------|--------|---------|
| `state_name` | Correspondance sigle → nom complet | Lisibilité (SP → São Paulo) |
| `region` | Correspondance état → région | Analyser les ventes par grande région du Brésil |
