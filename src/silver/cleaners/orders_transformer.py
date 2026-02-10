import pandas as pd
import numpy as np
from src.utils.functions import safe_to_datetime, remove_duplicates


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nom        : clean_orders
    Input      : df (DataFrame) - données brutes des commandes
    Output     : DataFrame - commandes nettoyées avec métriques livraison
    Description: Filtre période 2017-2018, impute dates manquantes,
                 calcule délais livraison, retards, dimensions temporelles
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    
    # Doublons sur order_id
    df = remove_duplicates(df, ['order_id'])
    
    # Conversion dates
    date_cols = ['order_purchase_timestamp', 'order_approved_at', 
                 'order_delivered_carrier_date', 'order_delivered_customer_date', 
                 'order_estimated_delivery_date']
    for col in date_cols:
        if col in df.columns:
            df[col] = safe_to_datetime(df[col])
    
    # Période valide: données fiables de janvier 2017 à août 2018
    # Avant 2017: données incomplètes, après sept 2018: quasi toutes annulées
    df = df[
        df['order_purchase_timestamp'].between('2017-01-01', '2018-09-01', inclusive='left')
        | df['order_purchase_timestamp'].isna()
    ]
    
    # Incohérences temporelles: livraison avant achat → NaT
    for col in ['order_delivered_customer_date', 'order_delivered_carrier_date', 'order_approved_at']:
        if col in df.columns:
            mask = df[col].notna() & (df[col] < df['order_purchase_timestamp'])
            df.loc[mask, col] = pd.NaT
    
    # Remplir dates manquantes avec délai médian (imputation)
    df = _fill_missing_dates(df)
    
    # Statuts valides
    valid_statuses = ['delivered', 'shipped', 'canceled', 'unavailable', 
                      'invoiced', 'processing', 'created', 'approved']
    df['order_status'] = df['order_status'].str.strip().str.lower()
    df.loc[~df['order_status'].isin(valid_statuses), 'order_status'] = 'processing'
    
    # === MÉTRIQUES TEMPORELLES ===
    
    # Délai approbation (heures)
    df['approval_delay_hours'] = (df['order_approved_at'] - df['order_purchase_timestamp']).dt.total_seconds() / 3600
    
    # Achat → transporteur (jours)
    df['purchase_to_carrier_days'] = (df['order_delivered_carrier_date'] - df['order_purchase_timestamp']).dt.total_seconds() / 86400
    df.loc[df['purchase_to_carrier_days'] < 0, 'purchase_to_carrier_days'] = df['purchase_to_carrier_days'].median()
    
    # Approbation → transporteur (jours)
    df['approved_to_carrier_days'] = (df['order_delivered_carrier_date'] - df['order_approved_at']).dt.total_seconds() / 86400
    df.loc[df['approved_to_carrier_days'] < 0, 'approved_to_carrier_days'] = df['approved_to_carrier_days'].median()
    
    # Transporteur → client (jours)
    df['carrier_to_customer_days'] = (df['order_delivered_customer_date'] - df['order_delivered_carrier_date']).dt.total_seconds() / 86400
    df.loc[df['carrier_to_customer_days'] < 0, 'carrier_to_customer_days'] = df['carrier_to_customer_days'].median()
    
    # Livraison totale (jours)
    df['delivery_days'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.total_seconds() / 86400
    
    # Livraison estimée (jours)
    df['delivery_estimated_days'] = (df['order_estimated_delivery_date'] - df['order_purchase_timestamp']).dt.total_seconds() / 86400
    
    # Écart livraison réelle vs estimée (jours)
    df['delivery_delta_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.total_seconds() / 86400
    
    # === DIMENSIONS CATÉGORIELLES ===
    
    # Livré oui/non
    df['is_delivered'] = (df['order_status'] == 'delivered')
    
    # En retard oui/non
    df['is_late'] = df['delivery_delta_days'] > 0
    
    # Catégorie délai livraison: Fast (≤5j), Medium (5-15j), Long (>15j)
    df['delivery_time_category'] = pd.cut(
        df['delivery_days'],
        bins=[-np.inf, 5, 15, np.inf],
        labels=['Fast', 'Medium', 'Long']
    )
    
    # Raison échec livraison
    df['delivery_issue_reason'] = 'No Issues'
    df.loc[df['order_status'].isin(['approved', 'shipped', 'processing', 'unavailable']), 'delivery_issue_reason'] = 'Service Issue'
    df.loc[df['order_status'].isin(['created', 'invoiced', 'canceled']), 'delivery_issue_reason'] = 'Customer Issue'
    
    # === DIMENSIONS TEMPORELLES ===
    
    df['purchase_year'] = df['order_purchase_timestamp'].dt.year
    df['purchase_month'] = df['order_purchase_timestamp'].dt.month
    df['purchase_month_name'] = df['order_purchase_timestamp'].dt.month_name()
    df['purchase_weekday'] = df['order_purchase_timestamp'].dt.dayofweek
    df['purchase_weekday_name'] = df['order_purchase_timestamp'].dt.day_name()
    df['purchase_hour'] = df['order_purchase_timestamp'].dt.hour
    
    # Type de jour: Weekend / Weekday
    df['purchase_day_type'] = np.where(
        df['purchase_weekday'].isin([5, 6]), 'Weekend', 'Weekday'
    )
    
    # Moment de la journée
    hour = df['purchase_hour']
    df['purchase_time_of_day'] = np.select(
        [
            hour.between(5, 11),   # 5h-11h
            hour.between(12, 16),  # 12h-16h
            hour.between(17, 22),  # 17h-22h
        ],
        ['Morning', 'Afternoon', 'Evening'],
        default='Night'  # 23h-4h
    )
    
    # Saison (hémisphère SUD: été = déc/jan/fév)
    month = df['order_purchase_timestamp'].dt.month
    df['purchase_season'] = np.select(
        [month.isin([12, 1, 2]), month.isin([3, 4, 5]), month.isin([6, 7, 8]), month.isin([9, 10, 11])],
        ['Summer', 'Autumn', 'Winter', 'Spring'],
        default=None
    )
    
    return df


def _fill_missing_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nom        : _fill_missing_dates
    Input      : df (DataFrame) - commandes avec dates potentiellement manquantes
    Output     : DataFrame - commandes avec dates imputées
    Description: Estime les dates manquantes en utilisant les délais médians
                 observés (approbation ~20min, transporteur ~1.8j, livraison ~7j)
    """
    
    # Délai médian: achat → approbation (~20 minutes)
    approval_delay = (df['order_approved_at'] - df['order_purchase_timestamp']).median()
    
    # Délai médian: approbation → remise transporteur (~1.8 jours)
    carrier_delay = (df['order_delivered_carrier_date'] - df['order_approved_at']).median()
    
    # Délai médian: transporteur → livraison client (~7 jours)
    delivery_delay = (df['order_delivered_customer_date'] - df['order_delivered_carrier_date']).median()
    
    # Remplir order_approved_at si manquant mais carrier_date présent
    mask = df['order_approved_at'].isna() & df['order_delivered_carrier_date'].notna()
    if mask.any() and pd.notna(approval_delay):
        df.loc[mask, 'order_approved_at'] = df.loc[mask, 'order_purchase_timestamp'] + approval_delay
    
    # Remplir order_delivered_carrier_date si manquant mais statut = delivered
    mask = df['order_delivered_carrier_date'].isna() & (
        df['order_delivered_customer_date'].notna() | (df['order_status'] == 'delivered')
    )
    if mask.any() and pd.notna(carrier_delay):
        df.loc[mask, 'order_delivered_carrier_date'] = df.loc[mask, 'order_approved_at'] + carrier_delay
    
    # Remplir order_delivered_customer_date si statut = delivered mais date manquante
    mask = df['order_delivered_customer_date'].isna() & (df['order_status'] == 'delivered')
    if mask.any() and pd.notna(delivery_delay):
        df.loc[mask, 'order_delivered_customer_date'] = df.loc[mask, 'order_delivered_carrier_date'] + delivery_delay
    
    return df
