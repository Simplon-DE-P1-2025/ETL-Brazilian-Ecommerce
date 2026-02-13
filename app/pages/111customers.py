import streamlit as st
from src.loaders.postgres_loader import PostgresLoader
from kpi_queries import COHORT_LTV_QUERY





def main():
    st.title("Analyse clients 🔍")
    postgres_loader = PostgresLoader()
    df_cohort = postgres_loader.execute_query(COHORT_LTV_QUERY)
    st.subheader("Lifetime Value par cohorte")
    # Line chart for LTV par cohorte
    seriesLineChart = [{
        "type": 'Line',
        "data": [
            {"time": str(row["cohort_month"]), "value": row["avg_ltv"]}
            for _, row in df_cohort.iterrows()
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
    from streamlit_lightweight_charts import renderLightweightCharts
    renderLightweightCharts([
        {
            "chart": chartOptions,
            "series": seriesLineChart
        }
    ], 'ltv_cohort')
    st.subheader("Table clients (AGGrid)")
    # Table fallback (AGGrid removed for lightweight-charts focus)
    st.dataframe(df_cohort)
    

