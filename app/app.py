import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pages import sales, rfm_clients, products, geography, cohots, home,clients
from ui.sidebar import render_sidebar

# Affiche la sidebar et récupère la page sélectionnée
page = render_sidebar()

# Page dispatcher
if page == "Accueil":
    home.main()
elif page == "Ventes":
    sales.main()
elif page == "Clients":
    clients.main()
elif page == "RFM":
    rfm_clients.main()
elif page == "Produits":
    products.main()
elif page == "Géographie":
    geography.main()
elif page == "cohots":
    cohots.main()