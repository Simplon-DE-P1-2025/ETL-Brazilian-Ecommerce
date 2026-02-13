import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from src.loaders.postgres_loader import PostgresLoader
from kpi_gold_queries import NEW_RETURNING_CUSTOMERS_GOLD_QUERY, RFM_SEGMENTATION_GOLD_QUERY
from streamlit_lightweight_charts import renderLightweightCharts

def main():
    st.title("Tableau de bord Clients")
    st.markdown("Suivi des nouveaux clients, récurrents, segmentation RFM, et analyse de fidélité.")

    postgres_loader = PostgresLoader()

    st.subheader("Nouveaux vs Récurrents (par mois)")
    df_cust = postgres_loader.execute_query(NEW_RETURNING_CUSTOMERS_GOLD_QUERY)
    if 'year_month' in df_cust.columns and 'new_customers' in df_cust.columns and 'returning_customers' in df_cust.columns:
        seriesBarChart = [
            {"type": 'Bar', "data": [{"time": row['year_month'], "value": row['new_customers']} for _, row in df_cust.iterrows()], "options": {"color": '#1976d2'}},
            {"type": 'Bar', "data": [{"time": row['year_month'], "value": row['returning_customers']} for _, row in df_cust.iterrows()], "options": {"color": '#388e3c'}}
        ]
        renderLightweightCharts([
            {"chart": {"layout": {"textColor": 'black', "background": {"type": 'solid', "color": 'white'}}}, "series": seriesBarChart}
        ], 'bar_customers')
    else:
        st.warning("Colonnes manquantes. Voici le DataFrame:")
        st.write(df_cust)

    st.markdown("### Détail (tableau exportable)")
    st.dataframe(df_cust)

    st.subheader("Segmentation RFM")
    df_rfm = postgres_loader.execute_query(RFM_SEGMENTATION_GOLD_QUERY)
    if 'rfm_segment' in df_rfm.columns and 'customer_count' in df_rfm.columns:
        seriesPieChart = [{
            "type": 'Pie',
            "data": [{"label": row['rfm_segment'], "value": row['customer_count']} for _, row in df_rfm.iterrows()],
            "options": {}
        }]
        renderLightweightCharts([
            {"chart": {"layout": {"textColor": 'black', "background": {"type": 'solid', "color": 'white'}}}, "series": seriesPieChart}
        ], 'pie_rfm')
    else:
        st.warning("Colonnes manquantes. Voici le DataFrame:")
        st.write(df_rfm)

    st.markdown("---")
    st.subheader("Segmentation avancée et fidélité")
    st.markdown("- 97% des clients sont des acheteurs uniques, 3% font des achats répétés.\n- Les segments à fort potentiel : High-Spend, Core Audience, Promoters.\n- Les critics (notes < 3) ont des paniers élevés mais une fidélité faible : ciblez-les pour améliorer la rétention.\n- Les clients utilisant les paiements en plusieurs fois ont des paniers et une durée de vie plus élevés.")

    st.subheader("Recommandations business")
    st.markdown("- Mettre en place un programme de fidélité pour les acheteurs uniques.\n- Offrir un service premium aux clients Core et High-Spend.\n- Analyser les raisons de la faible rétention des promoteurs.\n- Cibler les critics avec des offres personnalisées et une amélioration logistique.")

    st.subheader("Insights comportementaux")
    st.markdown("- Les clients de São Paulo et Rio de Janeiro sont les plus nombreux : campagnes géolocalisées recommandées.\n- Les segments multi-produits et multi-paiements sont les plus rentables.\n- Les clients qui achètent le week-end sont plus fidèles.")
