import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests

# --- DISCORD FUNKCIJA ---
def posalji_discord_obavijest(ime, kontakt, datum, vrijeme, usluga):
    try:
        DISCORD_WEBHOOK = st.secrets["DISCORD_WEBHOOK"]
    except:
        return

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

# --- BAZA PODATAKA ---
DB_FILE = "termini.csv"

def ucitaj_termine():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Status"])

def spremi_termin(ime, kontakt, datum, vrijeme, usluga):
    df = ucitaj_termine()
    novi_termin = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": str(datum), "Vrijeme": vrijeme, "Usluga": usluga, "Status": "Na cekanju"}])
    df = pd.concat([df, novi_termin], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

# --- GLAVNI PROGRAM ---
st.set_page_config(page_title="Rezervacija", layout="centered")
stranica = st.sidebar.radio("Navigacija", ["Rezerviraj Termin", "Admin Panel"])

if stranica == "Rezerviraj Termin":
    st.title("📅 Rezervirajte termin")
    
    with st.form("rezervacija_forma", clear_on_submit=True):
        ime = st.text_input("Ime i Prezime:")
        kontakt = st.text_input("Kontakt (Instagram/Broj):")
        
        # Ovdje su tvoje nove kategorije:
        kategorije = [
            "Šminkanje", "Terensko šminkanje", "Oblikovanje obrva pincetom", 
            "Oblikovanje i bojanje obrva", "Brow lift", "Brow lift i bojanje", 
            "Enzimski piling", "Blagi mehanički piling", 
            "Parenje toplim ručnikom i masaža uz piling", "Ravnanje kose", 
            "Uvijanje kose", "Hollywood valovi", "Elegantni repovi", 
            "Punđa", "Relax zona", "Little Luxe Spa tretman"
        ]
        usluga = st.selectbox("Odaberite uslugu:", kategorije)
        
        datum = st.date_input("Datum:", min_value=datetime.today().date())
        vremena = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"]
        vrijeme = st.selectbox("Vrijeme:", vremena)
        
        if st.form_submit_button("Rezerviraj"):
            if ime and kontakt:
                spremi_termin(ime, kontakt, datum, vrijeme, usluga)
                posalji_discord_obavijest(ime, kontakt, datum, vrijeme, usluga)
                st.success("Uspješno poslano!")
            else:
                st.error("Molimo unesite ime i kontakt.")

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