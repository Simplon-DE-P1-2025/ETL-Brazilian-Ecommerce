import pandas as pd
import numpy as np
from typing import List
from loguru import logger


def clean_string(series: pd.Series) -> pd.Series:
    """
    Nom        : clean_string
    Input      : series (Series) - colonne texte brute
    Output     : Series - texte normalisé (minuscules, sans espaces)
    Description: Nettoie une colonne texte en appliquant strip, lowercase,
                 et remplace 'nan' et vide par NaN
    """
    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
        .replace('nan', np.nan)
        .replace('', np.nan)
    )


def remove_duplicates(df: pd.DataFrame, subset: List[str]) -> pd.DataFrame:
    """
    Nom        : remove_duplicates
    Input      : df (DataFrame), subset (List[str]) - colonnes pour détection
    Output     : DataFrame - sans doublons sur les colonnes spécifiées
    Description: Supprime les doublons en gardant la première occurrence,
                 et log le nombre de lignes supprimées
    """
    initial = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep='first')
    removed = initial - len(df_clean)
    if removed > 0:
        logger.warning(f"  {removed:,} doublons retirés sur {subset}")
    return df_clean


def safe_to_datetime(series: pd.Series) -> pd.Series:
    """
    Nom        : safe_to_datetime
    Input      : series (Series) - colonne avec dates en texte
    Output     : Series - dates converties (NaT si invalide)
    Description: Convertit en datetime avec gestion d'erreurs (coerce)
    """
    return pd.to_datetime(series, errors='coerce')


def calculate_volume_cm3(df: pd.DataFrame) -> pd.Series:
    """
    Nom        : calculate_volume_cm3
    Input      : df (DataFrame) - avec colonnes length, height, width en cm
    Output     : Series - volume en cm3
    Description: Calcule le volume du produit (longueur x hauteur x largeur)
    """
    return df['product_length_cm'] * df['product_height_cm'] * df['product_width_cm']


def fill_missing_with_mode(series: pd.Series) -> pd.Series:
    """
    Nom        : fill_missing_with_mode
    Input      : series (Series) - colonne avec valeurs manquantes
    Output     : Series - valeurs manquantes remplacées par le mode
    Description: Remplit les NaN par le mode (valeur la plus fréquente),
                 ou la médiane si pas de mode
    """
    if series.isnull().sum() > 0:
        mode_value = series.mode()[0] if len(series.mode()) > 0 else series.median()
        return series.fillna(mode_value)
    return series


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Nom        : haversine_distance
    Input      : lat1, lon1, lat2, lon2 (float) - coordonnées GPS
    Output     : float - distance en kilomètres
    Description: Calcule la distance à vol d'oiseau entre deux points GPS
                 en utilisant la formule de Haversine
    """
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return 6371 * c
