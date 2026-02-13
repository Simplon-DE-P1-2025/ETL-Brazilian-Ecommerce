import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from src.loaders.postgres_loader import PostgresLoader
from streamlit_lightweight_charts import renderLightweightCharts

def main():
    st.title("Tableau de bord Livraison")
    st.markdown("Analyse des délais, coûts et anomalies de livraison.")

    postgres_loader = PostgresLoader()
    # Placeholder: à compléter avec requêtes gold spécifiques livraison
    st.subheader("À venir : indicateurs livraison (délais, coûts, anomalies)")
    st.markdown("---")
    st.subheader("Analyse avancée de la livraison")
    st.markdown("- 75% des commandes livrées en moins de 16 jours, 5% en plus de 30 jours.\n- Les retards sont plus fréquents sur les commandes lourdes et chères.\n- Les retards impactent négativement les ratings et la fidélité.\n- Les régions critiques : Pará, Maranhão, Ceará, Salvador, Porto Alegre, Rio de Janeiro.")

    st.subheader("Recommandations logistiques")
    st.markdown("- Optimiser la logistique pour les commandes lourdes et premium.\n- Mettre en place un suivi renforcé sur les régions à problème.\n- Réduire le délai entre paiement et expédition pour améliorer l’expérience client.")
