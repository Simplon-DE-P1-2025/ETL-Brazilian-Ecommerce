import pandas as pd
from src.utils.functions import clean_string, remove_duplicates, calculate_volume_cm3


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nom        : clean_products
    Input      : df (DataFrame) - données brutes du catalogue produits
    Output     : DataFrame - produits nettoyés avec volume calculé
    Description: Impute poids et dimensions par médiane de catégorie,
                 calcule volume en cm3 et litres, normalise catégories
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    
    # Doublons sur product_id
    df = remove_duplicates(df, ['product_id'])
    
    # Catégorie: normaliser, NaN → 'unknown'
    df['product_category_name'] = clean_string(df['product_category_name'])
    df['product_category_name'] = df['product_category_name'].fillna('unknown')
    
    # Dimensions numériques
    numeric_cols = ['product_weight_g', 'product_length_cm', 'product_height_cm', 
                    'product_width_cm', 'product_photos_qty']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Photos: NaN → 1 (médiane et mode)
    df['product_photos_qty'] = df['product_photos_qty'].fillna(1).astype(int)
    
    # Poids = 0 → valeur non renseignée, remplacer par médiane de la catégorie
    df = _fill_zero_weight_by_category(df)
    
    # Dimensions manquantes → médiane par catégorie
    df = _fill_missing_dimensions_by_category(df)
    
    # Volume calculé
    df['product_volume_cm3'] = calculate_volume_cm3(df)
    df['product_volume_liters'] = df['product_volume_cm3'] / 1000
    df['volumetric_weight_kg'] = df['product_volume_cm3'] / 5000
    
    return df


def _fill_zero_weight_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nom        : _fill_zero_weight_by_category
    Input      : df (DataFrame) - produits avec poids potentiellement à 0
    Output     : DataFrame - produits avec poids corrigés
    Description: Remplace les poids égaux à 0 par la médiane des produits
                 de la même catégorie
    """
    zero_weight_mask = df['product_weight_g'] == 0
    
    if zero_weight_mask.any():
        for category in df.loc[zero_weight_mask, 'product_category_name'].unique():
            category_median = df.loc[
                (df['product_category_name'] == category) & (df['product_weight_g'] > 0),
                'product_weight_g'
            ].median()
            
            if pd.notna(category_median):
                mask = zero_weight_mask & (df['product_category_name'] == category)
                df.loc[mask, 'product_weight_g'] = category_median
    
    return df


def _fill_missing_dimensions_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nom        : _fill_missing_dimensions_by_category
    Input      : df (DataFrame) - produits avec dimensions manquantes
    Output     : DataFrame - produits avec dimensions complétées
    Description: Remplace dimensions manquantes par la médiane de la catégorie,
                 ou par la médiane globale si catégorie insuffisante
    """
    dim_cols = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
    
    for col in dim_cols:
        missing_mask = df[col].isna()
        
        if missing_mask.any():
            # Médiane globale comme fallback
            global_median = df[col].median()
            
            for category in df.loc[missing_mask, 'product_category_name'].unique():
                category_median = df.loc[
                    (df['product_category_name'] == category) & df[col].notna(),
                    col
                ].median()
                
                fill_value = category_median if pd.notna(category_median) else global_median
                
                if pd.notna(fill_value):
                    mask = missing_mask & (df['product_category_name'] == category)
                    df.loc[mask, col] = fill_value
    
    return df
