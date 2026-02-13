# Optimized KPI SQL queries using gold tables

SALES_DAILY_GOLD_QUERY = '''
SELECT d.date, d.year_month, SUM(o.order_amount) AS total_sales, COUNT(DISTINCT o.order_id) AS total_orders
FROM gold.fact_orders o
JOIN gold.dim_date d ON o.date_id = d.date_id
WHERE o.order_status = 'delivered'
GROUP BY d.date, d.year_month
ORDER BY d.date;
'''

SALES_MONTHLY_GOLD_QUERY = '''
SELECT d.year_month, SUM(o.order_amount) AS total_sales, COUNT(DISTINCT o.order_id) AS total_orders
FROM gold.fact_orders o
JOIN gold.dim_date d ON o.date_id = d.date_id
WHERE o.order_status = 'delivered'
GROUP BY d.year_month
ORDER BY d.year_month;
'''

SALES_YEARLY_GOLD_QUERY = '''
SELECT d.year, SUM(o.order_amount) AS total_sales, COUNT(DISTINCT o.order_id) AS total_orders
FROM gold.fact_orders o
JOIN gold.dim_date d ON o.date_id = d.date_id
WHERE o.order_status = 'delivered'
GROUP BY d.year
ORDER BY d.year;
'''

SALES_YOY_GOLD_QUERY = '''
SELECT d.year_month,
       SUM(o.order_amount) AS total_sales,
       LAG(SUM(o.order_amount)) OVER (ORDER BY d.year_month) AS sales_last_year,
       (SUM(o.order_amount) - LAG(SUM(o.order_amount)) OVER (ORDER BY d.year_month)) / NULLIF(LAG(SUM(o.order_amount)) OVER (ORDER BY d.year_month),0) AS yoy_growth
FROM gold.fact_orders o
JOIN gold.dim_date d ON o.date_id = d.date_id
WHERE o.order_status = 'delivered'
GROUP BY d.year_month
ORDER BY d.year_month;
'''

TOP_PRODUCTS_GOLD_QUERY = '''
SELECT p.product_id, p.category_name, SUM(oi.total_price) AS total_sales, COUNT(oi.order_id) AS total_orders
FROM gold.fact_order_items oi
JOIN gold.dim_products p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.category_name
ORDER BY total_sales DESC
LIMIT 10;
'''

NEW_RETURNING_CUSTOMERS_GOLD_QUERY = '''
SELECT d.year_month,
       COUNT(DISTINCT CASE WHEN c.total_orders = 1 THEN c.customer_unique_id END) AS new_customers,
       COUNT(DISTINCT CASE WHEN c.total_orders > 1 THEN c.customer_unique_id END) AS returning_customers
FROM gold.fact_customer_lifetime c
JOIN gold.dim_date d ON d.year_month IS NOT NULL
GROUP BY d.year_month
ORDER BY d.year_month;
'''

AVG_BASKET_GOLD_QUERY = '''
SELECT d.year_month, AVG(o.order_amount) AS avg_basket_value
FROM gold.fact_orders o
JOIN gold.dim_date d ON o.date_id = d.date_id
WHERE o.order_status = 'delivered'
GROUP BY d.year_month
ORDER BY d.year_month;
'''

CONVERSION_RATE_GOLD_QUERY = '''
SELECT d.year_month,
       COUNT(DISTINCT o.order_id) AS total_orders,
       COUNT(DISTINCT o.customer_id) AS total_customers,
       COUNT(DISTINCT o.order_id)::float / NULLIF(COUNT(DISTINCT o.customer_id),0) AS conversion_rate
FROM gold.fact_orders o
JOIN gold.dim_date d ON o.date_id = d.date_id
WHERE o.order_status = 'delivered'
GROUP BY d.year_month
ORDER BY d.year_month;
'''

RFM_SEGMENTATION_GOLD_QUERY = '''
SELECT r.rfm_segment, COUNT(DISTINCT r.customer_unique_id) AS customer_count, AVG(r.monetary) AS avg_monetary
FROM gold.fact_customer_rfm r
GROUP BY r.rfm_segment
ORDER BY customer_count DESC;
'''

COHORT_RETENTION_GOLD_QUERY = '''
SELECT d.year_month AS cohort_month,
       COUNT(DISTINCT o.customer_id) AS cohort_size,
       SUM(CASE WHEN o.order_status = 'delivered' THEN 1 ELSE 0 END) AS delivered_orders
FROM gold.fact_orders o
JOIN gold.dim_date d ON o.date_id = d.date_id
GROUP BY d.year_month
ORDER BY d.year_month;
'''

COHORT_LTV_GOLD_QUERY = '''
SELECT d.year_month AS cohort_month,
       AVG(c.lifetime_value) AS avg_ltv
FROM gold.fact_customer_lifetime c
JOIN gold.dim_date d ON d.year_month IS NOT NULL
GROUP BY d.year_month
ORDER BY d.year_month;
'''

GEO_STATE_METRICS_QUERY = """
SELECT
  c.state AS customer_state_short,
  g.region_name,
  g.population,
  COUNT(DISTINCT o.order_id) AS total_orders,
  ROUND(SUM(o.order_amount)::numeric, 2) AS total_payment,
  ROUND((SUM(o.order_amount) / GREATEST(g.population, 1))::numeric, 2) AS total_payment_per_thousand_person,
  ROUND((COUNT(DISTINCT o.order_id) / GREATEST(g.population, 1))::numeric, 2) AS orders_per_thousand_person,
  ROUND(AVG(r.review_score)::numeric, 2) AS avg_review_score,
  COUNT(r.review_id) AS total_reviews,
  ROUND(AVG(o.delivery_days)::numeric, 2) AS avg_delivery_delay_days,
  ROUND(AVG(o.order_amount)::numeric, 2) AS aov,
  ROUND(AVG(p.payment_installments)::numeric, 2) AS avg_installments,
  ROUND(AVG(oi.total_price)::numeric, 2) AS avg_products_cnt,
  ROUND(SUM(CASE WHEN o.order_status = 'canceled' THEN 1 ELSE 0 END)::numeric / GREATEST(COUNT(*),1) * 100,2) AS cancel_rate,
  ROUND(SUM(CASE WHEN p.payment_installments > 1 THEN 1 ELSE 0 END)::numeric / GREATEST(COUNT(*),1) * 100,2) AS installment_orders_rate
FROM gold.fact_orders o
LEFT JOIN gold.dim_customers c ON o.customer_id = c.customer_id
LEFT JOIN gold.dim_geography g ON c.state = g.state_code
LEFT JOIN gold.fact_order_reviews r ON o.order_id = r.order_id
LEFT JOIN gold.fact_payments p ON o.order_id = p.order_id
LEFT JOIN gold.fact_order_items oi ON o.order_id = oi.order_id
GROUP BY c.state, g.region_name, g.population
ORDER BY total_payment DESC;
"""

RETENTION_STATE_QUERY = """
SELECT
  c.state AS customer_state_short,
  ROUND(SUM(CASE WHEN o.order_status = 'delivered' THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2) AS retention_1st_month_state
FROM gold.fact_orders o
LEFT JOIN gold.dim_customers c ON o.customer_id = c.customer_id
GROUP BY c.state
ORDER BY retention_1st_month_state DESC;
"""

STATE_PAYMENT_EVOLUTION_QUERY = """
SELECT
  d.year_month,
  c.state AS customer_state_short,
  SUM(o.order_amount) AS total_payment
FROM gold.fact_orders o
LEFT JOIN gold.dim_customers c ON o.customer_id = c.customer_id
LEFT JOIN gold.dim_date d ON o.date_id = d.date_id
GROUP BY d.year_month, c.state
ORDER BY d.year_month, c.state;
"""