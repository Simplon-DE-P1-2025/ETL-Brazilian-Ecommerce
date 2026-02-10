import pandas as pd
from src.utils.functions import clean_string, remove_duplicates
from config.settings import STATES, REGION_MAPPING, POPULATION, STATE_NAMES


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nom        : clean_customers
    Input      : df (DataFrame) - données brutes des clients
    Output     : DataFrame - clients nettoyés avec région et population
    Description: Valide codes postaux et états brésiliens, supprime doublons,
                 ajoute région et nom complet de l'état
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    
    # Doublons sur customer_id
    df = remove_duplicates(df, ['customer_id'])
    
    # Code postal valide: 5 chiffres entre 01000 et 99999
    df = df[df['customer_zip_code_prefix'].notna()]
    df['customer_zip_code_prefix'] = pd.to_numeric(df['customer_zip_code_prefix'], errors='coerce').astype('Int64')
    df = df[df['customer_zip_code_prefix'].between(1000, 99999)]
    
    # Ville minuscules, État majuscules
    df['customer_city'] = clean_string(df['customer_city'])
    df['customer_state'] = df['customer_state'].str.strip().str.upper()
    
    # États brésiliens valides uniquement
    df = df[df['customer_state'].isin(STATES)]
    
    # Champs dérivés
    df['customer_state_name'] = df['customer_state'].map(STATE_NAMES)  # Nom complet
    df['customer_region'] = df['customer_state'].map(REGION_MAPPING)
    df['customer_zip_code_prefix_3_digits'] = df['customer_zip_code_prefix'].astype(str).str[:3].astype(int)
    df['population'] = df['customer_state'].map(POPULATION)
    
    return df
