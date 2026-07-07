import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests

# --- FUNKCIJE (ostaju iste) ---
def posalji_discord_obavijest(ime, kontakt, datum, vrijeme, usluga):
    try:
        DISCORD_WEBHOOK = st.secrets["DISCORD_WEBHOOK"]
        data = {
            "content": "🔔 **Nova rezervacija!**",
            "embeds": [{
                "title": f"👤 Klijent: {ime}",
                "color": 15418782,
                "fields": [
                    {"name": "✂️ Usluga", "value": usluga, "inline": False},
                    {"name": "📱 Kontakt", "value": kontakt, "inline": False},
                    {"name": "📅 Datum", "value": str(datum), "inline": True},
                    {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True}
                ]
            }]
        }
        requests.post(DISCORD_WEBHOOK, json=data)
    except: pass

DB_FILE = "termini.csv"
def ucitaj_termine():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Status"])

def spremi_termin(ime, kontakt, datum, vrijeme, usluga):
    df = ucitaj_termine()
    novi_termin = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": str(datum), "Vrijeme": vrijeme, "Usluga": usluga, "Status": "Na cekanju"}])
    df = pd.concat([df, novi_termin], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- GLAVNI PROGRAM ---
st.set_page_config(page_title="Adora Rezervacije", layout="centered")
stranica = st.sidebar.radio("Navigacija", ["Rezerviraj Termin", "Admin Panel"])

usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
    "Frizure": ["Kratka kosa", "Duga kosa", "Punđa - 15€"], # Punđa je sada ovdje
    "Ostale usluge": ["Relax zona - 25€"],
    "Little Luxe Spa tretman": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

frizure_po_duzini = {
    "Kratka kosa": ["Ravnanje kose - 10€", "Uvijanje kose - 20€", "Hollywood valovi - 25€", "Elegantni repovi - 15€"],
    "Duga kosa": ["Ravnanje kose - 20€", "Uvijanje kose - 30€", "Hollywood valovi - 35€", "Elegantni repovi - 25€"]
}

if stranica == "Rezerviraj Termin":
    st.title("📅 Adora Beauty Concept")
    ime = st.text_input("Ime i Prezime:")
    kontakt = st.text_input("Kontakt (Instagram/Broj):")
    kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()))
    
    if kat == "Frizure":
        odabir_duzine = st.selectbox("Odaberite dužinu ili frizuru:", list(usluge_mapa["Frizure"]))
        
        # Ako je odabrana dužina, otvaramo drugi izbornik za usluge
        if odabir_duzine in frizure_po_duzini:
            usluga = st.selectbox("Odaberite uslugu:", frizure_po_duzini[odabir_duzine])
            puna_usluga = f"{kat} -> {odabir_duzine} -> {usluga}"
        else:
            # Ako je odabrana Punđa
            puna_usluga = f"{kat} -> {odabir_duzine}"
    else:
        usluga = st.selectbox("Odaberite uslugu:", usluge_mapa[kat])
        puna_usluga = f"{kat} -> {usluga}"
    
    # Zamijeni svoj postojeći redak za datum ovim:
datum = st.date_input("Datum:", min_value=datetime.today().date(), format="DD/MM/YYYY")
    vremena = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
    vrijeme = st.selectbox("Vrijeme:", vremena)
    
    if st.button("Rezerviraj"):
        if ime and kontakt:
            spremi_termin(ime, kontakt, datum, vrijeme, puna_usluga)
            posalji_discord_obavijest(ime, kontakt, datum, vrijeme, puna_usluga)
            st.success("Termin uspješno rezerviran!")
            st.rerun()
        else: st.error("Molimo ispunite ime i kontakt.")

# ... (ostatak koda za Admin panel ostaje isti)