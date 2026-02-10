import pandas as pd
import numpy as np
from src.utils.functions import safe_to_datetime, remove_duplicates


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nom        : clean_reviews
    Input      : df (DataFrame) - données brutes des avis clients
    Output     : DataFrame - avis nettoyés avec métriques temporelles
    Description: Valide scores [1-5], calcule délai de réponse et longueur
                 commentaire, ajoute dimensions temporelles (saison, weekend)
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    
    # Doublons sur review_id
    df = remove_duplicates(df, ['review_id'])
    
    # Score numérique, hors [1,5] → NaN (garder la ligne)
    df['review_score'] = pd.to_numeric(df['review_score'], errors='coerce')
    df.loc[~df['review_score'].between(1, 5), 'review_score'] = pd.NA
    
    # Commentaires: NaN → chaîne vide
    if 'review_comment_title' in df.columns:
        df['review_comment_title'] = df['review_comment_title'].fillna('')
    if 'review_comment_message' in df.columns:
        df['review_comment_message'] = df['review_comment_message'].fillna('')
    
    # Dates
    for col in ['review_creation_date', 'review_answer_timestamp']:
        if col in df.columns:
            df[col] = safe_to_datetime(df[col])
    
    # Période valide
    df = df[(df['review_creation_date'] >= '2017-01-01') | df['review_creation_date'].isna()]
    
    # === MÉTRIQUES DÉRIVÉES ===
    
    df['review_comment_length'] = df['review_comment_message'].str.len()
    
    if 'review_answer_timestamp' in df.columns:
        # Délai réponse en jours
        df['response_delay_days'] = (
            df['review_answer_timestamp'] - df['review_creation_date']
        ).dt.total_seconds() / 86400
    
    # === DIMENSIONS TEMPORELLES ===
    
    # Jour de la semaine
    df['review_weekday'] = df['review_creation_date'].dt.dayofweek
    df['review_weekday_name'] = df['review_creation_date'].dt.day_name()
    
    # Type de jour: Weekend / Weekday
    df['review_day_type'] = np.where(
        df['review_weekday'].isin([5, 6]), 'Weekend', 'Weekday'
    )
    
    # Saison (hémisphère SUD)
    month = df['review_creation_date'].dt.month
    df['review_season'] = np.select(
        [month.isin([12, 1, 2]), month.isin([3, 4, 5]), month.isin([6, 7, 8]), month.isin([9, 10, 11])],
        ['Summer', 'Autumn', 'Winter', 'Spring'],
        default=None
    )
    
    return df
