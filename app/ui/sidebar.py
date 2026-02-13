import streamlit as st
from streamlit_option_menu import option_menu

def render_sidebar(page_name=None):
    """
    Affiche le menu latéral et retourne le label de la page sélectionnée.
    """
    with st.sidebar:
        key = f"sidebar_menu_{page_name or 'main'}"
        selected = option_menu(
            "Navigation",
            [
                "Accueil",
                "Ventes",
                "Clients",
                "RFM",
                "Produits",
                "Géographie",
                "Cohortes",
            ],
            icons=[
                'house',
                'graph-up',
                'people',
                'diagram-3',
                'box',
                'map',
                'bar-chart',
            ],
            menu_icon="cast",
            default_index=0,
            key=key
        )
    return selected