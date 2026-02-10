import pandas as pd
from src.utils.functions import safe_to_datetime


def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nom        : clean_order_items
    Input      : df (DataFrame) - données brutes des articles commandés
    Output     : DataFrame - articles nettoyés avec total_price calculé
    Description: Valide prix et frais de port, corrige valeurs négatives,
                 calcule le prix total (prix + frais)
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    
    # Doublons complets
    df = df.drop_duplicates()
    
    # Date limite expédition
    if 'shipping_limit_date' in df.columns:
        df['shipping_limit_date'] = safe_to_datetime(df['shipping_limit_date'])
    
    # Montants numériques
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['freight_value'] = pd.to_numeric(df['freight_value'], errors='coerce')
    
    # Négatifs → 0 (au lieu de supprimer)
    df['price'] = df['price'].clip(lower=0)
    df['freight_value'] = df['freight_value'].fillna(0).clip(lower=0)
    
    # order_item_id valide (≥ 1)
    df['order_item_id'] = pd.to_numeric(df['order_item_id'], errors='coerce')
    df = df[df['order_item_id'] >= 1]
    df['order_item_id'] = df['order_item_id'].astype(int)
    
    # Total
    df['total_price'] = df['price'] + df['freight_value']
    
    return df
