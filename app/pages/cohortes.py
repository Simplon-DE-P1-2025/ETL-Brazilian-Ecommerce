import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from src.loaders.postgres_loader import PostgresLoader
from kpi_gold_queries import COHORT_RETENTION_GOLD_QUERY, COHORT_LTV_GOLD_QUERY
from streamlit_lightweight_charts import renderLightweightCharts

def main():
    st.title("Tableau de bord Cohortes")
    st.markdown("Analyse de la rétention et de la valeur client par cohorte.")

    postgres_loader = PostgresLoader()

    st.subheader("Rétention par cohorte")
    df_ret = postgres_loader.execute_query(COHORT_RETENTION_GOLD_QUERY)
    if 'cohort_month' in df_ret.columns and 'cohort_size' in df_ret.columns:
        seriesBarChart = [{
            "type": 'Bar',
            "data": [{"time": row['cohort_month'], "value": row['cohort_size']} for _, row in df_ret.iterrows()],
            "options": {}
        }]
        renderLightweightCharts([
            {"chart": {"layout": {"textColor": 'black', "background": {"type": 'solid', "color": 'white'}}}, "series": seriesBarChart}
        ], 'bar_cohort_retention')
    else:
        st.warning("Colonnes manquantes. Voici le DataFrame:")
        st.write(df_ret)

    st.markdown("### Détail (tableau exportable)")
    st.dataframe(df_ret)

    st.subheader("LTV par cohorte")
    df_ltv = postgres_loader.execute_query(COHORT_LTV_GOLD_QUERY)
    if 'cohort_month' in df_ltv.columns and 'avg_ltv' in df_ltv.columns:
        seriesLineChart = [{
            "type": 'Line',
            "data": [{"time": row['cohort_month'], "value": row['avg_ltv']} for _, row in df_ltv.iterrows()],
            "options": {}
        }]
        renderLightweightCharts([
            {"chart": {"layout": {"textColor": 'black', "background": {"type": 'solid', "color": 'white'}}}, "series": seriesLineChart}
        ], 'line_cohort_ltv')
    else:
        st.warning("Colonnes manquantes. Voici le DataFrame:")
        st.write(df_ltv)

    st.markdown("---")
    st.subheader("Analyse avancée des cohortes")
    st.markdown("- La majorité des clients ne revient pas après le premier achat : la rétention est le principal levier à travailler.\n- Les cohortes avec LTV élevée sont souvent liées à des segments High-Spend ou Core Audience.\n- Les cohortes week-end montrent une fidélité supérieure.\n- Les cohortes critiques : mars 2017, avril 2017, mars 2018 (anomalies ou opportunités à investiguer).")

    st.subheader("Recommandations business")
    st.markdown("- Mettre en place des campagnes de réactivation pour les cohortes à faible rétention.\n- Cibler les segments à forte LTV avec des offres premium.\n- Analyser les cohortes critiques pour détecter les causes de churn ou d’opportunité.")
