import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

SQL_DIR = BASE_DIR / "sql"

for directory in [RAW_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "brazilian_ecommerce"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# Taille des lots pour l'insertion en base
CHUNK_SIZE = 10000

CSV_FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "payments": "olist_order_payments_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}

STATES = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
    'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
    'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
]

REGION_MAPPING = {
    'AC': 'Norte', 'AP': 'Norte', 'AM': 'Norte', 'PA': 'Norte',
    'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
    'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste',
    'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
    'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste',
    'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
    'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul',
}

POPULATION = {
    'AC': 869265, 'AL': 3322820, 'AP': 829494, 'AM': 4080611,
    'BA': 14812617, 'CE': 9075649, 'DF': 3974703, 'ES': 3972388,
    'GO': 6921161, 'MA': 7035055, 'MT': 3441998, 'MS': 2748023,
    'MG': 21040662, 'PA': 8513497, 'PB': 3996496, 'PR': 11348937,
    'PE': 9496294, 'PI': 3264531, 'RJ': 17159960, 'RN': 3479010,
    'RS': 11329605, 'RO': 1757589, 'RR': 576568, 'SC': 7075494,
    'SP': 45538936, 'SE': 2278308, 'TO': 1555229
}

# Noms complets des états brésiliens
STATE_NAMES = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AM': 'Amazonas', 'AP': 'Amapa',
    'BA': 'Bahia', 'CE': 'Ceara', 'DF': 'Distrito Federal', 'ES': 'Espirito Santo',
    'GO': 'Goias', 'MA': 'Maranhao', 'MG': 'Minas Gerais', 'MS': 'Mato Grosso do Sul',
    'MT': 'Mato Grosso', 'PA': 'Para', 'PB': 'Paraiba', 'PE': 'Pernambuco',
    'PI': 'Piaui', 'PR': 'Parana', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
    'RO': 'Rondonia', 'RR': 'Roraima', 'RS': 'Rio Grande do Sul', 'SC': 'Santa Catarina',
    'SE': 'Sergipe', 'SP': 'Sao Paulo', 'TO': 'Tocantins'
}

# Mapping des catégories vers groupes généraux
CATEGORY_MAPPING = {
    'furniture': [
        'office_furniture', 'furniture_decor', 'bed_bath_table', 
        'furniture_living_room', 'furniture_bedroom', 'furniture_mattress_and_upholstery',
        'kitchen_dining_laundry_garden_furniture', 'la_cuisine'
    ],
    'electronics': [
        'computers_accessories', 'telephony', 'electronics', 'pc_gamer',
        'audio', 'tablets_printing_image', 'computers', 'small_appliances',
        'small_appliances_home_oven_and_coffee', 'air_conditioning',
        'home_appliances', 'home_appliances_2', 'portable_kitchen_food_processors',
        'signaling_and_security', 'security_and_services', 'fixed_telephony'
    ],
    'fashion': [
        'fashion_female_clothing', 'fashion_male_clothing', 'fashion_shoes',
        'fashion_bags_accessories', 'fashion_underwear_beach', 'fashion_sport',
        'fashion_childrens_clothes', 'fashio_female_clothing', 'luggage_accessories',
        'watches_gifts', 'cool_stuff'
    ],
    'home_garden': [
        'housewares', 'garden_tools', 'pet_shop', 'flowers', 'home_confort',
        'home_comfort_2', 'home_construction', 'construction_tools_construction',
        'construction_tools_lights', 'construction_tools_garden', 
        'construction_tools_safety', 'costruction_tools_tools', 'costruction_tools_garden'
    ],
    'entertainment': [
        'sports_leisure', 'toys', 'music', 'cds_dvds_musicals', 'dvds_blu_ray',
        'musical_instruments', 'consoles_games', 'party_supplies', 'christmas_supplies',
        'arts_and_craftmanship', 'art'
    ],
    'beauty_health': [
        'health_beauty', 'perfumery', 'diapers_and_hygiene', 'baby', 
        'market_place'
    ],
    'food_drinks': [
        'food_drink', 'drinks', 'food', 'agro_industry_and_commerce'
    ],
    'books_stationery': [
        'books_general_interest', 'stationery', 'books_technical', 
        'books_imported', 'cine_photo'
    ],
    'auto': [
        'auto', 'industry_commerce_and_business'
    ],
    'other': []  # Catégorie par défaut
}
