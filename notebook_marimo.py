import marimo

__generated_with = "0.19.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from src.loaders.postgres_loader import PostgresLoader

    return (PostgresLoader,)


@app.cell
def _(PostgresLoader):
    postgresloader = PostgresLoader() 
    engine =postgresloader.engine
    return (engine,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:red; font-size: 35px'> CTE et Windows Functions </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:green; font-size: 25px'> LES CTE(Common Table Expression) </div>
    """)
    return


@app.cell
def _(engine, mo):
    _df = mo.sql(
        f"""
        WITH customer_orders AS (
            SELECT 
            	o.customer_id,
            	COUNT(*) AS nb_orders
            FROM gold.fact_orders o
            GROUP BY o.customer_id
        )
        SELECT 
            c.customer_unique_id,
            c.city,
            co.nb_orders
        FROM gold.dim_customers c 
        JOIN customer_orders co ON c.customer_id = co.customer_id
        ORDER BY co.nb_orders DESC
        """,
        engine=engine
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:green; font-size: 25px'> Windows Functions </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:blue; font-size: 18px'> RANK() </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Classer par order décroissant les produits par chiffre d'affaires dans chaque catégorie
    """)
    return


@app.cell
def _(engine, mo):
    _df = mo.sql(
        f"""
        WITH product_revenue AS (
            SELECT 
                oi.product_id,
                p.category_name,
                SUM(oi.total_price) AS revenue
            FROM
            gold.fact_order_items oi
            JOIN gold.dim_products p ON oi.product_id = p.product_id
            GROUP BY oi.product_id, p.category_name
        )
        SELECT 
            product_id,
            category_name,
            revenue,
            RANK() OVER(PARTITION BY category_name ORDER BY revenue DESC) AS classement
        FROM product_revenue
        """,
        engine=engine
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:blue; font-size: 18px'> DENSE_RANK() </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    -- Classer par order décroissant les produits par chiffre d'affaires dans chaque catégorie
    """)
    return


@app.cell
def _(engine, mo):
    _df = mo.sql(
        f"""
        WITH product_revenue AS (
            SELECT 
                oi.product_id,
                p.category_name,
                SUM(oi.total_price) AS revenue
            FROM
            gold.fact_order_items oi
            JOIN gold.dim_products p ON oi.product_id = p.product_id
            GROUP BY oi.product_id, p.category_name
        )
        SELECT 
            product_id,
            category_name,
            revenue,
            DENSE_RANK() OVER(PARTITION BY category_name ORDER BY revenue DESC) AS classement
        FROM product_revenue
        """,
        engine=engine
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
 
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:blue; font-size: 18px'> LAG() </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Comparer le paiement d'une commande avec la précédente pour un même client
    """)
    return


@app.cell
def _(engine, mo):
    _df = mo.sql(
        f"""
        /*WITH customer_payments AS (
            SELECT
                o.customer_id,
                o.order_id,
                o.order_purchase_timestamp,
                op.payment_value
            FROM silver.orders o
            JOIN silver.payments op ON op.order_id = o.order_id
        )
        SELECT
            customer_id,
            order_id,
            order_purchase_timestamp,
            payment_value,
            LAG(payment_value) OVER (
                PARTITION BY customer_id
                ORDER BY order_purchase_timestamp
            ) AS prev_payment_value
        FROM customer_payments;*/
        """,
        engine=engine
    )
    return


@app.cell
def _(engine, mo):
    df = mo.sql("""
    WITH customer_payments AS (
        SELECT
        	o.customer_id,
        	c.customer_unique_id,
            o.order_id,
            o.order_purchase_timestamp,
            op.payment_value
        FROM silver.orders o
        JOIN silver.payments op ON op.order_id = o.order_id
        JOIN silver.customers c ON o.customer_id = c.customer_id
    ),
    test as (
        SELECT
        customer_unique_id,
        order_id,
        order_purchase_timestamp,
        payment_value,
        LAG(payment_value) OVER (
            PARTITION BY customer_unique_id
            ORDER BY order_purchase_timestamp
        ) AS prev_payment_value
    FROM customer_payments
    )
    select * from test 
    WHERE prev_payment_value is not null;
    """,engine = engine)
    df
    return


@app.cell(hide_code=True)
def _(engine, mo):
    _df = mo.sql(
        f"""
          SELECT order_id, SUM(payment_value) as total_payment_value
            FROM silver.payments
            GROUP BY order_id
        """,
        engine=engine
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:blue; font-size: 18px'> LEAD() </div>
    """)
    return


@app.cell
def _(engine, mo):
    #1-agrègation des paiements par commande
    #2-Jointure avec costumer pour récupérer le vrai id client métier
    #3-application de window function : LEAD avoir l'historique paiment commande 
    #de chaque client par odre de date d'achats
    df2= mo.sql("""
    WITH aggreged_payments AS (
        SELECT 
            order_id, 
            SUM(payment_value) as total_payment_value
        FROM silver.payments
        GROUP BY order_id
    ),
    customer_payments AS (
        SELECT
        	o.customer_id,
        	c.customer_unique_id,
            o.order_id,
            o.order_purchase_timestamp,
            op.total_payment_value
        FROM silver.orders o
        JOIN aggreged_payments op ON op.order_id = o.order_id
        JOIN silver.customers c ON o.customer_id = c.customer_id
    ),
    previous_commande AS (
        SELECT
        customer_unique_id,  
        order_id,
        order_purchase_timestamp,
        total_payment_value,
        LAG(total_payment_value) OVER (
            PARTITION BY customer_unique_id
            ORDER BY order_purchase_timestamp
        ) AS prev_payment_value
    FROM customer_payments
    )
    select * from previous_commande 
    WHERE prev_payment_value is not null;
    """,engine = engine)

    # remplace LAG par LEAD pour récuppérer le montant de la commande suivante dans chaque ligne
    df2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:blue; font-size: 18px'> Sommes cumulées </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Calculer le chiffre d’affaires par jour ensuite calculer le cumul jour après jour
    """)
    return


@app.cell
def _(engine, mo):
    #Calculer le chiffre d’affaires par jour, puis le cumul jour après jour
    df3= mo.sql("""
    WITH daily_revenue AS (
        SELECT
            CAST(DATE_TRUNC('day', o.order_purchase_timestamp) AS DATE) AS order_day,
            SUM(oi.price + oi.freight_value) AS revenue
        FROM silver.orders o
        JOIN silver.order_items oi ON oi.order_id = o.order_id
        GROUP BY 1
    )
    SELECT
        order_day,
        revenue,
        SUM(revenue) OVER (ORDER BY order_day) AS running_total
    FROM daily_revenue;
    """,engine = engine)
    df3
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:green; font-size: 25px'> Exercices </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:blue; font-size: 18px'> 1-Récupérer le classement de chaque client en fonction du montant total de ses paiements (à l'aide de l'expression régulière CTE sur olist_order_payments_dataset, puis en appelant la fonction RANK()).
    </div>
    """)
    return


@app.cell(hide_code=True)
def _(engine, mo):
    _df = mo.sql(
        f"""

        """,
        engine=engine
    )
    return


@app.cell
def _(engine, mo):
    df_exo1 =mo.sql(
        """
        WITH payement_aggregated AS (
            SELECT 
                order_id,
                SUM(payment_value) as total_payment_value
            FROM silver.payments
            GROUP BY order_id
        ),
        orders_payments AS (
            SELECT 
                o.order_id,
                o.customer_id,
                op.total_payment_value
            FROM silver.orders o
            JOIN payement_aggregated op ON o.order_id = op.order_id
        ),
        payments_per_customer AS (
            SELECT 
                c.customer_unique_id as customer,
                SUM(total_payment_value) as total_spent
            FROM silver.customers c
            JOIN orders_payments c2 ON c2.customer_id = c.customer_id
            GROUP BY c.customer_unique_id
        )
        SELECT
            customer,
            total_spent,
            RANK() OVER(ORDER BY total_spent DESC)
        FROM payments_per_customer
        """, engine=engine)
    df_exo1
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:blue; font-size: 18px'>2-Pour chaque commande, afficher le montant du paiement et le montant moyen des commandes du client (à l'aide des fonctions AVG() OVER() sur silver.orders et olist_order_payments_dataset).</div>
    """)
    return


@app.cell
def _(engine, mo):
    df_exo2 =mo.sql(
        """
        WITH payments_aggregated as (
            SELECT
                order_id,
                SUM(payment_value) AS total_payment_value
            FROM silver.payments
            GROUP BY order_id
        ),
        orders_payments AS
        (
            SELECT
                o.order_id,
                o.customer_id,
                p.total_payment_value
            FROM silver.orders o
            JOIN payments_aggregated p ON o.order_id = p.order_id    
        ),
        payments_per_customer AS (
            SELECT 
                op.order_id,
                c.customer_unique_id as customer,
                total_payment_value as amount
            FROM silver.customers c
            JOIN orders_payments op ON op.customer_id = c.customer_id
            )
        SELECT 
            order_id,
            customer,
            amount,
            AVG(amount) OVER(PARTITION BY customer)  AS average_amount
        FROM payments_per_customer
    
        """, engine=engine)
    df_exo2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:blue; font-size: 18px'> 3-Calculer la différence en jours entre deux commandes consécutives d'un même client (à l'aide de la fonction LAG() sur order_purchase_timestamp).</div>
    """)
    return


@app.cell
def _(engine, mo):
    df_exo3 = mo.sql("""
        WITH cte1 AS (
            SELECT
                order_id,
                customer_unique_id as customer,
                CAST(DATE_TRUNC('day', order_purchase_timestamp) AS DATE) purchase_date
            FROM silver.orders o
            JOIN silver.customers c ON o.customer_id = c.customer_id
        ),
        cte2 AS (
            SELECT 
                customer,
                purchase_date,
                order_id,
                LAG(purchase_date) OVER(PARTITION BY customer ORDER BY purchase_date) previous_date,
                purchase_date - (LAG(purchase_date) OVER(PARTITION BY customer ORDER BY purchase_date)) as diff_days
            FROM cte1
        )
        SELECT 
            customer,
            purchase_date,
            order_id,
            previous_date,
            diff_days
        FROM cte2
        ORDER BY diff_days DESC NULLS LAST
    
    """,engine=engine)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:red; font-size: 35px'> Performance et Optimisation </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    supprimer les index déja créer dan sle projet etl
    """)
    return


@app.cell(hide_code=True)
def _(engine, mo):
    _df = mo.sql("""
    DO $$
    DECLARE
        r RECORD;
    BEGIN
        -- Parcours tous les indexes du schéma 'silver' sauf les indexes de clés primaires
        FOR r IN
            SELECT indexname, schemaname
            FROM pg_indexes
            WHERE schemaname = 'silver'
              AND indexname NOT IN (
                  SELECT conname
                  FROM pg_constraint
                  WHERE contype = 'p'
              )
        LOOP
            EXECUTE 'DROP INDEX IF EXISTS ' || quote_ident(r.schemaname) || '.' || quote_ident(r.indexname) || ' CASCADE;';
        END LOOP;
    END $$;
    """, engine = engine)
    _df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:green; font-size: 25px'> Index et structures de données </div>
    """)
    return


@app.cell
def _(engine, mo):
    _df = mo.sql("""
        DROP INDEX IF EXISTS silver.idx_orders_customer;
        DROP INDEX IF EXISTS silver.idx_orders_customer_purchase;
        EXPLAIN
        SELECT *
        FROM silver.orders
        WHERE customer_id = '9ef432eb6251297304e76186b10a928d';
    """, engine = engine)
    _df
    return


@app.cell
def _(engine, mo):
    # 1/ Tree Index
    _df = mo.sql("""
        DROP INDEX IF EXISTS silver.idx_orders_purchase_ts;
        CREATE INDEX idx_orders_purchase_ts
        ON silver.orders(order_purchase_timestamp);

        DROP INDEX IF EXISTS silver.idx_orders_customer_purchase;
        CREATE INDEX idx_orders_customer_purchase
        ON silver.orders(customer_id, order_purchase_timestamp DESC);

        DROP INDEX IF EXISTS silver.idx_orders_customer;
        CREATE INDEX idx_orders_customer
        ON silver.orders(customer_id);
    
        DROP INDEX IF EXISTS silver.idx_order_items_product;
        CREATE INDEX idx_order_items_product
        ON silver.order_items(product_id);

        DROP INDEX IF EXISTS silver.idx_products_category;
        CREATE INDEX idx_products_category
        ON silver.products(product_category_name);
    """,engine= engine)

    return


@app.cell
def _(engine, mo):
    _df = mo.sql("""
        EXPLAIN
        SELECT *
        FROM silver.orders
        WHERE customer_id = '9ef432eb6251297304e76186b10a928d';
    """, engine = engine)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:blue; font-size: 18px'> Exercice</div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Dans une table Olist de commandes volumineuse :**

    - **Ne pas indexer les clés primaires** : les clés primaires comme `order_id` sont **indexées par défaut**.
    - **Indexer les colonnes utilisées dans les jointures et les filtres** : par exemple `customer_id`.
    - **Indexer les colonnes utilisées dans les filtres temporels** : par exemple `order_purchase_timestamp`.
    - **Ne pas indexer les colonnes à faible cardinalité** : par exemple `order_status`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:green; font-size: 25px'>EXPLAIN et EXPLAIN ANALYSZE </div>
    """)
    return


@app.cell
def _(engine, mo):
    #EXPLAIN ANALYZE - Avec timing réel
    #1-ANALYSE AVANT INDEX
    _df = mo.sql("""
    
        DROP INDEX IF EXISTS silver.idx_orders_purchase_ts;
        DROP INDEX IF EXISTS silver.idx_order_items_order;
        DROP INDEX IF EXISTS silver.idx_order_order;

        EXPLAIN ANALYZE
        SELECT
            o.order_id,
            SUM(oi.price + oi.freight_value) AS order_total
        FROM silver.orders o
        JOIN silver.order_items oi ON oi.order_id = o.order_id
        WHERE o.order_purchase_timestamp >= '2018-01-01'
        GROUP BY o.order_id;""",
        engine=engine)
    _df
    return


@app.cell
def _(engine, mo):
    #1-ANALYSE APRS INDEX
    _df = mo.sql("""
        SET enable_seqscan = ON;
        DROP INDEX IF EXISTS silver.idx_order_purchase_year;
        CREATE INDEX idx_order_purchase_year
        ON silver.orders(purchase_year);
    
        DROP INDEX IF EXISTS silver.idx_orders_purchase_ts;
        CREATE INDEX idx_orders_purchase_ts
        ON silver.orders(order_purchase_timestamp);
    
        DROP INDEX IF EXISTS silver.idx_order_items_order;
        CREATE INDEX idx_order_items_order
        ON silver.order_items(order_id);

        --SET enable_seqscan = OFF;
        EXPLAIN ANALYZE
        SELECT
            o.order_id,
            SUM(oi.price + oi.freight_value) AS order_total
        FROM silver.orders o
        JOIN silver.order_items oi ON oi.order_id = o.order_id
        WHERE o.order_purchase_timestamp >= '2018-01-01'
        GROUP BY o.order_id;
        --SET enable_seqscan = ON;
        """,
        engine=engine)
    _df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Problème 1 : scan complet
    """)
    return


@app.cell
def _(engine, mo):
    #1-ANALYSE AVANT INDEX
    _df = mo.sql("""
        EXPLAIN ANALYZE
        SELECT *
        FROM silver.orders
        WHERE purchase_year = 2025;
        """,
        engine=engine)
    _df
    return


@app.cell
def _(engine, mo):
    #1-ANALYSE APRES INDEX
    _df=mo.sql("""

        DROP INDEX IF EXISTS silver.idx_order_purchase_year;
        CREATE INDEX idx_order_purchase_year
        ON silver.orders(purchase_year);

        EXPLAIN ANALYZE
        SELECT *
        FROM silver.orders
        WHERE purchase_year = 2025;
    
        """,
        engine=engine)
    _df
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:green; font-size: 25px'>Bonnes pratiques SQL</div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:green; font-size: 25px'>Performance avancée et monitoring</div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:red; font-size: 35px'> Vues et Transactions </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:green; font-size: 25px'>Vues</div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:green; font-size: 25px'>Transactions acid</div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:red; font-size: 35px'> Projets </div>
    """)
    return


if __name__ == "__main__":
    app.run()
