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

# Definiramo mape s cijenama
usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
    "Frizure": ["Ravnanje kose", "Uvijanje kose", "Hollywood valovi", "Elegantni repovi", "Punđa - 15€"],
    "Ostale usluge": ["Relax zona - 25€"],
    "Little Luxe Spa tretman": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

if stranica == "Rezerviraj Termin":
    st.title("📅 Adora Beauty Concept")
    
    ime = st.text_input("Ime i Prezime:")
    kontakt = st.text_input("Kontakt (Instagram/Broj):")
    
    kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()))
    usluga = st.selectbox("Odaberite uslugu:", usluge_mapa[kat])
    
    # Logika za frizure: ako je odabrana frizura, pitamo za dužinu
    prikaz_usluge = usluga
    if kat == "Frizure" and usluga in ["Ravnanje kose", "Uvijanje kose", "Hollywood valovi", "Elegantni repovi"]:
        duzina = st.radio("Odaberite dužinu kose:", ["Kratka kosa", "Duga kosa"])
        # Definicija cijena po dužini
        cijene = {
            "Ravnanje kose": {"Kratka kosa": "10€", "Duga kosa": "20€"},
            "Uvijanje kose": {"Kratka kosa": "20€", "Duga kosa": "30€"},
            "Hollywood valovi": {"Kratka kosa": "25€", "Duga kosa": "35€"},
            "Elegantni repovi": {"Kratka kosa": "15€", "Duga kosa": "25€"}
        }
        odabrana_cijena = cijene[usluga][duzina]
        prikaz_usluge = f"{usluga} ({duzina} - {odabrana_cijena})"

    datum = st.date_input("Datum:", min_value=datetime.today().date())
    vremena = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
    vrijeme = st.selectbox("Vrijeme:", vremena)
    
    if st.button("Rezerviraj"):
        if ime and kontakt:
            puna_info = f"{kat} -> {prikaz_usluge}"
            spremi_termin(ime, kontakt, datum, vrijeme, puna_info)
            posalji_discord_obavijest(ime, kontakt, datum, vrijeme, puna_info)
            st.success("Termin uspješno rezerviran!")
            st.rerun()
        else:
            st.error("Molimo ispunite ime i kontakt.")

elif stranica == "Admin Panel":
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