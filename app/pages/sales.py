import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
import streamlit as st
from src.loaders.postgres_loader import PostgresLoader
from kpi_gold_queries import SALES_DAILY_GOLD_QUERY, SALES_MONTHLY_GOLD_QUERY, SALES_YEARLY_GOLD_QUERY, SALES_YOY_GOLD_QUERY, TOP_PRODUCTS_GOLD_QUERY, AVG_BASKET_GOLD_QUERY, CONVERSION_RATE_GOLD_QUERY
from streamlit_lightweight_charts import renderLightweightCharts



def main():
    st.title("Tableau de bord des ventes")
    st.markdown("Suivi du chiffre d'affaires, évolution, top produits, panier moyen, taux de conversion.")

    postgres_loader = PostgresLoader()
    granularite = st.selectbox(
        "Choisissez la granularité",
        ["Jour", "Mois", "Année"],
        index=1
    )

    chartOptions = {
        "layout": {
            "textColor": 'black',
            "background": {
                "type": 'solid',
                "color": 'white'
            }
        }
    }

    # CA selon granularité
    if granularite == "Jour":
        df = postgres_loader.execute_query(SALES_DAILY_GOLD_QUERY)
        x_col = 'date'
        titre = "Évolution du chiffre d'affaires journalier"
    elif granularite == "Mois":
        df = postgres_loader.execute_query(SALES_MONTHLY_GOLD_QUERY)
        x_col = 'year_month'
        titre = "Évolution du chiffre d'affaires mensuel"
    else:
        df = postgres_loader.execute_query(SALES_YEARLY_GOLD_QUERY)
        x_col = 'year'
        titre = "Évolution du chiffre d'affaires annuel"

    st.subheader(titre)
    if x_col in df.columns and 'total_sales' in df.columns:
        # Remplacer NaN par 0 et forcer float
        df['total_sales'] = df['total_sales'].astype(float).fillna(0)
        # Vérifier que le DataFrame n'est pas vide
        if df.empty:
            st.warning("Aucune donnée disponible pour l'évolution annuelle.")
            st.write(df)
        else:
            seriesLineChart = [{
                "type": 'Line',
                "data": [
                    {"time": f"{int(row[x_col])}-01-01", "value": row['total_sales']} if granularite == "Année" else {"time": str(row[x_col]), "value": row['total_sales']} 
                    for _, row in df.iterrows()
                ],
                "options": {}
            }]
            renderLightweightCharts([
                {"chart": chartOptions, "series": seriesLineChart}
            ], f"line_{granularite.lower()}_{st.session_state.get('unique_id', '')}")
    else:
        st.warning(f"Colonnes '{x_col}' ou 'total_sales' absentes des données. Voici le DataFrame:")
        st.write(df)

    # Bloc supprimé : affichage dupliqué du graphique annuel

    st.markdown("### Détail des ventes (tableau exportable)")
    st.dataframe(df)

    # Évolution CA vs N-1
    st.subheader("Évolution du CA vs N-1")
    df_yoy = postgres_loader.execute_query(SALES_YOY_GOLD_QUERY)
    if 'year_month' in df_yoy.columns and 'yoy_growth' in df_yoy.columns:
        # Remplacer NaN par 0 et forcer float
        df_yoy['yoy_growth'] = df_yoy['yoy_growth'].astype(float).fillna(0)
        # Générer la liste sans NaN
        chart_data = []
        for _, row in df_yoy.iterrows():
            value = row['yoy_growth']
            if value is None or (isinstance(value, float) and (value != value)):
                value = 0
            chart_data.append({"time": row['year_month'], "value": value})
        seriesAreaChart = [{
            "type": 'Area',
            "data": chart_data,
            "options": {}
        }]
        renderLightweightCharts([
            {"chart": chartOptions, "series": seriesAreaChart}
        ], 'area_yoy')
    else:
        st.warning("Colonnes 'year_month' ou 'yoy_growth' absentes des données. Voici le DataFrame:")
        st.write(df_yoy)

    # Top 10 produits
    st.subheader("Top 10 produits (par ventes)")
    df_top = postgres_loader.execute_query(TOP_PRODUCTS_GOLD_QUERY)
    if 'product_id' in df_top.columns and 'total_sales' in df_top.columns:
        df_top = df_top.sort_values('total_sales', ascending=False).head(10)
        st.bar_chart(df_top.set_index('product_id')['total_sales'])
    else:
        st.warning("Colonnes 'product_id' ou 'total_sales' absentes des données. Voici le DataFrame:")
        st.write(df_top)

    st.markdown("### Détail des produits (tableau exportable)")
    st.dataframe(df_top)

    # Panier moyen
    st.subheader("Panier moyen")
    df_basket = postgres_loader.execute_query(AVG_BASKET_GOLD_QUERY)
    if 'year_month' in df_basket.columns and 'avg_basket_value' in df_basket.columns:
        seriesLineChart = [{
            "type": 'Line',
            "data": [{"time": row['year_month'], "value": row['avg_basket_value']} for _, row in df_basket.iterrows()],
            "options": {}
        }]
        renderLightweightCharts([
            {"chart": chartOptions, "series": seriesLineChart}
        ], 'line_basket')
    else:
        st.warning("Colonnes 'year_month' ou 'avg_basket_value' absentes des données. Voici le DataFrame:")
        st.write(df_basket)

    # Taux de conversion
    st.subheader("Taux de conversion")
    df_conv = postgres_loader.execute_query(CONVERSION_RATE_GOLD_QUERY)
    if 'year_month' in df_conv.columns and 'conversion_rate' in df_conv.columns:
        seriesLineChart = [{
            "type": 'Line',
            "data": [{"time": row['year_month'], "value": row['conversion_rate']} for _, row in df_conv.iterrows()],
            "options": {}
        }]
        renderLightweightCharts([
            {"chart": chartOptions, "series": seriesLineChart}
        ], 'line_conversion')
    else:
        st.warning("Colonnes 'year_month' ou 'conversion_rate' absentes des données. Voici le DataFrame:")
        st.write(df_conv)

    st.markdown("---")
    st.subheader("Analyse avancée : Paiement en plusieurs fois et retards")
    st.markdown("**Impact des commandes en plusieurs fois** : Les commandes avec paiement en plusieurs fois sont traitées plus rapidement, ont une valeur, un poids, un prix produit et un coût de livraison plus élevés.\n\n**Analyse des retards** : Les commandes retardées présentent des valeurs, poids, prix produit et coûts de livraison supérieurs, et reçoivent des notes plus basses. Les commandes non retardées ont plus de chances d’obtenir une note élevée.")

    st.subheader("Breakdown par rating et livraison")
    st.markdown("- Les commandes avec rating 1 sont plus chères et plus lourdes, et sont souvent retardées.\n- Les commandes avec rating 5 dominent le volume et la valeur.\n- Les livraisons longues sont corrélées à des ratings plus faibles.")

    st.subheader("Recommandations business")
    st.markdown("- Promouvoir les paiements en plusieurs fois pour augmenter le panier moyen.\n- Optimiser la logistique pour réduire les retards et améliorer les ratings.\n- Cibler les segments critiques (commandes chères, ratings faibles) pour améliorer l’expérience client.")
    


