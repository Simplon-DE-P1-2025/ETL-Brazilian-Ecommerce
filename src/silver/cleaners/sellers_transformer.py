import pandas as pd
from src.utils.functions import clean_string, remove_duplicates
from config.settings import STATES, REGION_MAPPING, STATE_NAMES


def clean_sellers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nom        : clean_sellers
    Input      : df (DataFrame) - données brutes des vendeurs
    Output     : DataFrame - vendeurs nettoyés avec région
    Description: Valide codes postaux et états brésiliens, supprime doublons,
                 ajoute région et nom complet de l'état
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    
    # Doublons sur seller_id
    df = remove_duplicates(df, ['seller_id'])
    
    # Code postal valide: 5 chiffres entre 01000 et 99999
    df = df[df['seller_zip_code_prefix'].notna()]
    df['seller_zip_code_prefix'] = pd.to_numeric(df['seller_zip_code_prefix'], errors='coerce').astype('Int64')
    df = df[df['seller_zip_code_prefix'].between(1000, 99999)]
    
    # Ville minuscules, État majuscules
    df['seller_city'] = clean_string(df['seller_city'])
    df['seller_state'] = df['seller_state'].str.strip().str.upper()
    
    # États brésiliens valides uniquement
    df = df[df['seller_state'].isin(STATES)]
    
    # Champs dérivés
    df['seller_state_name'] = df['seller_state'].map(STATE_NAMES)  # Nom complet
    df['seller_region'] = df['seller_state'].map(REGION_MAPPING)
    df['seller_zip_code_prefix_3_digits'] = df['seller_zip_code_prefix'].astype(str).str[:3].astype(int)
    
    return df
