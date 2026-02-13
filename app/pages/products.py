import streamlit as st
from src.loaders.postgres_loader import PostgresLoader
from kpi_queries import TOP_PRODUCTS_QUERY
from streamlit_lightweight_charts import renderLightweightCharts
import plotly.express as px


def main():
    st.subheader("Top 10 Produits (Streamlit natif)")
    # Charger les données depuis Postgres
    postgres_loader = PostgresLoader()
    df = postgres_loader.execute_query(TOP_PRODUCTS_QUERY)
    if df is not None and 'product_id' in df.columns and 'total_revenue' in df.columns:
        df_top10 = df.sort_values("total_revenue", ascending=False).head(10)
        df_top10 = df_top10.set_index("product_id")
        st.bar_chart(df_top10["total_revenue"])
    else:
        st.warning("Colonnes 'product_id' ou 'total_revenue' absentes des données. Voici le DataFrame:")
        st.write(df)

    # Bar chart pour Top 10 Produits
    seriesBarChart = [{
        "type": 'Bar',
        "data": [
            {"time": str(row["product_id"]),
             "open": 0,
             "high": row["total_revenue"],
             "low": 0,
             "close": row["total_revenue"]}
            for _, row in df.iterrows()
        ],
        "options": {
            "upColor": '#26a69a',
            "downColor": '#ef5350'
        }
    }]

    chartOptions = {
        "layout": {
            "textColor": 'black',
            "background": {"type": 'solid', "color": 'white'}
        }
    }
    st.set_page_config(layout="wide") 
    col1, col2 = st.columns([3, 2]) 
    with col1:
        
        st.markdown(
            "<h1 style='font-size:32px;'>🏆 Top 10 produits</h1>",
            unsafe_allow_html=True)
        # Bar chart horizontal Plotly
        fig = px.bar(
            df.sort_values('total_revenue', ascending=True),  # bars du plus petit au plus grand
            y='product_id',
            x='total_revenue',
            color='category',
            orientation='h',
            text='total_units_sold',
            title='Top 10 produits par chiffre d\'affaires',
            labels={
                'total_revenue': 'Chiffre d\'affaires (€)',
                'product_id': 'Produit',
                'category': 'Catégorie',
                'total_units_sold': "Unités vendues"
            }
        )
        fig.update_traces(texttemplate='%{text} unités', textposition='outside')
        fig.update_layout(
            yaxis=dict(title=''),
            xaxis=dict(title='Chiffre d\'affaires (€)'),
            legend_title_text='Catégorie',
            plot_bgcolor='rgba(0,0,0,0)',
            
            
        )
        fig.update_layout(margin=dict(l=80, r=20, t=60, b=40))

        st.plotly_chart(fig, use_container_width=True)
    
    
    with col2:
        
        fig = px.scatter(
        df,
        x='avg_price',
        y='total_revenue',
        color='category',
        size='total_units_sold',
        hover_data=['product_id', 'category', 'total_units_sold'],
        labels={
            'avg_price': 'Prix moyen (€)',
            'total_revenue': 'Chiffre d\'affaires (€)',
            'category': 'Catégorie',
            'total_units_sold': 'Unités vendues'
        },
        title='Corrélation prix moyen / chiffre d\'affaires des produits'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title='Prix moyen (€)',
            yaxis_title='Chiffre d\'affaires (€)',
            legend_title_text='Catégorie',
            margin=dict(l=40, r=40, t=60, b=40)
        )
        
        fig.update_layout(margin=dict(l=80, r=20, t=60, b=40))
        st.markdown(
            "<h1 style='font-size:26px;'>💵 Corrélation : prix moyen et CA </h1>",
            unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        
    
    
    



