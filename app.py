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

if stranica == "Rezerviraj Termin":
    st.title("📅 Adora Beauty Concept")
    
    # Rječnik kategorija i usluga
    usluge_mapa = {
        "Šminkanje": ["Šminkanje", "Terensko šminkanje"],
        "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom", "Oblikovanje i bojanje obrva", "Brow lift", "Brow lift i bojanje"],
        "Tretmani lica": ["Enzimski piling", "Blagi mehanički piling", "Parenje toplim ručnikom i masaža uz piling"],
        "Frizure": ["Ravnanje kose", "Uvijanje kose", "Hollywood valovi", "Elegantni repovi", "Punđa"],
        "Ostale usluge": ["Relax zona"],
        "Little Luxe Spa tretman": ["Mini", "Classic", "VIP"]
    }

    with st.form("rezervacija_forma", clear_on_submit=True):
        ime = st.text_input("Ime i Prezime:")
        kontakt = st.text_input("Kontakt (Instagram/Broj):")
        
        kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()))
        usluga = st.selectbox("Odaberite uslugu:", usluge_mapa[kat])
        
        datum = st.date_input("Datum:", min_value=datetime.today().date())
        vremena = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
        vrijeme = st.selectbox("Vrijeme:", vremena)
        
        if st.form_submit_button("Rezerviraj"):
            if ime and kontakt:
                puna_usluga = f"{kat} - {usluga}"
                spremi_termin(ime, kontakt, datum, vrijeme, puna_usluga)
                posalji_discord_obavijest(ime, kontakt, datum, vrijeme, puna_usluga)
                st.success("Termin uspješno rezerviran!")
            else:
                st.error("Molimo ispunite sva polja.")

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