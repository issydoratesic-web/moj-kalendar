import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests

# --- DISCORD FUNKCIJA ---
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
    except:
        pass

# --- BAZA PODATAKA ---
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

# Mape bez cijena u nazivu
usluge_mapa = {
    "Šminkanje": ["Šminkanje", "Terensko šminkanje"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom", "Oblikovanje i bojanje obrva", "Brow lift", "Brow lift i bojanje"],
    "Tretmani lica": ["Enzimski piling", "Blagi mehanički piling", "Parenje toplim ručnikom i masaža uz piling"],
    "Frizure": ["Ravnanje kose", "Uvijanje kose", "Hollywood valovi", "Elegantni repovi", "Punđa"],
    "Ostale usluge": ["Relax zona"],
    "Little Luxe Spa tretman": ["Mini", "Classic", "VIP"]
}

# Cjenik za sve usluge
cijene_detaljno = {
    "Šminkanje": "40€", "Terensko šminkanje": "50€",
    "Oblikovanje obrva pincetom": "8€", "Oblikovanje i bojanje obrva": "15€", "Brow lift": "30€", "Brow lift i bojanje": "35€",
    "Enzimski piling": "25€", "Blagi mehanički piling": "20€", "Parenje toplim ručnikom i masaža uz piling": "35€",
    "Punđa": "15€", "Relax zona": "25€",
    "Mini": "50€", "Classic": "70€", "VIP": "100€",
    # Posebne cijene za frizure
    "Ravnanje kose": {"Kratka kosa": "10€", "Duga kosa": "20€"},
    "Uvijanje kose": {"Kratka kosa": "20€", "Duga kosa": "30€"},
    "Hollywood valovi": {"Kratka kosa": "25€", "Duga kosa": "35€"},
    "Elegantni repovi": {"Kratka kosa": "15€", "Duga kosa": "25€"}
}

if stranica == "Rezerviraj Termin":
    st.title("📅 Adora Beauty Concept")
    
    ime = st.text_input("Ime i Prezime:")
    kontakt = st.text_input("Kontakt (Instagram/Broj):")
    
    kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()))
    usluga = st.selectbox("Odaberite uslugu:", usluge_mapa[kat])
    
    puna_info = usluga
    
    # Logika za frizure - dodaje cijenu tek nakon odabira dužine
    if kat == "Frizure" and usluga in ["Ravnanje kose", "Uvijanje kose", "Hollywood valovi", "Elegantni repovi"]:
        duzina = st.radio("Odaberite dužinu kose:", ["Kratka kosa", "Duga kosa"])
        cijena = cijene_detaljno[usluga][duzina]
        puna_info = f"{usluga} ({duzina} - {cijena})"
    else:
        # Za ostale usluge, dohvati fiksnu cijenu
        cijena = cijene_detaljno.get(usluga, "")
        puna_info = f"{usluga} - {cijena}"

    datum = st.date_input("Datum:", min_value=datetime.today().date())
    vremena = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
    vrijeme = st.selectbox("Vrijeme:", vremena)
    
    if st.button("Rezerviraj"):
        if ime and kontakt:
            zapis = f"{kat} -> {puna_info}"
            spremi_termin(ime, kontakt, datum, vrijeme, zapis)
            posalji_discord_obavijest(ime, kontakt, datum, vrijeme, zapis)
            st.success("Termin uspješno rezerviran!")
            st.rerun()
        else:
            st.error("Molimo ispunite ime i kontakt.")

elif stranica == "Admin Panel":
    # ... (ostatak admin panela ostaje isti)
    st.title("🔐 Admin Pristup")
    lozinka = st.text_input("Lozinka:", type="password")
    if lozinka == st.secrets.get("ADMIN_PASSWORD"):
        st.title("📥 Pristigli Termini")
        df = ucitaj_termine()
        st.dataframe(df, use_container_width=True)
        if st.button("⚠️ Obriši sve termine"):
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
                st.rerun()
    elif lozinka:
        st.error("Pogrešna lozinka!")