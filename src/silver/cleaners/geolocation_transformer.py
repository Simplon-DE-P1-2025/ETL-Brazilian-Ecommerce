import pandas as pd


def clean_geolocation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nom        : clean_geolocation
    Input      : df (DataFrame) - données brutes de géolocalisation
    Output     : DataFrame - 1 ligne par code postal avec coordonnées moyennes
    Description: Valide coordonnées GPS, agrège par code postal (moyenne lat/lng),
                 supprime les doublons et coordonnées hors limites
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    
    # Doublons complets
    df = df.drop_duplicates()
    
    # Code postal numérique
    df['geolocation_zip_code_prefix'] = pd.to_numeric(
        df['geolocation_zip_code_prefix'], errors='coerce'
    ).astype('Int64')
    df = df[df['geolocation_zip_code_prefix'].between(1000, 99999)]
    
    # Coordonnées valides: lat [-90,90], lng [-180,180]
    df['geolocation_lat'] = pd.to_numeric(df['geolocation_lat'], errors='coerce')
    df['geolocation_lng'] = pd.to_numeric(df['geolocation_lng'], errors='coerce')
    df = df[
        (df['geolocation_lat'].between(-90, 90)) &
        (df['geolocation_lng'].between(-180, 180))
    ]
    
    # Agrégation par code postal: moyenne des coordonnées
    # On ignore ville/état car ils sont déjà dans customers/sellers
    df = df.groupby('geolocation_zip_code_prefix', as_index=False).agg({
        'geolocation_lat': 'mean',
        'geolocation_lng': 'mean'
    })
    
    # Champs dérivés
    df['geolocation_zip_code_prefix_3_digits'] = (
        df['geolocation_zip_code_prefix'].astype(str).str[:3].astype(int)
    )
    df['in_south_america'] = (
        df['geolocation_lat'].between(-53.90, 12.45) &
        df['geolocation_lng'].between(-81.32, -34.79)
    )
    
    return df
