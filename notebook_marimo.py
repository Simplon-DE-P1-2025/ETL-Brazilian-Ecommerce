import marimo

__generated_with = "0.19.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from src.loaders.postgres_loader import PostgresLoader

    return (PostgresLoader,)


@app.cell
def _(PostgresLoader):
    postgresloader = PostgresLoader() 

    return (postgresloader,)


@app.cell(hide_code=True)
def _(postgresloader):
    _query = """
    SELECT 
    * 
    FROM gold.dim_customers
    """
    df = postgresloader.execute_query(_query)
    df
    return


@app.cell
def _():
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        SELECT * FROM
        """
    )
    return


if __name__ == "__main__":
    app.run()
