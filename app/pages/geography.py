import streamlit as st
from src.loaders.postgres_loader import PostgresLoader
from kpi_gold_queries import GEO_STATE_METRICS_QUERY, RETENTION_STATE_QUERY, STATE_PAYMENT_EVOLUTION_QUERY
import plotly.express as px
import json
import urllib.request

def main():
    st.title("🗺️ Analyse géographique des ventes & performances")
    postgres_loader = PostgresLoader()

    df_geo = postgres_loader.execute_query(GEO_STATE_METRICS_QUERY)

    # --- Metrics cards ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("CA total", f"{df_geo['total_payment'].sum():,.0f} €")
    with col2:
        st.metric("Commandes", int(df_geo['total_orders'].sum()))
    with col3:
        st.metric("Moyenne retard livraison", f"{df_geo['avg_delivery_delay_days'].mean():.1f} j")
    with col4:
        st.metric("Nombre reviews", int(df_geo['total_reviews'].sum()))

    metrics_labels = {
        'total_orders': "Nombre de commandes",
        'total_payment': "Chiffre d'affaires (€)",
        'total_payment_per_thousand_person': "CA / Mille habitants",
        'orders_per_thousand_person': "Commandes / Mille habitants",
        'avg_review_score': "Score moyen des avis",
        'total_reviews': "Nombre d'avis",
        'avg_delivery_delay_days': "Retard moyen de livraison (j)",
        'aov': "Panier moyen (€)",
        'avg_order_weight_kg': "Poids moyen (kg)",
        'avg_order_volume_cm3': "Volume moyen (cm³)",
        'cancel_rate': "% d'annulation",
        'installment_orders_rate': "% commandes en plusieurs fois"
    }
    list_metrics = list(metrics_labels.keys())
    metric_selected_label = st.selectbox("Métrique pour la carte", [metrics_labels[m] for m in list_metrics], index=1)
    metric_selected = list_metrics[[metrics_labels[m] for m in list_metrics].index(metric_selected_label)]

    labels_for_map = {
        'customer_state_short': "État",
        'total_orders': "Nb commandes",
        'total_payment': "CA (€)",
        'total_payment_per_thousand_person': "CA / Mille hab.",
        'orders_per_thousand_person': "Cmds / Mille hab.",
        'avg_review_score': "Score moyen review",
        'total_reviews': "Nb reviews",
        'avg_delivery_delay_days': "Retard moyen (j)",
        'avg_delivery_time_days': "Delai moyen (j)",
        'aov': "Panier moyen (€)",
        'avg_order_weight_kg': "Poids moyen (kg)",
        'avg_order_volume_cm3': "Volume moyen (cm³)",
        'cancel_rate': "% annulation",
        'installment_orders_rate': "% commandes en plusieurs fois"
    }

    # --- Map plotting pastel ---
    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    with urllib.request.urlopen(geojson_url) as response:
        geojson = json.load(response)

    fig_map = px.choropleth(
        df_geo,
        geojson=geojson,
        locations='customer_state_short',
        featureidkey="properties.sigla",
        color=metric_selected,
        color_continuous_scale="Mint",  # Pastel palette
        labels=labels_for_map,
        title=f"{labels_for_map.get(metric_selected, metric_selected)} par état"
    )
    fig_map.update_geos(
        visible=False,
        lataxis_range=[-40.7, 7.3],
        lonaxis_range=[-85, -34.5],
        projection_scale=1.2,
        center=dict(lat=-15, lon=-55)
    )
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, width=650, height=500)
    st.plotly_chart(fig_map, use_container_width=True)

    # --- Bar chart Top 5 états ---
    st.subheader(f"Top 5 états sur la métrique : {labels_for_map.get(metric_selected, metric_selected)}")
    top_states = df_geo.sort_values(metric_selected, ascending=False).head(5)
    fig_bar = px.bar(
        top_states,
        x='customer_state_short',
        y=metric_selected,
        color='customer_state_short',
        text=metric_selected,
        labels=labels_for_map,
        title=f"Top 5 états - {labels_for_map.get(metric_selected, metric_selected)}",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_bar.update_layout(width=600, height=330, margin={"r":0,"t":40,"l":0,"b":0}, plot_bgcolor="#fafafa")
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Pie chart CA par région ---
    st.subheader("Répartition du CA par région")
    if 'region_name' in df_geo.columns:
        fig_pie = px.pie(
            df_geo,
            values='total_payment',
            names='region_name',
            color='region_name',
            labels={'region_name': 'Région', 'total_payment': 'CA (€)'},
            title="Part du chiffre d'affaires par région",
            color_discrete_sequence=px.colors.qualitative.Pastel2
        )
        fig_pie.update_layout(width=400, height=340)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- Table detail ---
    st.markdown("### Détail par état")
    st.dataframe(df_geo)

    # --- Retention M1 (Bonus card/map) ---
    st.subheader("Rétention M1 par état")
    st.markdown("""
    <span style='color:#555'><b>La rétention M1 par état</b> indique le pourcentage de clients qui passent une nouvelle commande dans le mois suivant leur première commande, pour chaque état brésilien.<br>
    Plus ce taux est élevé, plus les clients sont fidèles et reviennent rapidement.<br>
    C'est un indicateur clé de la fidélisation régionale, utile pour piloter des actions marketing ciblées.</span>
    """, unsafe_allow_html=True)
    df_retention = postgres_loader.execute_query(RETENTION_STATE_QUERY)
    if 'customer_state_short' in df_retention.columns and 'retention_1st_month_state' in df_retention.columns:
        fig_ret = px.choropleth(
            df_retention,
            geojson=geojson,
            locations='customer_state_short',
            featureidkey="properties.sigla",
            color='retention_1st_month_state',
            color_continuous_scale="Pinkyl",
            labels={'retention_1st_month_state': "Rétention clients M1"},
            title="Rétention 1er mois par état"
        )
        fig_ret.update_geos(visible=False, projection_scale=1.2, center=dict(lat=-15, lon=-55))
        fig_ret.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, width=650, height=500)
        st.plotly_chart(fig_ret, use_container_width=True)
    else:
        st.write(df_retention)

    # --- Evolution CA par état ---
    st.subheader("Évolution CA par état")
    df_state_payment = postgres_loader.execute_query(STATE_PAYMENT_EVOLUTION_QUERY)
    state_list = df_state_payment['customer_state_short'].unique().tolist()
    state_choice = st.selectbox("Choix de l'état pour évolution :", state_list)
    if state_choice and 'year_month' in df_state_payment.columns:
        df_state_plot = df_state_payment[df_state_payment['customer_state_short'] == state_choice]
        fig_state = px.line(
            df_state_plot,
            x='year_month', y='total_payment',
            markers=True,
            title=f"Évolution CA - {state_choice}",
            labels={"year_month": "Mois", "total_payment": "CA (€)"}
        )
        st.plotly_chart(fig_state, use_container_width=True)
    else:
        st.write(df_state_payment)

if __name__ == "__main__":
    main()