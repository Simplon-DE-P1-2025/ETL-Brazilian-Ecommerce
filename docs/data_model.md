[← Retour au README](../README.md)
<p align="center">
	<img src="simplon_logo.png" alt="Simplon Logo" width="180"/>
</p>

---

**Auteur : Kaouter Rhazlani**  
Formation : Simplon Data Engineer P1 (2025-2027)

---
# Modèle de Données

Star Schema avec 6 dimensions et 6 tables de faits.

## Dimensions

### dim_date
Calendrier généré entre min/max des dates de commandes.
- `date_id` (YYYYMMDD), `date`, `year`, `month`, `day`, `quarter`
- `week`, `day_of_week`, `day_name`, `month_name`
- `is_weekend`, `is_month_start`, `is_month_end`
- `year_month`, `year_quarter`

### dim_product_categories
Catégories avec traduction et groupe général.
- `category_id`, `product_category_name`, `product_category_name_english`
- `general_category` (electronics, fashion, home_garden...)

### dim_customers
Clients avec localisation.
- `customer_id`, `customer_unique_id`
- `zip_code`, `city`, `state`, `region`

### dim_products
Catalogue avec caractéristiques physiques.
- `product_id`, `category_id`, `category_name`
- `weight_g`, `length_cm`, `height_cm`, `width_cm`, `volume_cm3`
- `photos_qty`

### dim_sellers
Vendeurs avec localisation.
- `seller_id`, `zip_code`, `city`, `state`, `region`

### dim_geography
27 états brésiliens.
- `state_code`, `region_name`, `population`

## Faits

### fact_orders
Une ligne par commande.
- `order_id`, `customer_id`, `date_id`, `order_status`
- `total_items`, `order_amount`, `payment_amount`
- `delivery_days`, `is_late`

### fact_order_items
Une ligne par article commandé.
- `order_id`, `order_item_id`, `product_id`, `seller_id`
- `customer_id`, `date_id`
- `price`, `freight_value`, `total_price`

### fact_daily_sales
Agrégation par jour.
- `date_id`, `total_orders`, `unique_customers`
- `total_revenue`, `avg_delivery_days`

### fact_customer_lifetime
Métriques par client avec segmentation.
- `customer_unique_id`, `total_orders`, `lifetime_value`, `avg_order_value`
- `cancellation_rate`, `customer_segment`
- `state`, `region`

Segments : Champions, Loyal, Potential Loyalists, At Risk, Needs Attention

### fact_product_performance
Performance par produit.
- `product_id`, `category_id`
- `total_orders`, `total_units_sold`, `total_revenue`
- `avg_price`, `avg_review_score`

### fact_category_performance
Performance par catégorie.
- `category_id`, `category_name`, `general_category`
- `total_products`, `total_revenue`
- `revenue_share_pct`, `revenue_rank`
