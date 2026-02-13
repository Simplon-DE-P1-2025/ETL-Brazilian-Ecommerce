import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from src.loaders.postgres_loader import PostgresLoader

def main():
    st.title("Tableau de bord Anomalies")
    st.markdown("Détection et analyse des anomalies dans les données e-commerce.")

    postgres_loader = PostgresLoader()
    # Placeholder: à compléter avec requêtes gold spécifiques anomalies
    st.subheader("À venir : détection des anomalies (doublons, valeurs manquantes, incohérences)")
    st.markdown("---")
    st.subheader("Détection avancée des anomalies")
    st.markdown("- Doublons : géolocalisation, reviews, produits.\n- Valeurs manquantes : dates, paiements, caractéristiques produits.\n- Incohérences : statuts, dates, reviews multiples, produits multi-vendeurs.\n- Anomalies critiques : pics de cancellations, retards, incohérences de livraison.")

    st.subheader("Recommandations qualité data")
    st.markdown("- Mettre en place des contrôles automatiques pour détecter et corriger les anomalies.\n- Prioriser la correction des anomalies critiques pour fiabiliser les analyses.\n- Documenter les cas récurrents pour améliorer les processus ETL.")
