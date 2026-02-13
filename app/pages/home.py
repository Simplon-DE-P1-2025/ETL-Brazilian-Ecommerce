import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.loaders.postgres_loader import PostgresLoader
from kpi_queries import SALES_MONTHLY_QUERY, RFM_DISTRIBUTION_QUERY ,TOP_PRODUCTS_QUERY

def main():
    postgres_loader = PostgresLoader()
    st.title("Dashboard e-commerce 🛒")

    # Affichage KPI CA actuel
    df = postgres_loader.execute_query(SALES_MONTHLY_QUERY)
    st.metric("CA Total", f"{df['total_sales'].sum():,.0f} €")

    # Affichage courbe CA
    if 'year_month' in df.columns and 'total_sales' in df.columns:
        st.line_chart(df.set_index('year_month')['total_sales'])
    else:
        st.warning("La colonne 'year_month' ou 'total_sales' est absente des données. Impossible d'afficher la courbe CA.")

    # Affichage segmentation RFM
    st.subheader("Distribution RFM")
    df_rfm = postgres_loader.execute_query(RFM_DISTRIBUTION_QUERY)
    st.bar_chart(df_rfm.set_index('rfm_label')['num_customers'])

    st.title("Top 10 produits 🥇")
    df = postgres_loader.execute_query(TOP_PRODUCTS_QUERY)
    st.bar_chart(df.set_index('product_id')['total_revenue'])
    st.dataframe(df)