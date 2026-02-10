import pandas as pd
from typing import Dict
from sqlalchemy import create_engine, text
from config.settings import DB_CONFIG, CHUNK_SIZE


class PostgresLoader:
    # chargement des dataframes dans postgresql par schéma

    def __init__(self):
        conn_string = (
            f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        self.engine = create_engine(conn_string)

    def _ensure_schema(self, schema: str):
        with self.engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
            conn.commit()

    def load_layer(self, data: Dict[str, pd.DataFrame], schema: str, if_exists: str = 'replace'):
        # charge tous les dataframes d'une couche dans le schéma correspondant
        self._ensure_schema(schema)
        for table_name, df in data.items():
            df.to_sql(
                name=table_name,
                con=self.engine,
                schema=schema,
                if_exists=if_exists,
                index=False,
                method='multi',
                chunksize=CHUNK_SIZE
            )

    def execute_sql_file(self, filepath: str):
        # exécute un fichier SQL statement par statement
        with open(filepath, 'r') as f:
            sql = f.read()
        with self.engine.connect() as conn:
            for statement in sql.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
            conn.commit()
