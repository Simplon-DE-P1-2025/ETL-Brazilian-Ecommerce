# Chiffre d'affaires par mois
SALES_MONTHLY_QUERY = """
SELECT TO_CHAR(TO_DATE(date_id::text, 'YYYYMMDD'), 'YYYY-MM') AS year_month,
       SUM(order_amount) AS total_sales
FROM gold.fact_orders
GROUP BY year_month
ORDER BY year_month;
"""

# Chiffre d'affaires par année
SALES_YEARLY_QUERY = """
SELECT EXTRACT(YEAR FROM TO_DATE(date_id::text, 'YYYYMMDD'))::INT AS year,
       SUM(order_amount) AS total_sales
FROM gold.fact_orders
GROUP BY year
ORDER BY year;
"""

# Chiffre d'affaires par jour
SALES_DAILY_QUERY = """
SELECT TO_CHAR(TO_DATE(date_id::text, 'YYYYMMDD'), 'YYYY-MM-DD') AS day,
       SUM(order_amount) AS total_sales
FROM gold.fact_orders
GROUP BY day
ORDER BY day;
"""

TOP_PRODUCTS_QUERY = """
SELECT p.product_id, c.product_category_name_english AS category,
       ROUND(p.total_revenue::numeric, 2) AS total_revenue,
       p.total_units_sold,
       ROUND(p.avg_price::numeric, 2) AS avg_price
FROM gold.fact_product_performance p
LEFT JOIN gold.dim_product_categories c ON p.category_id = c.category_id
ORDER BY p.total_revenue DESC LIMIT 10;
"""

SALES_BY_CATEGORY_QUERY = """
SELECT c.product_category_name_english AS category,
       ROUND(SUM(p.total_revenue)::numeric, 2) AS total_sales,
       SUM(p.total_units_sold) AS total_units
FROM gold.fact_product_performance p
JOIN gold.dim_product_categories c ON p.category_id = c.category_id
GROUP BY 1
ORDER BY total_sales DESC;
"""

RFM_DISTRIBUTION_QUERY = """
SELECT
  rfm_label,
  COUNT(*) AS num_customers,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_customers
FROM gold.fact_customer_rfm
GROUP BY rfm_label
ORDER BY num_customers DESC;
"""

COHORT_LTV_QUERY = """
SELECT cohort_month,
       ROUND(AVG(lifetime_value)::numeric, 2) AS avg_ltv,
       COUNT(DISTINCT customer_unique_id) as num_clients
FROM (
  SELECT
    c.customer_unique_id,
    MIN(TO_CHAR(TO_DATE(f.date_id::text, 'YYYYMMDD'),'YYYY-MM')) AS cohort_month,
    SUM(f.order_amount) AS lifetime_value
  FROM gold.fact_orders f
  JOIN gold.dim_customers c ON f.customer_id = c.customer_id
  GROUP BY c.customer_unique_id
) AS cohort
GROUP BY cohort_month
ORDER BY cohort_month;
"""

GEO_SALES_QUERY = """
SELECT g.state_code, g.region_name, g.population,
       SUM(o.order_amount) AS total_sales
FROM gold.fact_orders o
JOIN gold.dim_customers c ON o.customer_id = c.customer_id
JOIN gold.dim_geography g ON c.state = g.state_code
GROUP BY g.state_code, g.region_name, g.population
ORDER BY total_sales DESC;
"""




# Top vendeurs
TOP_SELLERS_QUERY = """
SELECT
  i.seller_id,
  s.city,
  s.state,
  ROUND(SUM(i.total_price)::numeric, 2) AS total_sales,
  COUNT(i.order_id) AS nb_orders
FROM gold.fact_order_items i
JOIN gold.dim_sellers s ON i.seller_id = s.seller_id
GROUP BY 1,2,3
ORDER BY total_sales DESC
LIMIT 10;
"""

# Taux commandes en retard par mois
LATE_RATE_MONTHLY_QUERY = """
SELECT
  TO_CHAR(TO_DATE(date_id::text, 'YYYYMMDD'), 'YYYY-MM') AS year_month,
  ROUND((COUNT(CASE WHEN is_late THEN 1 END)::numeric / GREATEST(COUNT(*), 1))*100,2) AS late_pct
FROM gold.fact_orders
GROUP BY 1
ORDER BY 1;
"""

# Distribution score reviews
REVIEW_SCORE_DISTRIBUTION_QUERY = """
SELECT
  review_score,
  COUNT(*) AS nb_reviews,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_reviews
FROM gold.fact_order_reviews
GROUP BY review_score
ORDER BY review_score DESC;
"""

# Score moyen review par mois
REVIEW_SCORE_MONTHLY_QUERY = """
SELECT
  TO_CHAR(TO_DATE(date_id::text, 'YYYYMMDD'), 'YYYY-MM') AS year_month,
  ROUND(AVG(review_score)::numeric, 2) AS avg_score
FROM gold.fact_order_reviews
GROUP BY 1
ORDER BY 1;
"""

# CA par région
GEO_SALES_QUERY = """
SELECT g.state_code, g.region_name, g.population,
       ROUND(SUM(o.order_amount)::numeric,2) AS total_sales
FROM gold.fact_orders o
JOIN gold.dim_geography g ON o.customer_id = g.state_code
GROUP BY g.state_code, g.region_name, g.population
ORDER BY total_sales DESC;
"""

# Annulations par région
CANCELLATION_BY_REGION_QUERY = """
SELECT
  g.region_name,
  ROUND(SUM(CASE WHEN o.order_status = 'canceled' THEN 1 ELSE 0 END)::numeric / GREATEST(COUNT(*),1) * 100,2) AS cancellation_rate_pct
FROM gold.fact_orders o
JOIN gold.dim_geography g ON o.customer_id = g.state_code
GROUP BY g.region_name
ORDER BY cancellation_rate_pct DESC;
"""

# Distribution RFM
RFM_DISTRIBUTION_QUERY = """
SELECT
  rfm_label,
  COUNT(*) AS num_customers,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_customers
FROM gold.fact_customer_rfm
GROUP BY rfm_label
ORDER BY num_customers DESC;
"""

# TOP produits
TOP_PRODUCTS_QUERY = """
SELECT p.product_id, c.product_category_name_english AS category,
       ROUND(p.total_revenue::numeric,2) AS total_revenue,
       p.total_units_sold,
       ROUND(p.avg_price::numeric,2) AS avg_price
FROM gold.fact_product_performance p
LEFT JOIN gold.dim_product_categories c ON p.category_id = c.category_id
ORDER BY total_revenue DESC LIMIT 10;
"""

# Moyen paiement répartition
PAYMENTS_TYPE_QUERY = """
SELECT
  payment_type_desc,
  COUNT(*) AS nb_transactions,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM gold.fact_payments
GROUP BY payment_type_desc
ORDER BY nb_transactions DESC;
"""

# Nouveaux clients par mois
NEW_CUSTOMERS_MONTHLY_QUERY = """
SELECT
  TO_CHAR(first_month, 'YYYY-MM') AS first_month,
  COUNT(*) AS nb_new_customers
FROM (
  SELECT MIN(TO_DATE(date_id::text, 'YYYYMMDD')) AS first_month
  FROM gold.fact_orders
  GROUP BY customer_id
) sub
GROUP BY first_month
ORDER BY first_month;
"""











ORDERS_STATUS_MONTHLY_QUERY = """
SELECT
  TO_CHAR(TO_DATE(date_id::text, 'YYYYMMDD'),'YYYY-MM') AS year_month,
  order_status,
  COUNT(DISTINCT order_id) AS num_orders
FROM gold.fact_orders
GROUP BY year_month, order_status
ORDER BY year_month, order_status;
"""