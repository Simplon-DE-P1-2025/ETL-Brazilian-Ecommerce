import pandas as pd


def clean_payments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nom        : clean_payments
    Input      : df (DataFrame) - données brutes des paiements
    Output     : DataFrame - paiements nettoyés avec indicateur échelonnement
    Description: Valide types de paiement, corrige montants négatifs,
                 limite mensualités entre 1 et 24
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    
    # Doublons complets
    df = df.drop_duplicates()
    
    # Types de paiement valides
    valid_types = ['credit_card', 'boleto', 'voucher', 'debit_card']
    df['payment_type'] = df['payment_type'].str.strip().str.lower()
    df = df[df['payment_type'].isin(valid_types)]
    
    # Montants numériques, négatifs → 0
    df['payment_value'] = pd.to_numeric(df['payment_value'], errors='coerce')
    df['payment_value'] = df['payment_value'].fillna(0).clip(lower=0)
    
    # Mensualités: NaN ou <1 → 1, max 24
    df['payment_installments'] = pd.to_numeric(df['payment_installments'], errors='coerce')
    df['payment_installments'] = df['payment_installments'].fillna(1).clip(lower=1, upper=24).astype(int)
    
    # Indicateur échelonnement
    df['has_installments'] = (df['payment_installments'] > 1).map({True: 'yes', False: 'no'})
    
    return df
