
import pandas as pd
import numpy as np
from typing import Dict
import logging
from config.settings import CATEGORY_MAPPING

logger = logging.getLogger(__name__)


def _get_general_category(category_name: str) -> str:
    """
    Nom        : _get_general_category
    Input      : category_name (str) - nom de la catégorie en anglais
    Output     : str - groupe général (electronics, fashion, etc.)
    Description: Mappe une catégorie détaillée vers son groupe général
                 pour simplifier les analyses
    """
    if pd.isna(category_name) or category_name == '':
        return 'other'
    category_name = str(category_name).lower().strip()
    for general, categories in CATEGORY_MAPPING.items():
        if category_name in categories:
            return general
    return 'other'


class GoldAggregator:
    """
    Agrégations métier pour le Gold Layer avec architecture Star Schema.
    
    Crée les dimensions (tables de référence) et les faits (tables de métriques)
    à partir des données Silver nettoyées.
    """

    def __init__(self, silver_data: Dict[str, pd.DataFrame]):
        self.silver = silver_data
        self.gold = {}

    def aggregate(self) -> Dict[str, pd.DataFrame]:
        """
        Point d'entrée principal pour créer toutes les tables Gold.
        Crée les dimensions AVANT les faits pour garantir les FK.
        """
        # === DIMENSIONS (Tables de référence - attributs descriptifs) ===
        self._create_dim_date()
        self._create_dim_product_categories()
        self._create_dim_customers()
        self._create_dim_products()
        self._create_dim_sellers()
        self._create_dim_geography()
        
        # === FAITS (Tables de métriques - mesures quantitatives) ===
        self._create_fact_order_items()
        self._create_fact_orders()
        self._create_fact_payments()
        self._create_fact_daily_sales()
        self._create_fact_customer_lifetime()
        self._create_fact_customer_rfm()
        self._create_fact_product_performance()
        self._create_fact_category_performance()
        self._create_fact_reviews()
        
        return self.gold

    # =========================================================================
    # DIMENSIONS
    # =========================================================================
    
    def _create_dim_date(self):
        """
        Dimension calendrier avec toutes les dates entre min/max des commandes.
        Format date_id: YYYYMMDD (int) pour jointures optimisées.
        """
        if 'orders' not in self.silver:
            logger.warning("Table 'orders' manquante dans Silver - dim_date non créée")
            return
        
        orders = self.silver['orders']
        
        # Trouver la plage de dates
        min_date = orders['order_purchase_timestamp'].min()
        max_date = orders['order_purchase_timestamp'].max()
        
        if pd.isna(min_date) or pd.isna(max_date):
            logger.warning("Dates invalides dans orders - dim_date non créée")
            return
        
        # Générer toutes les dates de la plage
        date_range = pd.date_range(start=min_date.date(), end=max_date.date(), freq='D')
        
        dim_date = pd.DataFrame({'date': date_range})
        
        # Clé primaire: YYYYMMDD
        dim_date['date_id'] = dim_date['date'].dt.strftime('%Y%m%d').astype(int)
        
        # Attributs temporels
        dim_date['year'] = dim_date['date'].dt.year
        dim_date['quarter'] = dim_date['date'].dt.quarter
        dim_date['month'] = dim_date['date'].dt.month
        dim_date['month_name'] = dim_date['date'].dt.month_name()
        dim_date['week'] = dim_date['date'].dt.isocalendar().week.astype(int)
        dim_date['day'] = dim_date['date'].dt.day
        dim_date['day_name'] = dim_date['date'].dt.day_name()
        dim_date['day_of_week'] = dim_date['date'].dt.dayofweek  # 0=Monday
        dim_date['day_of_year'] = dim_date['date'].dt.dayofyear
        dim_date['is_weekend'] = dim_date['day_of_week'].isin([5, 6])
        dim_date['is_month_start'] = dim_date['date'].dt.is_month_start
        dim_date['is_month_end'] = dim_date['date'].dt.is_month_end
        dim_date['year_month'] = dim_date['date'].dt.strftime('%Y-%m')
        dim_date['year_quarter'] = dim_date['year'].astype(str) + '-Q' + dim_date['quarter'].astype(str)
        
        # Convertir date en string pour stockage
        dim_date['date'] = dim_date['date'].dt.date
        
        self.gold['dim_date'] = dim_date
        logger.info(f"dim_date créée: {len(dim_date)} lignes")

    def _create_dim_product_categories(self):
        """
        Dimension catégories produits depuis category_translation Silver.
        Ajoute un category_id auto-incrémenté et le groupe général.
        """
        if 'category_translation' not in self.silver:
            logger.warning("Table 'category_translation' manquante - dim_product_categories non créée")
            return
        
        categories = self.silver['category_translation'].copy()
        
        # Créer category_id auto-incrémenté (PK)
        categories = categories.reset_index(drop=True)
        categories['category_id'] = categories.index + 1
        
        # Assurer les colonnes requises
        if 'product_category_name' not in categories.columns:
            logger.warning("Colonne 'product_category_name' manquante")
            return
        
        # Colonne anglaise si absente
        if 'product_category_name_english' not in categories.columns:
            categories['product_category_name_english'] = categories['product_category_name']
        
        # Mapper vers groupe général
        categories['general_category'] = categories['product_category_name_english'].apply(_get_general_category)
        
        # Sélectionner et ordonner les colonnes
        dim_categories = categories[[
            'category_id',
            'product_category_name',
            'product_category_name_english', 
            'general_category'
        ]].copy()
        
        self.gold['dim_product_categories'] = dim_categories
        logger.info(f"dim_product_categories créée: {len(dim_categories)} lignes")

    def _create_dim_customers(self):
        """
        Dimension clients (attributs descriptifs SANS métriques de ventes).
        """
        if 'customers' not in self.silver:
            logger.warning("Table 'customers' manquante - dim_customers non créée")
            return
        
        customers = self.silver['customers'].copy()
        
        # Colonnes à garder (attributs descriptifs uniquement)
        cols_to_keep = ['customer_id', 'customer_unique_id']
        
        # Ajouter colonnes optionnelles si présentes
        optional_cols = {
            'customer_zip_code_prefix': 'zip_code',
            'customer_city': 'city',
            'customer_state': 'state',
            'customer_region': 'region',
            'population': 'population'
        }
        
        for old_col, new_col in optional_cols.items():
            if old_col in customers.columns:
                cols_to_keep.append(old_col)
        
        dim_customers = customers[cols_to_keep].copy()
        
        # Renommer les colonnes
        rename_map = {k: v for k, v in optional_cols.items() if k in dim_customers.columns}
        dim_customers = dim_customers.rename(columns=rename_map)
        
        self.gold['dim_customers'] = dim_customers
        logger.info(f"dim_customers créée: {len(dim_customers)} lignes")

    def _create_dim_products(self):
        """
        Dimension produits (attributs descriptifs SANS métriques de ventes).
        Inclut category_id comme FK vers dim_product_categories.
        """
        if 'products' not in self.silver:
            logger.warning("Table 'products' manquante - dim_products non créée")
            return
        
        products = self.silver['products'].copy()
        
        # Joindre avec categories pour obtenir category_id
        if 'dim_product_categories' in self.gold:
            categories = self.gold['dim_product_categories'][['category_id', 'product_category_name']]
            products = products.merge(categories, on='product_category_name', how='left')
            # Catégories inconnues → category_id = -1
            products['category_id'] = products['category_id'].fillna(-1).astype(int)
        else:
            products['category_id'] = -1
        
        # Colonnes à garder
        cols_mapping = {
            'product_id': 'product_id',
            'category_id': 'category_id',
            'product_category_name': 'category_name',
            'product_weight_g': 'weight_g',
            'product_length_cm': 'length_cm',
            'product_height_cm': 'height_cm',
            'product_width_cm': 'width_cm',
            'product_volume_cm3': 'volume_cm3',
            'product_photos_qty': 'photos_qty'
        }
        
        existing_cols = [c for c in cols_mapping.keys() if c in products.columns]
        dim_products = products[existing_cols].copy()
        dim_products = dim_products.rename(columns={k: v for k, v in cols_mapping.items() if k in existing_cols})
        
        self.gold['dim_products'] = dim_products
        logger.info(f"dim_products créée: {len(dim_products)} lignes")

    def _create_dim_sellers(self):
        """
        Dimension vendeurs (attributs descriptifs uniquement).
        """
        if 'sellers' not in self.silver:
            logger.warning("Table 'sellers' manquante - dim_sellers non créée")
            return
        
        sellers = self.silver['sellers'].copy()
        
        cols_mapping = {
            'seller_id': 'seller_id',
            'seller_zip_code_prefix': 'zip_code',
            'seller_city': 'city',
            'seller_state': 'state',
            'seller_region': 'region'
        }
        
        existing_cols = [c for c in cols_mapping.keys() if c in sellers.columns]
        dim_sellers = sellers[existing_cols].copy()
        dim_sellers = dim_sellers.rename(columns={k: v for k, v in cols_mapping.items() if k in existing_cols})
        
        self.gold['dim_sellers'] = dim_sellers
        logger.info(f"dim_sellers créée: {len(dim_sellers)} lignes")

    def _create_dim_geography(self):
        """
        Dimension géographique avec états et régions du Brésil.
        """
        from config.settings import STATES, REGION_MAPPING, POPULATION
        
        geo_data = []
        for state in STATES:
            geo_data.append({
                'state_code': state,
                'region_name': REGION_MAPPING.get(state, 'Unknown'),
                'population': POPULATION.get(state, 0)
            })
        
        dim_geography = pd.DataFrame(geo_data)
        
        self.gold['dim_geography'] = dim_geography
        logger.info(f"dim_geography créée: {len(dim_geography)} lignes")
    
    


    # =========================================================================
    # FAITS
    # =========================================================================
    
    def _create_fact_order_items(self):
        """
        Table de faits au niveau article (granularité la plus fine).
        1 ligne = 1 article dans 1 commande.
        """
        required_tables = ['order_items', 'orders']
        for table in required_tables:
            if table not in self.silver:
                logger.warning(f"Table '{table}' manquante - fact_order_items non créée")
                return
        
        order_items = self.silver['order_items'].copy()
        orders = self.silver['orders'][['order_id', 'customer_id', 'order_purchase_timestamp']].copy()
        
        # Joindre avec orders pour customer_id et date
        fact = order_items.merge(orders, on='order_id', how='left')
        
        # Filtrer les lignes sans date valide
        fact = fact[fact['order_purchase_timestamp'].notna()].copy()
        
        # Créer date_id (format YYYYMMDD)
        fact['date_id'] = pd.to_datetime(fact['order_purchase_timestamp']).dt.strftime('%Y%m%d').astype(int)
        
        # Sélectionner colonnes finales
        cols_fact = ['order_id', 'order_item_id', 'product_id', 'seller_id', 
                     'customer_id', 'date_id', 'price', 'freight_value', 'total_price']
        
        existing_cols = [c for c in cols_fact if c in fact.columns]
        fact_order_items = fact[existing_cols].copy()
        
        self.gold['fact_order_items'] = fact_order_items
        logger.info(f"fact_order_items créée: {len(fact_order_items)} lignes")

    def _create_fact_orders(self):
        """
        Table de faits au niveau commande (1 ligne = 1 commande).
        Agrège les articles et paiements.
        """
        if 'orders' not in self.silver:
            logger.warning("Table 'orders' manquante - fact_orders non créée")
            return
        
        orders = self.silver['orders'].copy()
        
        # Filtrer les commandes sans date valide
        orders = orders[orders['order_purchase_timestamp'].notna()].copy()
        
        # Créer date_id (format YYYYMMDD)
        orders['date_id'] = pd.to_datetime(orders['order_purchase_timestamp']).dt.strftime('%Y%m%d').astype(int)
        
        # Agrégation des items si disponible
        if 'order_items' in self.silver:
            items_agg = self.silver['order_items'].groupby('order_id', as_index=False).agg({
                'order_item_id': 'count',
                'price': 'sum',
                'freight_value': 'sum',
                'total_price': 'sum'
            })
            items_agg.columns = ['order_id', 'total_items', 'items_amount', 'freight_amount', 'order_amount']
            orders = orders.merge(items_agg, on='order_id', how='left')
        else:
            orders['total_items'] = 0
            orders['order_amount'] = 0
        
        # Agrégation des paiements si disponible
        if 'payments' in self.silver:
            payments_agg = self.silver['payments'].groupby('order_id', as_index=False).agg({
                'payment_value': 'sum'
            })
            payments_agg.columns = ['order_id', 'payment_amount']
            orders = orders.merge(payments_agg, on='order_id', how='left')
        else:
            orders['payment_amount'] = orders.get('order_amount', 0)
        
        # Colonnes finales
        cols_fact = ['order_id', 'customer_id', 'date_id', 'order_status',
                     'total_items', 'order_amount', 'payment_amount', 
                     'delivery_days', 'is_late']
        
        existing_cols = [c for c in cols_fact if c in orders.columns]
        fact_orders = orders[existing_cols].copy()
        
        # Remplir valeurs manquantes
        for col in ['total_items', 'order_amount', 'payment_amount', 'delivery_days']:
            if col in fact_orders.columns:
                fact_orders[col] = fact_orders[col].fillna(0)
        
        if 'is_late' in fact_orders.columns:
            fact_orders['is_late'] = fact_orders['is_late'].fillna(False)
        
        self.gold['fact_orders'] = fact_orders
        logger.info(f"fact_orders créée: {len(fact_orders)} lignes")
    
    
    
    def _create_fact_payments(self):
        """
        Table de faits des paiements (1 ligne = 1 paiement).
        """
        if 'payments' not in self.silver:
            logger.warning("Table 'payments' manquante - fact_payments non créée")
            return
        
        
        payments = self.silver['payments'].copy()
        
        # Ajout descriptions business
        payment_type_desc = {
            'credit_card': "Carte de crédit",
            'voucher': "Coupon ou chèque-cadeau",
            'boleto': "Boleto (facture à payer en banque)",
            'debit_card': "Carte de débit",
            'not_defined': "Inconnu"
        }

        payments['payment_type_desc'] = payments['payment_type'].map(payment_type_desc).fillna("Autre")
        
        # Regroupement pour voir toutes les options de versements par type
        # => "installments_mode" : 'single', 'multiple', 'variable'
        def installments_mode(inst):
            if inst == 1:
                return 'single'
            elif inst > 1:
                return 'multiple'
            else:
                return 'variable'
        payments['installments_mode'] = payments['payment_installments'].apply(installments_mode)

        
        cols_mapping = {
            'order_id': 'order_id',
            'payment_type': 'payment_type',
            'payment_type_desc': 'payment_type_desc',
            'has_installments': 'has_installments',
            'payment_installments': 'payment_installments',
            'installments_mode': 'installments_mode',
            'payment_sequential': 'payment_sequential',
            'payment_value': 'payment_value'
        }
        
        existing_cols = [c for c in cols_mapping.keys() if c in payments.columns]
        payments = payments[existing_cols].copy()
        fact_payments = payments.rename(columns={k: v for k, v in cols_mapping.items() if k in existing_cols})
        

        self.gold['fact_payments'] = fact_payments
        logger.info(f"fact_payments créée: {len(fact_payments)} lignes")
   
        
    def _create_fact_reviews(self):
        """
        Table de faits des avis clients (reviews) enrichie : 
        - note, longueur, délai de réponse, type de jour, saison...
        - jointure avec orders pour date_id
        """
        required_tables = ['reviews', 'orders']
        for table in required_tables:
            if table not in self.silver:
                logger.warning(f"Table '{table}' manquante - fact_order_reviews non créée")
                return

        reviews = self.silver['reviews'].copy()
        orders = self.silver['orders'][['order_id', 'order_purchase_timestamp']]

        # Jointure orders pour date_id
        reviews = reviews.merge(orders, on='order_id', how='left')
        reviews = reviews[reviews['order_purchase_timestamp'].notna()].copy()
        reviews['date_id'] = pd.to_datetime(reviews['order_purchase_timestamp']).dt.strftime('%Y%m%d').astype(int)

        # Colonnes finales utiles (adapte selon tes dashboards/analyses)
        cols = [
            'review_id', 'order_id', 'review_score',
            'review_creation_date', 'review_answer_timestamp', 'date_id',
            'review_comment_length',        # longueur texte
            'response_delay_days',          # délai de réponse en jours
            'review_weekday', 'review_weekday_name',
            'review_day_type',
            'review_season'
        ]
        # Garder celles qui existent dans reviews
        cols = [c for c in cols if c in reviews.columns]
        fact_order_reviews = reviews[cols].copy()

        self.gold['fact_order_reviews'] = fact_order_reviews
        logger.info(f"fact_order_reviews créée: {len(fact_order_reviews)} lignes")
    
    def _create_fact_daily_sales(self):
        """
        Table de faits agrégée par jour.
        """
        if 'fact_orders' not in self.gold:
            logger.warning("fact_orders manquante - fact_daily_sales non créée")
            return
        
        orders = self.gold['fact_orders'].copy()
        
        # Agrégation par date_id
        daily = orders.groupby('date_id', as_index=False).agg({
            'order_id': 'count',
            'customer_id': 'nunique',
            'order_amount': 'sum',
            'delivery_days': 'mean'
        })
        
        daily.columns = ['date_id', 'total_orders', 'unique_customers', 'total_revenue', 'avg_delivery_days']
        
        # Arrondir les moyennes
        daily['avg_delivery_days'] = daily['avg_delivery_days'].round(2)
        daily['total_revenue'] = daily['total_revenue'].round(2)
        
        self.gold['fact_daily_sales'] = daily
        logger.info(f"fact_daily_sales créée: {len(daily)} lignes")

    def _create_fact_customer_lifetime(self):
        """
        Métriques lifetime par client avec segmentation RFM.
        1 ligne = 1 customer_unique_id.
        """
        required = ['customers', 'orders']
        for table in required:
            if table not in self.silver:
                logger.warning(f"Table '{table}' manquante - fact_customer_lifetime non créée")
                return
        
        customers = self.silver['customers'].copy()
        orders = self.silver['orders'].copy()
        
        # Préparer orders avec montants
        if 'order_items' in self.silver:
            items_agg = self.silver['order_items'].groupby('order_id', as_index=False)['total_price'].sum()
            items_agg.columns = ['order_id', 'order_value']
            orders = orders.merge(items_agg, on='order_id', how='left')
        else:
            orders['order_value'] = 0
        
        orders['order_value'] = orders['order_value'].fillna(0)
        
        # Joindre pour avoir customer_unique_id
        orders = orders.merge(
            customers[['customer_id', 'customer_unique_id']], 
            on='customer_id', 
            how='left'
        )
        
        # Pré-calculer les commandes annulées
        orders['is_canceled'] = (orders['order_status'] == 'canceled').astype(int)
        
        # Agrégation par customer_unique_id (sans lambda)
        customer_metrics = orders.groupby('customer_unique_id', as_index=False).agg({
            'order_id': 'count',
            'order_value': 'sum',
            'is_canceled': 'sum',
            'order_purchase_timestamp': ['min', 'max']
        })
        
        # Aplatir les colonnes multi-index
        customer_metrics.columns = [
            'customer_unique_id', 'total_orders', 'lifetime_value', 
            'canceled_orders', 'first_order_date', 'last_order_date'
        ]
        
        # Calculer métriques dérivées
        customer_metrics['avg_order_value'] = (
            customer_metrics['lifetime_value'] / customer_metrics['total_orders']
        ).round(2)
        
        customer_metrics['cancellation_rate'] = (
            customer_metrics['canceled_orders'] / customer_metrics['total_orders']
        ).round(4)
        
        # Segmentation RFM simplifiée
        reference_date = orders['order_purchase_timestamp'].max()
        customer_metrics['recency_days'] = (
            reference_date - customer_metrics['last_order_date']
        ).dt.days
        
        # Segmentation vectorisée (évite apply lent)
        customer_metrics['customer_segment'] = self._calculate_rfm_segments_vectorized(customer_metrics)
        
        # Ajouter state et region depuis customers (merge plus rapide que groupby+map)
        customer_geo = customers[['customer_unique_id', 'customer_state', 'customer_region']].drop_duplicates(
            subset=['customer_unique_id'], keep='first'
        )
        customer_metrics = customer_metrics.merge(
            customer_geo, on='customer_unique_id', how='left'
        )
        customer_metrics = customer_metrics.rename(columns={
            'customer_state': 'state',
            'customer_region': 'region'
        })
        
        # Sélectionner colonnes finales
        cols_final = [
            'customer_unique_id', 'total_orders', 'lifetime_value', 
            'avg_order_value', 'cancellation_rate', 'customer_segment',
            'state', 'region'
        ]
        cols_final = [c for c in cols_final if c in customer_metrics.columns]
        
        fact_lifetime = customer_metrics[cols_final].copy()
        
        self.gold['fact_customer_lifetime'] = fact_lifetime
        logger.info(f"fact_customer_lifetime créée: {len(fact_lifetime)} lignes")

    def _calculate_rfm_segments_vectorized(self, df) -> pd.Series:
        """Segmentation RFM vectorisée (rapide)"""
        import numpy as np
        
        recency = df['recency_days']
        frequency = df['total_orders']
        
        segments = np.select(
            [
                (recency <= 30) & (frequency >= 3),  # Champions
                (frequency >= 3),                     # Loyal
                (recency <= 60),                      # Potential Loyalists
                (recency <= 90),                      # At Risk
            ],
            ['Champions', 'Loyal', 'Potential Loyalists', 'At Risk'],
            default='Needs Attention'
        )
        return pd.Series(segments, index=df.index)
    
    
    def _create_fact_customer_rfm(self):
        """
        Crée la fact table customer RFM avec scores, segment, label marketing.
        """

        if 'orders' not in self.silver or 'customers' not in self.silver:
            logger.warning("orders ou customers absents - fact_customer_rfm non créée")
            return

        # Merge orders + customers pour amener customer_unique_id dans orders
        orders = self.silver['orders'].copy()
        customers = self.silver['customers'][['customer_id', 'customer_unique_id']].copy()
        orders = orders.merge(customers, on='customer_id', how='left')

        # SÉCURITÉ supplémentaire
        if 'customer_unique_id' not in orders.columns:
            logger.warning("'customer_unique_id' absent de orders après merge - abandon")
            return

        today = orders['order_purchase_timestamp'].max()

        # Calcul des montants de commande (on suppose colonne 'order_value' sinon adapte)
        if 'order_value' not in orders.columns:
            # Tente de le calculer depuis items
            if 'order_items' in self.silver:
                order_amounts = self.silver['order_items'].groupby('order_id')['total_price'].sum().reset_index()
                orders = orders.merge(order_amounts, on='order_id', how='left')
                orders = orders.rename(columns={'total_price': 'order_value'})
            else:
                orders['order_value'] = 0

        # Agrégation RFM (par customer_unique_id)
        agg = orders.groupby('customer_unique_id').agg(
            recency_days=('order_purchase_timestamp', lambda x: (today - x.max()).days),
            frequency=('order_id', 'nunique'),
            monetary=('order_value', 'sum')
        ).reset_index()

        # Scores (quintiles, sur 5)
        agg['recency_score'] = pd.qcut(agg['recency_days'], 5, labels=[5,4,3,2,1]).astype(int)
        agg['frequency_score'] = pd.qcut(agg['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
        agg['monetary_score'] = pd.qcut(agg['monetary'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)

        # Segment
        agg['rfm_segment'] = (
            agg['recency_score'].astype(str) +
            agg['frequency_score'].astype(str) +
            agg['monetary_score'].astype(str)
        )

        # Label marketing simple
        def label_rfm(row):
            if row['recency_score'] == 5 and row['frequency_score'] >= 4:
                return 'Champions'
            elif row['frequency_score'] >= 4:
                return 'Loyal'
            elif row['recency_score'] <= 2:
                return 'At Risk'
            elif row['frequency_score'] == 1:
                return 'One-Time'
            else:
                return 'Others'
        agg['rfm_label'] = agg.apply(label_rfm, axis=1)
        agg['rfm_as_of_date'] = today

        self.gold['fact_customer_rfm'] = agg
        logger.info(f"fact_customer_rfm créée: {len(agg)} lignes")
        
        
    def _calculate_rfm_segment(self, row) -> str:
        """
        Segmentation RFM simplifiée basée sur recency et frequency.
        
        Segments:
        - Champions: Achat récent, haute fréquence
        - Loyal: Fréquence élevée
        - One-Time: Un seul achat
        - At Risk: Pas d'achat récent mais historique d'achats
        - Lost: Très ancien, peu d'achats
        """
        recency = row.get('recency_days', 999)
        frequency = row.get('total_orders', 1)
        
        if frequency == 1:
            return 'One-Time'
        
        if recency <= 30 and frequency >= 3:
            return 'Champions'
        elif recency <= 90 and frequency >= 2:
            return 'Loyal'
        elif recency <= 180:
            return 'At Risk'
        else:
            return 'Lost'

    def _create_fact_product_performance(self):
        """
        Métriques de performance par produit.
        1 ligne = 1 produit.
        """
        if 'products' not in self.silver:
            logger.warning("Table 'products' manquante - fact_product_performance non créée")
            return
        
        products = self.silver['products'][['product_id', 'product_category_name']].copy()
        
        # Joindre avec category_id si disponible
        if 'dim_product_categories' in self.gold:
            categories = self.gold['dim_product_categories'][['category_id', 'product_category_name']]
            products = products.merge(categories, on='product_category_name', how='left')
            products['category_id'] = products['category_id'].fillna(-1).astype(int)
        else:
            products['category_id'] = -1
        
        # Métriques depuis order_items
        if 'order_items' in self.silver:
            items = self.silver['order_items'].copy()
            
            product_metrics = items.groupby('product_id', as_index=False).agg({
                'order_id': 'nunique',
                'order_item_id': 'count',
                'price': ['sum', 'mean']
            })
            product_metrics.columns = [
                'product_id', 'total_orders', 'total_units_sold', 
                'total_revenue', 'avg_price'
            ]
            
            products = products.merge(product_metrics, on='product_id', how='left')
        else:
            products['total_orders'] = 0
            products['total_units_sold'] = 0
            products['total_revenue'] = 0
            products['avg_price'] = 0
        
        # Métriques depuis reviews
        if 'reviews' in self.silver:
            # Joindre reviews via order_items
            if 'order_items' in self.silver:
                items_orders = self.silver['order_items'][['order_id', 'product_id']].drop_duplicates()
                reviews = self.silver['reviews'][['order_id', 'review_score']]
                product_reviews = items_orders.merge(reviews, on='order_id', how='inner')
                
                review_agg = product_reviews.groupby('product_id', as_index=False)['review_score'].mean()
                review_agg.columns = ['product_id', 'avg_review_score']
                
                products = products.merge(review_agg, on='product_id', how='left')
        
        if 'avg_review_score' not in products.columns:
            products['avg_review_score'] = np.nan
        
        # Remplir et arrondir
        for col in ['total_orders', 'total_units_sold', 'total_revenue']:
            products[col] = products[col].fillna(0).astype(int) if col != 'total_revenue' else products[col].fillna(0).round(2)
        
        products['avg_price'] = products['avg_price'].fillna(0).round(2)
        products['avg_review_score'] = products['avg_review_score'].round(2)
        
        # Colonnes finales
        fact_product = products[[
            'product_id', 'category_id', 'total_orders', 'total_units_sold',
            'total_revenue', 'avg_price', 'avg_review_score'
        ]].copy()
        
        self.gold['fact_product_performance'] = fact_product
        logger.info(f"fact_product_performance créée: {len(fact_product)} lignes")

    def _create_fact_category_performance(self):
        """
        Métriques de performance par catégorie.
        1 ligne = 1 catégorie.
        """
        if 'dim_product_categories' not in self.gold:
            logger.warning("dim_product_categories manquante - fact_category_performance non créée")
            return
        
        if 'fact_product_performance' not in self.gold:
            logger.warning("fact_product_performance manquante - fact_category_performance non créée")
            return
        
        categories = self.gold['dim_product_categories'].copy()
        products = self.gold['fact_product_performance'].copy()
        
        # Agrégation par category_id
        cat_metrics = products.groupby('category_id', as_index=False).agg({
            'product_id': 'count',
            'total_revenue': 'sum'
        })
        cat_metrics.columns = ['category_id', 'total_products', 'total_revenue']
        
        # Joindre avec categories pour les noms
        fact_cat = categories.merge(cat_metrics, on='category_id', how='left')
        
        # Remplir valeurs manquantes
        fact_cat['total_products'] = fact_cat['total_products'].fillna(0).astype(int)
        fact_cat['total_revenue'] = fact_cat['total_revenue'].fillna(0).round(2)
        
        # Calculer part de revenu et rang
        total_all_revenue = fact_cat['total_revenue'].sum()
        if total_all_revenue > 0:
            fact_cat['revenue_share_pct'] = (fact_cat['total_revenue'] / total_all_revenue * 100).round(2)
        else:
            fact_cat['revenue_share_pct'] = 0
        
        fact_cat['revenue_rank'] = fact_cat['total_revenue'].rank(method='dense', ascending=False).astype(int)
        
        # Renommer pour clarté
        fact_cat = fact_cat.rename(columns={
            'product_category_name': 'category_name_pt',
            'product_category_name_english': 'category_name'
        })
        
        # Colonnes finales
        cols_final = [
            'category_id', 'category_name', 'general_category',
            'total_products', 'total_revenue', 'revenue_share_pct', 'revenue_rank'
        ]
        
        existing_cols = [c for c in cols_final if c in fact_cat.columns]
        fact_category = fact_cat[existing_cols].copy()
        
        self.gold['fact_category_performance'] = fact_category
        logger.info(f"fact_category_performance créée: {len(fact_category)} lignes")
