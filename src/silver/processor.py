from typing import Dict
import pandas as pd
from loguru import logger
from src.silver.cleaners.customers_transformer import clean_customers
from src.silver.cleaners.orders_transformer import clean_orders
from src.silver.cleaners.products_transformer import clean_products
from src.silver.cleaners.sellers_transformer import clean_sellers
from src.silver.cleaners.payments_transformer import clean_payments
from src.silver.cleaners.reviews_transformer import clean_reviews
from src.silver.cleaners.order_items_transformer import clean_order_items
from src.silver.cleaners.geolocation_transformer import clean_geolocation
from src.silver.cleaners.category_transformer import clean_category_translation


CLEANERS = {
    'customers': clean_customers,
    'orders': clean_orders,
    'products': clean_products,
    'sellers': clean_sellers,
    'payments': clean_payments,
    'reviews': clean_reviews,
    'order_items': clean_order_items,
    'geolocation': clean_geolocation,
    'category_translation': clean_category_translation,
}


class SilverProcessor:
    """Applique les fonctions de nettoyage sur chaque dataset bronze"""

    def process(self, bronze_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        silver_data = {}
        
        # Nettoyer chaque dataset
        for name, df in bronze_data.items():
            cleaner = CLEANERS.get(name)
            if cleaner:
                silver_data[name] = cleaner(df)
            else:
                silver_data[name] = df
        
        # Filtrage par intégrité référentielle (après nettoyage de orders)
        silver_data = self._filter_by_order_presence(silver_data)
        
        return silver_data
    
    def _filter_by_order_presence(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Garder uniquement les enregistrements liés à une commande existante"""
        
        if 'orders' not in data:
            return data
        
        valid_order_ids = set(data['orders']['order_id'].dropna())
        valid_customer_ids = set(data['orders']['customer_id'].dropna())
        
        # Customers: garder seulement ceux avec une commande
        if 'customers' in data:
            before = len(data['customers'])
            data['customers'] = data['customers'][
                data['customers']['customer_id'].isin(valid_customer_ids)
            ]
            after = len(data['customers'])
            if before > after:
                logger.info(f"  → Customers: {before - after} orphelins supprimés")
        
        # Payments: garder seulement ceux liés à une commande existante
        if 'payments' in data:
            before = len(data['payments'])
            data['payments'] = data['payments'][
                data['payments']['order_id'].isin(valid_order_ids)
            ]
            after = len(data['payments'])
            if before > after:
                logger.info(f"  → Payments: {before - after} orphelins supprimés")
        
        # Reviews: garder seulement ceux liés à une commande existante
        if 'reviews' in data:
            before = len(data['reviews'])
            data['reviews'] = data['reviews'][
                data['reviews']['order_id'].isin(valid_order_ids)
            ]
            after = len(data['reviews'])
            if before > after:
                logger.info(f"  → Reviews: {before - after} orphelins supprimés")
        
        # Order_items: garder seulement ceux liés à une commande existante
        if 'order_items' in data:
            before = len(data['order_items'])
            data['order_items'] = data['order_items'][
                data['order_items']['order_id'].isin(valid_order_ids)
            ]
            after = len(data['order_items'])
            if before > after:
                logger.info(f"  → Order_items: {before - after} orphelins supprimés")
        
        # Products et Sellers: garder tous (pour identifier ceux jamais vendus)
        
        return data