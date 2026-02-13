import streamlit as st
from src.loaders.postgres_loader import PostgresLoader
from kpi_queries import RFM_DISTRIBUTION_QUERY


def main():
    st.title("Segmentation RFM 🎯")
    postgres_loader = PostgresLoader()
    df = postgres_loader.execute_query(RFM_DISTRIBUTION_QUERY)
    # Pie fallback: show table and bar chart (lightweight-charts has no pie)
    st.subheader("Distribution clients RFM (bar)")
    if 'rfm_label' in df.columns and 'num_customers' in df.columns:
        df_bar = df.set_index('rfm_label')
        st.bar_chart(df_bar['num_customers'])
    else:
        st.warning("Colonnes manquantes. Voici le DataFrame:")
        st.write(df)
    st.table(df[['rfm_label', 'pct_customers']])

