import streamlit as st
from src.loaders.postgres_loader import PostgresLoader
from kpi_queries import COHORT_LTV_QUERY
from streamlit_lightweight_charts import renderLightweightCharts

def main():
    postgres_loader = PostgresLoader()
    st.title("Lifetime Value par cohorte 📊")

    df = postgres_loader.execute_query(COHORT_LTV_QUERY)

    # Préparation des données pour le chart
    seriesLineChart = [{
        "type": 'Line',
        "data": [
            {"time": str(row["cohort_month"]), "value": row["avg_ltv"]}
            for _, row in df.iterrows()
        ],
        "options": {}
    }]
    chartOptions = {
        "layout": {
            "textColor": 'black',
            "background": {
                "type": 'solid',
                "color": 'white'
            }
        }
    }

    st.subheader("Lifetime Value par cohorte (interactive)")
    renderLightweightCharts([
        {
            "chart": chartOptions,
            "series": seriesLineChart
        }
    ], 'cohort_ltv_line')

    st.table(df)