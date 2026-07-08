import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- CSS STILOVI ---
st.markdown("""
    <style>
    /* 1. Pozadina stranice */
    .stApp { background-color: #fff0f5 !important; }

    /* 2. SAMO NASLOV - Luksuzni font, bez emojija */
    .simple-luxury-title {
        color: #d63384 !important;
        font-family: 'Georgia', 'Playfair Display', serif !important;
        font-size: 40px !important;
        font-weight: 500 !important;
        text-align: center !important;
        letter-spacing: 3px !important;
        text-transform: uppercase !important;
        margin-top: 20px;
        margin-bottom: 40px;
    }

    /* 3. POLJA ZA UNOS */
    div[data-baseweb="base-input"], div[data-baseweb="select"] > div, input, textarea {
        background-color: #ffffff !important;
        color: black !important;
        border: 1px solid #ffb6c1 !important;
        border-radius: 0px !important; 
    }

    /* 4. PADAJUĆI IZBORNICI */
    div[role="listbox"], ul[role="listbox"], li[role="option"] {
        background-color: #fff0f5 !important;
        color: black !important;
    }
    
    li[role="option"]:hover {
        background-color: #ffc0cb !important;
    }

    /* 5. GUMBI */
    div.stButton > button {
        background-color: #d63384 !important;
        color: white !important;
        border-radius: 0px !important;
        border: none !important;
        font-family: 'Georgia', serif !important;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NASLOV ---
st.markdown("<h1 class='simple-luxury-title'>ADORA BEAUTY CONCEPT</h1>", unsafe_allow_html=True)

# --- OSTATAK APLIKACIJE (OVDJE IDE TVOJ KOD ZA FORMU) ---
# ... (nastavi s ostatkom koda kao i do sada)
