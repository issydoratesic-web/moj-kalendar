import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import time

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Adora Studio", page_icon="✨", layout="centered")

# --- CSS ZA POZADINU I DIZAJN ---
# NAPOMENA: Zamijeni URL u 'background-image' sa svojom slikom kada je nađeš.
st.markdown("""
    <style>
    .stApp { 
        background-image: url("https://tvoj-link-do-slike.jpg"); 
        background-size: cover;
        background-position: center;
    }
    .stButton>button { 
        width: 100%; 
        border-radius: 20px; 
        background-color: #d4a373; 
        color: white; 
        font-weight: bold; 
        border: none;
    }
    .stButton>button:hover { background-color: #bc8a5f; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        border-radius: 10px;
        border: 1px solid #d4a373;
        background-color: rgba(255, 255, 255, 0.8);
    }
    h1, h2, h3 { color: #5c4a3d; background-color: rgba(255, 255, 255, 0.5); padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCIJE ---
def posalji_discord_obavijest(ime, kontakt, datum, vrijeme, usluga):
    try:
        DISCORD_WEBHOOK = st.secrets["DISCORD_WEBHOOK"]
        data = {
            "content": "🔔 **Nova rezervacija!**",
            "embeds": [{"title": f"👤 Klijent: {ime}", "color": 13935987, "fields": [
                {"name": "✂️ Usluga", "value": usluga, "inline": False},
                {"name": "📱 Kontakt", "value": kontakt, "inline": False},
                {"name": "📅 Datum", "value": datum, "inline": True},
                {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True}]}]
        }
        requests.post(DISCORD_WEBHOOK, json=data)
    except: pass

DB_FILE = "termini.csv"

def ucitaj_termine():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga"])

def spremi_termin(ime, kontakt, datum, vrijeme, usluga):
    df = ucitaj_termine()
    novi_termin = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum, "Vrijeme": vrijeme, "Usluga": usluga}])
    df = pd.concat([df, novi_termin], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- PODACI ---
usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
    "Frizure": ["Kratka kosa", "Duga kosa", "Punđa - 15€"],
    "Ostale usluge": ["Relax zona - 25€"],
    "Little Luxe Spa tretman": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}
frizure_po_duzini = {
    "Kratka kosa": ["Ravnanje kose - 10€", "Uvijanje kose - 20€", "Hollywood valovi - 25€", "Elegantni repovi - 15€"],
    "Duga kosa": ["Ravnanje kose - 20€", "Uvijanje kose - 30€", "Hollywood valovi - 35€", "Elegantni repovi - 25€"]
}

# --- UI ---
st.title("✨ Adora Beauty Concept")
stranica = st.sidebar.radio("Navigacija", ["📅 Rezervacija", "🔐 Admin Panel"])

if stranica == "📅 Rezervacija":
    col1, col2 = st.columns(2)
    with col1: ime = st.text_input("Ime i Prezime:")
    with col2: kontakt = st.text_input("Kontakt (IG/Br):")
    
    kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None, placeholder="Odaberite...")
    
    puna_usluga = None
    if kat:
        if kat == "Frizure":
            odabir = st.selectbox("Odaberite dužinu ili frizuru:", list(usluge_mapa["Frizure"]), index=None, placeholder="Odaberite...")
            if odabir:
                if odabir in frizure_po_duzini:
                    usluga = st.selectbox("Usluga:", frizure_po_duzini[odabir], index=None, placeholder="Odaberite...")
                    if usluga: puna_usluga = f"{kat} -> {odabir} -> {usluga}"
                else: puna_usluga = f"{kat} -> {odabir}"
        else:
            usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None, placeholder="Odaberite...")
            if usluga: puna_usluga = f"{kat} -> {usluga}"
    
    if puna_usluga:
        d_input = st.date_input("Datum:", min_value=datetime.today(), format="DD/MM/YYYY")
        datum_str = d_input.strftime("%d/%m/%Y")
        
        df = ucitaj_termine()
        zauzeti = df[df['Datum'] == datum_str]['Vrijeme'].tolist()
        sva_vremena = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
        dostupna = [v for v in sva_vremena if v not in zauzeti]
        
        if dostupna:
            vrijeme = st.selectbox("Odaberite slobodno vrijeme:", dostupna)
            if st.button("POTVRDI REZERVACIJU"):
                zadnji = st.session_state.get('zadnji_klik', 0)
                if time.time() - zadnji < 10:
                    st.warning("Pričekajte 10 sekundi prije nove rezervacije!")
                elif ime and kontakt:
                    spremi_termin(ime, kontakt, datum_str, vrijeme, puna_usluga)
                    posalji_discord_obavijest(ime, kontakt, datum_str, vrijeme, puna_usluga)
                    st.session_state['zadnji_klik'] = time.time()
                    
                    # POTVRDA (4 sekunde)
                    placeholder = st.empty()
                    placeholder.success("Termin uspješno rezerviran!")
                    time.sleep(4)
                    placeholder.empty()
                    st.rerun()
                else: st.error("Ispunite ime i kontakt.")
        else: st.warning("Nema slobodnih termina za odabrani datum.")

elif stranica == "🔐 Admin Panel":
    lozinka = st.text_input("Lozinka:", type="password")
    if lozinka == st.secrets.get("ADMIN_PASSWORD"):
        st.subheader("📥 Pristigli Termini")
        df = ucitaj_termine()
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🗑️ Brisanje termina")
        if not df.empty:
            df['Display'] = df['Datum'] + " u " + df['Vrijeme'] + " - " + df['Ime']