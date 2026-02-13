import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from loguru import logger
from src.bronze.csv_extractor import BronzeExtractor
from src.silver.processor import SilverProcessor
from src.gold.aggregator import GoldAggregator
from src.loaders.postgres_loader import PostgresLoader
from config.settings import SQL_DIR


def main():
    # pipeline ETL : bronze -> silver -> gold -> postgres
    logger.info("="*60)
    logger.info("DÉMARRAGE PIPELINE ETL")
    logger.info("="*60)

    # bronze : extraction des CSV bruts
    logger.info("\nExtraction des données brutes:")
    extractor = BronzeExtractor()
    bronze_data = extractor.extract_all()
    logger.info(f"  {len(bronze_data)} datasets extraits")

    # silver : nettoyage et validation
    logger.info("\nNettoyage des données:")
    processor = SilverProcessor()
    silver_data = processor.process(bronze_data)
    logger.info(f"  {len(silver_data)} datasets nettoyés")

    # gold : agrégations métier
    logger.info("\nCréation des tables business:")
    aggregator = GoldAggregator(silver_data)
    gold_data = aggregator.aggregate()
    logger.info(f"{len(gold_data)} tables Gold créées")

    # chargement dans postgres par couche
    logger.info("\nChargement dans PostgreSQL")
    loader = PostgresLoader()

    loader.load_layer(bronze_data, schema='bronze')
    logger.info("  Bronze layer chargée")

    loader.load_layer(silver_data, schema='silver')
    logger.info("  Silver layer chargée")

    loader.load_layer(gold_data, schema='gold')
    logger.info("  Gold layer chargée")

    # création des index pour la performance
    logger.info("\nCréation des index...")
    loader.execute_sql_file(SQL_DIR / "create_indexes.sql")
    logger.info("  Index créés")

    logger.info("\n" + "="*60)
    logger.info("PIPELINE TERMINÉ AVEC SUCCÈS")
    logger.info("="*60)


if __name__ == "__main__":
    main()
