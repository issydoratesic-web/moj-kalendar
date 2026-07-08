import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- CSS STILOVI ---
st.markdown("""
    <style>
    /* Globalno postavljanje crne boje za sav tekst */
    html, body, [class*="st-"] {
        color: black !important;
    }
    
    .stApp { background-color: #fdfbfb; }
    
    /* Naslovi */
    h1, h2, h3 { color: black !important; text-align: center; }
    
    /* Roza pozadina za polja za unos, s crnim tekstom */
    div[data-baseweb="select"] > div, 
    input, 
    textarea {
        background-color: #fff0f5 !important;
        border: 1px solid #ffb6c1 !important;
        border-radius: 10px !important;
        color: black !important;
    }
    
    /* Tekst unutar izbornika */
    div[data-baseweb="select"] div {
        color: black !important;
    }

    /* Prilagođeni box (napomena) */
    .custom-box { 
        background-color: #fff0f5; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #d63384; 
        color: black !important;
        margin-bottom: 20px;
    }
    
    /* Stil gumba */
    div.stButton > button {
        background-color: #d63384;
        color: white !important; /* Gumb ostaje bijeli tekst radi kontrasta */
        border-radius: 10px;
        width: 100%;
        border: none;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCIJA ZA DISCORD ---
def posalji_na_discord(naslov, ime, usluga, kontakt, detalji):
    webhook_url = "TVOJ_DISCORD_WEBHOOK_URL_OVDJE" 
    embed = {
        "title": naslov,
        "color": 16753920,
        "fields": [
            {"name": "👤 Klijent", "value": ime, "inline": False},
            {"name": "✂️ Usluga", "value": usluga, "inline": False},
            {"name": "📱 Kontakt", "value": kontakt, "inline": False},
            {"name": "📝 Detalji", "value": detalji, "inline": False}
        ]
    }
    data = {"embeds": [embed]}
    try: requests.post(webhook_url, json=data)
    except: pass

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena", "Laminacija_DA_NE", "Alergije"])

# --- ADMIN PANEL ---
with st.sidebar:
    st.header("🔐 Admin Panel")
    if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False
    
    if not st.session_state.admin_auth:
        pwd = st.text_input("Lozinka:", type="password")
        if st.button("Prijava"):
            if pwd == "171102": st.session_state.admin_auth = True; st.rerun()
            else: st.error("Pogrešna lozinka!")
    else:
        if st.button("Odjava"): st.session_state.admin_auth = False; st.rerun()
        st.subheader("Upravljanje terminima")
        df = ucitaj_termine()
        for idx, row in df.iterrows():
            with st.expander(f"{row['Ime']} - {row['Datum']}"):
                st.write(f"Usluga: {row['Usluga']}")
                if st.button(f"OBRIŠI {row['Ime']}", key=f"del_{idx}"):
                    posalji_na_discord("❌ Termin otkazan", row['Ime'], row['Usluga'], row['Kontakt'], "Uklonjeno iz sustava.")
                    df.drop(idx).to_csv("termini.csv", index=False)
                    st.rerun()

# --- GLAVNI UI ---
st.title("✨ Adora Beauty Concept")
st.markdown("""<div class='custom-box'><strong>Napomena:</strong><br>• Otkazivanje termina min. 24h ranije.<br>• Šminkanje: obavezna akontacija 50%.<br>IBAN: HR03 2402 0061 1406 1395 3</div>""", unsafe_allow_html=True)

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")

kat = st.selectbox("Odaberite kategoriju:", ["Šminkanje", "Oblikovanje i korekcija obrva", "Tretmani lica", "Frizure", "Little Luxe Spa"], index=None)

usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
    "Frizure": ["Kratka kosa - Ravnanje - 10€", "Duga kosa - Uvijanje - 30€"],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        st.subheader("Dodatna pitanja")
        novi_klijent = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None)
        napomena = st.text_area("Napomena:")
        
        c1, c2, c3 = st.columns(3)
        dan = c1.selectbox("Dan:", [f"{
