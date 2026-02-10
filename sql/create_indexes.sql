-- Index pour optimiser les requêtes analytiques
-- Exécuté après le chargement des données

-- === SILVER ===

-- Orders : recherche par période
CREATE INDEX IF NOT EXISTS idx_orders_year_month 
ON silver.orders(purchase_year, purchase_month);

-- Orders : filtrer les retards
CREATE INDEX IF NOT EXISTS idx_orders_late 
ON silver.orders(is_late) WHERE is_late = true;

-- Order items : jointures fréquentes
CREATE INDEX IF NOT EXISTS idx_order_items_product 
ON silver.order_items(product_id);

CREATE INDEX IF NOT EXISTS idx_order_items_seller 
ON silver.order_items(seller_id);

-- Reviews : jointure avec orders
CREATE INDEX IF NOT EXISTS idx_reviews_order 
ON silver.reviews(order_id);

-- Payments : jointure avec orders
CREATE INDEX IF NOT EXISTS idx_payments_order 
ON silver.payments(order_id);


-- === GOLD ===

-- fact_orders : recherche par date et statut
CREATE INDEX IF NOT EXISTS idx_fact_orders_date 
ON gold.fact_orders(date_id);

CREATE INDEX IF NOT EXISTS idx_fact_orders_status 
ON gold.fact_orders(order_status);

-- fact_order_items : jointures dimensions
CREATE INDEX IF NOT EXISTS idx_fact_items_product 
ON gold.fact_order_items(product_id);

CREATE INDEX IF NOT EXISTS idx_fact_items_seller 
ON gold.fact_order_items(seller_id);

CREATE INDEX IF NOT EXISTS idx_fact_items_date 
ON gold.fact_order_items(date_id);

-- fact_customer_lifetime : analyse par segment/région
CREATE INDEX IF NOT EXISTS idx_customer_segment 
ON gold.fact_customer_lifetime(customer_segment);

CREATE INDEX IF NOT EXISTS idx_customer_region 
ON gold.fact_customer_lifetime(region);

-- fact_product_performance : tri par revenus
CREATE INDEX IF NOT EXISTS idx_product_perf_revenue 
ON gold.fact_product_performance(total_revenue DESC);