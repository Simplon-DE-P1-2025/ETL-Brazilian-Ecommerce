import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from src.loaders.postgres_loader import PostgresLoader
from app.kpi_gold_queries import TOP_PRODUCTS_GOLD_QUERY
from streamlit_lightweight_charts import renderLightweightCharts

def main():
    st.title("Tableau de bord Produits")
    st.markdown("Analyse des meilleures ventes, catégories, et performance produit.")

    postgres_loader = PostgresLoader()

    st.subheader("Top 10 produits (par ventes)")
    df_top = postgres_loader.execute_query(TOP_PRODUCTS_GOLD_QUERY)
    if 'product_id' in df_top.columns and 'total_sales' in df_top.columns:
        seriesBarChart = [{
            "type": 'Bar',
            "data": [{"time": row['product_id'], "value": row['total_sales']} for _, row in df_top.iterrows()],
            "options": {}
        }]
        renderLightweightCharts([
            {"chart": {"layout": {"textColor": 'black', "background": {"type": 'solid', "color": 'white'}}}, "series": seriesBarChart}
        ], 'bar_top_products')
    else:
        st.warning("Colonnes manquantes. Voici le DataFrame:")
        st.write(df_top)

    st.markdown("### Détail (tableau exportable)")
    st.dataframe(df_top)

    st.markdown("---")
    st.subheader("Analyse avancée des produits")
    st.markdown("- Les best-sellers : Electronics, Furniture, Home & Garden.\n- Les catégories Beauty/Health et Home/Garden sont en croissance : à développer.\n- Watches & Gifts : volatilité des prix, à surveiller.\n- 2,5% des produits jamais vendus : opportunité de liquidation ou repositionnement.")

    st.subheader("Recommandations business")
    st.markdown("- Étendre l’assortiment sur les catégories en croissance.\n- Mettre en place des bundles et promotions sur les multi-produits.\n- Gérer les stocks morts par des campagnes de liquidation.")
