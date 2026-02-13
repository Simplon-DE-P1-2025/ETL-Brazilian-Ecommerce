import marimo

__generated_with = "0.19.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as _pd
    import matplotlib.pyplot as _plt
    import seaborn as _sns

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
    df1 = mo.sql("""
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
    """,engine = engine)
    df1
    return (df1,)


@app.cell
def _(df1):
    import pandas as _pd
    import matplotlib.pyplot as _plt
    import seaborn as _sns

    _df = df1.to_pandas()
    # Supposons que df1 est déjà chargé comme décrit
    # Agréger par ville
    top_villes = _df.groupby("city")["nb_orders"].sum().sort_values(ascending=False).head(20).reset_index()

    _plt.figure(figsize=(12,8))
    _sns.barplot(data=top_villes, y="city", x="nb_orders", palette="viridis")
    _plt.xlabel("Nombre total de commandes")
    _plt.ylabel("Ville")
    _plt.title("Top 20 villes par nombre total de commandes")
    _plt.tight_layout()
    _plt.show()
    return


@app.cell
def _(df1):
    import matplotlib.pyplot as _plt
    import seaborn as sns

    _df = df1.to_pandas()

    _plt.figure(figsize=(8,5))
    sns.histplot(_df["nb_orders"], bins=30, kde=True, color="skyblue")
    _plt.xlabel("Nombre de commandes par client")
    _plt.ylabel("Nombre de clients")
    _plt.title("Distribution du nombre de commandes par client")
    _plt.tight_layout()
    _plt.show()
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
    df2 = mo.sql("""
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
    """,engine = engine)
    df2
    return (df2,)


@app.cell
def _(df2):
    import matplotlib.pyplot as _plt
    import seaborn as _sns

    _df2 = df2.to_pandas()  # si df2 est polars

    # Calcule le revenue total par catégorie
    total_revenue = _df2.groupby("category_name")["revenue"].sum().reset_index()
    # Trie, garde les 20 meilleurs
    top20 = total_revenue.sort_values("revenue", ascending=False).head(20)

    _plt.figure(figsize=(12,5))
    _sns.barplot(data=top20, x="category_name", y="revenue", palette="tab20")
    _plt.ylabel("Chiffre d'affaires total")
    _plt.xlabel("Catégorie")
    _plt.title("Top 20 catégories par chiffre d'affaires total")
    _plt.xticks(rotation=45, ha="right")
    _plt.tight_layout()
    _plt.show()
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
    df3 = mo.sql("""
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
    """,engine = engine)
    df3
    return (df3,)


@app.cell
def _(df3):
    import matplotlib.pyplot as _plt
    import seaborn as _sns

    _df3 = df3.to_pandas()

    top10 = _df3.sort_values("revenue", ascending=False).head(10)

    _plt.figure(figsize=(14,6))
    _sns.barplot(data=top10, x="product_id", y="revenue", hue="category_name", palette="tab10")
    _plt.xlabel("Produit")
    _plt.ylabel("Chiffre d'affaires")
    _plt.title("Top 10 produits toutes catégories confondues")
    _plt.xticks(rotation=60, ha="right")
    _plt.tight_layout()
    _plt.show()
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
    df4 = mo.sql("""
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
    df4
    return (df4,)


@app.cell
def _(df4):
    import matplotlib.pyplot as _plt
    import seaborn as _sns

    _df4 = df4.to_pandas()

    _plt.figure(figsize=(8,6))
    _sns.scatterplot(data=_df4, x="prev_payment_value", y="payment_value", alpha=0.6)
    _plt.xlabel("Paiement précédent")
    _plt.ylabel("Paiement actuel")
    _plt.title("Relation entre deux paiements successifs par client")
    _plt.tight_layout()
    _plt.show()
    return


@app.cell
def _(df4):
    import matplotlib.pyplot as _plt
    import pandas as _pd

    _df4 = df4.to_pandas()

    # Convertir la colonne en datetime
    _df4["order_purchase_timestamp"] = _pd.to_datetime(_df4["order_purchase_timestamp"])

    # Regrouper par jour (ou par mois selon le volume)
    payments_by_day = _df4.groupby(_df4["order_purchase_timestamp"].dt.date)["payment_value"].sum().reset_index()

    _plt.figure(figsize=(12,5))
    _plt.plot(payments_by_day["order_purchase_timestamp"], payments_by_day["payment_value"], marker='o', color="royalblue")
    _plt.xlabel("Date")
    _plt.ylabel("Total des paiements")
    _plt.title("Total des paiements par jour")
    _plt.xticks(rotation=45)
    _plt.tight_layout()
    _plt.show()
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
    df5= mo.sql("""
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
        ) AS next_payment_value
    FROM customer_payments
    )
    select * from previous_commande 
    WHERE next_payment_value is not null;
    """,engine = engine)

    # remplace LAG par LEAD pour récuppérer le montant de la commande suivante dans chaque ligne
    df5
    return (df5,)


@app.cell
def _(df5):
    import matplotlib.pyplot as _plt
    import pandas as _pd
    import seaborn as _sns

    _df5 = df5.to_pandas()

    _df5["delta"] = _df5["next_payment_value"] - _df5["total_payment_value"]

    _plt.figure(figsize=(8,5))
    _sns.histplot(_df5["delta"], bins=30, color="orange", kde=True)
    _plt.xlabel("Variation du paiement entre deux commandes")
    _plt.ylabel("Nombre de commandes")
    _plt.title("Distribution des écarts de paiement entre commandes")
    _plt.tight_layout()
    _plt.show()
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
    df6= mo.sql("""
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
    df6
    return (df6,)


@app.cell
def _(df6):
    import matplotlib.pyplot as _plt
    import pandas as _pd

    _df6 = df6.to_pandas()

    # Si la colonne order_day n'est pas déjà datetime, convertir
    _df6["order_day"] = _pd.to_datetime(_df6["order_day"])

    _plt.figure(figsize=(14,6))
    _plt.plot(_df6["order_day"], _df6["revenue"], label="Chiffre d'affaires journalier", color="tab:blue", marker="o")
    _plt.plot(_df6["order_day"], _df6["running_total"], label="Chiffre d'affaires cumulé", color="tab:orange", linewidth=2)
    _plt.xlabel("Date")
    _plt.ylabel("Valeur (€)")
    _plt.title("Chiffre d'affaires journalier et cumul (running total)")
    _plt.legend()
    _plt.xticks(rotation=45)
    _plt.tight_layout()
    _plt.show()
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
    <div style='color:blue; font-size: 18px'> 1-Récupérer le classement de chaque client en fonction du montant total de ses paiements (à l'aide de l'expression régulière CTE sur order_payments, puis en appelant la fonction RANK()).
    </div>
    """)
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
    return (df_exo1,)


@app.cell
def _(df_exo1):
    import matplotlib.pyplot as _plt
    import pandas as _pd
    import seaborn as _sns

    _df_exo1 = df_exo1.to_pandas()  # si df_exo1 est polars

    # Prendre les 20 premiers (les top clients)
    _top20 = _df_exo1.sort_values("total_spent", ascending=False).head(20)

    _plt.figure(figsize=(12,5))
    _sns.barplot(data=_top20, x="customer", y="total_spent", palette="viridis")
    _plt.xlabel("Client")
    _plt.ylabel("Total dépensé")
    _plt.title("Top 20 clients par chiffre d'affaires")
    _plt.xticks(rotation=70)
    _plt.tight_layout()
    _plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:blue; font-size: 18px'>2-Pour chaque commande, afficher le montant du paiement et le montant moyen des commandes du client (à l'aide des fonctions AVG() OVER() sur silver.orders et order_payments).</div>
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
    return (df_exo2,)


@app.cell
def _(df_exo2):
    import matplotlib.pyplot as _plt
    import pandas as _pd
    import seaborn as _sns

    _df_exo2 = df_exo2.to_pandas()

    _plt.figure(figsize=(10,5))
    _sns.histplot(_df_exo2["average_amount"], bins=30, color="dodgerblue", kde=True)
    _plt.xlabel("Montant moyen par commande (par client)")
    _plt.ylabel("Nombre de clients/commandes")
    _plt.title("Distribution du montant moyen par commande client")
    _plt.tight_layout()
    _plt.show()
    return


@app.cell
def _(df_exo2):
    import matplotlib.pyplot as _plt
    import pandas as _pd
    import seaborn as _sns

    _df_exo2 = df_exo2.to_pandas()

    _plt.figure(figsize=(8,6))
    _sns.scatterplot(data=_df_exo2, x="average_amount", y="amount", alpha=0.4)
    _plt.xlabel("Montant moyen du client")
    _plt.ylabel("Montant de la commande")
    _plt.title("Montant de la commande vs ticket moyen client")
    _plt.tight_layout()
    _plt.show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:blue; font-size: 18px'> 3-Calculer la différence en jours entre deux commandes consécutives d'un même client (à l'aide de la fonction LAG() sur order_purchase_timestamp).</div>
    """)
    return


@app.cell
def _(engine, mo):
    df_exo3 =mo.sql(
        """
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

        """, engine=engine)
    df_exo3
    return (df_exo3,)


@app.cell
def _(df_exo3):
    import matplotlib.pyplot as _plt
    import pandas as _pd
    import seaborn as _sns

    _df_exo3 = df_exo3.to_pandas()

    # On supprime les NULL (première commande)
    _diff_days_no_null = _df_exo3["diff_days"].dropna()
    # Il se peut que diff_days soit un type timedelta à convertir
    if _diff_days_no_null.dtype == "timedelta64[ns]":
        _diff_days_no_null = _diff_days_no_null.dt.days

    _plt.figure(figsize=(10,5))
    _sns.histplot(_diff_days_no_null, bins=30, color="orchid", kde=True)
    _plt.xlabel("Nb jours entre deux commandes")
    _plt.ylabel("Nombre de commandes")
    _plt.title("Distribution du délai entre deux commandes d'un client")
    _plt.tight_layout()
    _plt.show()
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
        """, engine = engine)
    _df
    return


@app.cell
def _(engine, mo):
    _df = mo.sql("""
        EXPLAIN
        SELECT *
        FROM silver.orders
        WHERE customer_id = '9ef432eb6251297304e76186b10a928d';
        """, engine = engine)
    _df
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

        DROP INDEX IF EXISTS silver.idx_order_order;
        CREATE INDEX idx_order_order
        ON silver.orders(order_id);

        DROP INDEX IF EXISTS silver.idx_orders_purchase_ts;
        CREATE INDEX idx_orders_purchase_ts
        ON silver.orders(order_purchase_timestamp);

        DROP INDEX IF EXISTS silver.idx_order_items_order;
        CREATE INDEX idx_order_items_order
        ON silver.order_items(order_id);

        --SET enable_seqscan = OFF; --forcer l'utilisation d'index pour voir la diff
        EXPLAIN ANALYZE
        SELECT
            o.order_id,
            SUM(oi.price + oi.freight_value) AS order_total
        FROM silver.orders o
        JOIN silver.order_items oi ON oi.order_id = o.order_id
        WHERE o.order_purchase_timestamp >= '2018-01-01'
        GROUP BY o.order_id;
        --SET enable_seqscan = ON; 
        --activer l'utilisation de sequantial scan (car postgreSQL choisi la méthode la plus optimale)
        -- n'utilisé pas le param  enable_seqscan en prod  
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
        DROP INDEX IF EXISTS silver.idx_order_purchase_year;

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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Problème 2 : jointure coûteuse (Nested loop join)
    """)
    return


@app.cell
def _(engine, mo):
    #1-ANALYSE AVANT INDEX
    _df = mo.sql("""

        DROP INDEX IF EXISTS silver.idx_order_order;
        DROP INDEX IF EXISTS silver.idx_order_items_order;
        DROP INDEX IF EXISTS silver.idx_order_items_product;

        EXPLAIN ANALYZE
        SELECT o.order_id, oi.product_id
        FROM silver.orders o
        JOIN silver.order_items oi ON oi.order_id = o.order_id;
        """,
        engine=engine)
    _df
    return


@app.cell
def _(engine, mo):
    #1-ANALYSE APRES INDEX
    _df = mo.sql("""

        DROP INDEX IF EXISTS silver.idx_order_order;
        CREATE INDEX idx_order_order
        ON silver.orders(order_id);

        DROP INDEX IF EXISTS silver.idx_order_items_order;
        CREATE INDEX idx_order_items_order
        ON silver.orders(order_id);

        DROP INDEX IF EXISTS silver.idx_order_items_product;
        CREATE INDEX idx_order_items_product
        ON silver.order_items(product_id);

        EXPLAIN ANALYZE
        SELECT o.order_id, oi.product_id
        FROM silver.orders o
        JOIN silver.order_items oi ON oi.order_id = o.order_id;
        """,
        engine=engine)
    _df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Problème 3 : Problème 3 : tri coûteux (Sort sans index)
    """)
    return


@app.cell
def _(engine, mo):
    #1-ANALYSE AVANT INDEX
    _df = mo.sql("""

        DROP INDEX IF EXISTS silver.idx_order_order;
        DROP INDEX IF EXISTS silver.idx_orders_purchase_ts;

        EXPLAIN ANALYZE
        SELECT order_id, order_purchase_timestamp
        FROM silver.orders
        ORDER BY order_purchase_timestamp DESC;
        """,
        engine=engine)
    _df
    return


@app.cell
def _(engine, mo):
    #1-ANALYSE APRES INDEX
    _df = mo.sql("""

        DROP INDEX IF EXISTS silver.idx_order_order;
        CREATE INDEX idx_order_order
        ON silver.orders(order_id);

        DROP INDEX IF EXISTS silver.idx_orders_purchase_ts;
        CREATE INDEX idx_orders_purchase_ts
        ON silver.orders(order_purchase_timestamp);

        EXPLAIN ANALYZE
        SELECT order_id, order_purchase_timestamp
        FROM silver.orders
        ORDER BY order_purchase_timestamp DESC;
        """,
        engine=engine)
    _df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div style='color:blue; font-size: 18px'> Exercice</div>
    """)
    return


@app.cell
def _(engine, mo):
    #1--- Requête 1
    _df = mo.sql("""

        EXPLAIN ANALYZE
        SELECT *
        FROM silver.orders
        WHERE order_status = 'delivered';
        """,
        engine=engine)
    _df
    return


@app.cell
def _(engine, mo):
    #1--- Requête 2
    _df = mo.sql("""

        EXPLAIN ANALYZE
        SELECT order_id, customer_id
        FROM silver.orders
        WHERE order_status = 'delivered';
        """,
        engine=engine)
    _df
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Conclusion :La requête 2 est plus rapide que La requête 1
    """)
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
    <div style='color:blue; font-size: 18px'> Exercice</div>
    """)
    return


@app.cell
def _(engine, mo):
    # -- Requête avant optimisation
    _df = mo.sql(
        """
        SELECT *
        FROM silver.orders
        WHERE UPPER(order_status) = 'DELIVERED'
        ORDER BY order_purchase_timestamp DESC;
        """,
        engine=engine,
    )
    _df
    return


@app.cell
def _(engine, mo):
    # -- Requête avant optimisation
    _df = mo.sql(
        """
        EXPLAIN ANALYZE
        SELECT *
        FROM silver.orders
        WHERE UPPER(order_status) = 'DELIVERED'
        ORDER BY order_purchase_timestamp DESC;
        """,
        engine=engine,
    )
    _df
    return


@app.cell
def _(engine, mo):
    # -- Requête après optimisation
    _df = mo.sql(
        """
        SELECT
                order_id,
                customer_id,
                order_status,
                order_purchase_timestamp
        FROM silver.orders
        WHERE order_status = 'delivered'
        ORDER BY order_purchase_timestamp DESC
        LIMIT 10;
        """,
        engine=engine,
    )
    _df
    return


@app.cell
def _(engine, mo):
    # -- Requête après optimisation
    _df = mo.sql(
        """
        EXPLAIN ANALYZE
        SELECT
                order_id,
                customer_id,
                order_status,
                order_purchase_timestamp
        FROM silver.orders
        WHERE order_status = 'delivered'
        ORDER BY order_purchase_timestamp DESC
        LIMIT 10;
        """,
        engine=engine,
    )
    _df
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
    <div style='color:blue; font-size: 18px'> Exercice final</div>
    """)
    return


@app.cell
def _(engine, mo):
    # -- Requête avant optimisation
    _df = mo.sql(
        """
        DROP INDEX IF EXISTS silver.idx_products_category;
        DROP INDEX IF EXISTS silver.idx_order_items_product_price;


        EXPLAIN ANALYZE
        SELECT *
        FROM silver.order_items oi
        WHERE oi.product_id IN (
            SELECT p.product_id
            FROM silver.products p
            WHERE UPPER(p.product_category_name) = 'CAMA_MESA_BANHO'
        )
        ORDER BY oi.price DESC;
        """,
        engine=engine,
    )
    _df
    return


@app.cell
def _(engine, mo):
    # -- Requête après optimisation
    _df = mo.sql(
        """

        DROP INDEX IF EXISTS silver.idx_products_category;
        CREATE INDEX idx_products_category
        ON silver.products(product_category_name);

        CREATE INDEX idx_order_items_product_price
        ON silver.order_items(product_id, price DESC);

        EXPLAIN ANALYZE
        WITH target_products AS (
            SELECT product_id
            FROM silver.products
            WHERE product_category_name = 'cama_mesa_banho'
        )
        SELECT oi.order_id, oi.product_id, oi.price, oi.freight_value
        FROM silver.order_items oi
        JOIN target_products tp ON tp.product_id = oi.product_id
        ORDER BY oi.price DESC
        LIMIT 100;
        """,
        engine=engine,
    )
    _df
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
    <div style='color:red; font-size: 35px'> Projets </div>
    """)
    return


@app.cell
def _(engine, mo):
    # -- Requête après optimisation
    _df = mo.sql(
        """
        SELECT TO_CHAR(TO_DATE(date_id::text, 'YYYYMMDD'), 'YYYY-MM') AS year_month,
               SUM(order_amount) AS total_sales,
               COUNT(DISTINCT order_id) AS num_orders,
               ROUND(
        (SUM(order_amount)::numeric / GREATEST(COUNT(DISTINCT order_id), 1)),2) AS avg_order_value 
        FROM gold.fact_orders
        GROUP BY 1
        ORDER BY 1;
        """,
        engine=engine,
    )
    _df
    return


if __name__ == "__main__":
    app.run()
