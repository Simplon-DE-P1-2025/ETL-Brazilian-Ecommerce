import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from src.loaders.postgres_loader import PostgresLoader
from app.kpi_gold_queries import RFM_SEGMENTATION_GOLD_QUERY
from streamlit_lightweight_charts import renderLightweightCharts

def main():
    st.title("Tableau de bord RFM & Segmentation")
    st.markdown("Analyse des segments clients selon la méthode RFM.")

    postgres_loader = PostgresLoader()

    st.subheader("Distribution des segments RFM")
    df_rfm = postgres_loader.execute_query(RFM_SEGMENTATION_GOLD_QUERY)
    if 'rfm_segment' in df_rfm.columns and 'customer_count' in df_rfm.columns:
        df_rfm = df_rfm.set_index('rfm_segment')
        st.bar_chart(df_rfm['customer_count'])
    else:
        st.warning("Colonnes manquantes. Voici le DataFrame:")
        st.write(df_rfm)

    st.markdown("### Détail (tableau exportable)")
    st.dataframe(df_rfm)

    st.markdown("---")
    st.markdown("**Commentaires business** :\n\n- La segmentation RFM permet d'identifier les clients à fidéliser, à relancer ou à valoriser.")
