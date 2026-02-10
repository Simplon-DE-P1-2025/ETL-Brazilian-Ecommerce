import pandas as pd
from src.utils.functions import clean_string, remove_duplicates


def clean_category_translation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nom        : clean_category_translation
    Input      : df (DataFrame) - données brutes des traductions de catégories
    Output     : DataFrame - catégories nettoyées (portugais → anglais)
    Description: Nettoie les noms de catégories (normalisation, suppression doublons)
                 et garde uniquement les lignes avec traduction complète
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    
    # Doublons sur nom catégorie
    df = remove_duplicates(df, ['product_category_name'])
    
    # Noms normalisés: minuscules, underscores
    df['product_category_name'] = clean_string(df['product_category_name'])
    df['product_category_name_english'] = (
        df['product_category_name_english']
        .str.strip()
        .str.lower()
        .str.replace(' ', '_', regex=False)
    )
    
    # Supprimer lignes sans traduction
    df = df[df['product_category_name'].notna() & df['product_category_name_english'].notna()]
    
    return df
