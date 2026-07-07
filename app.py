import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import requests
import time

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Adora Studio", page_icon="✂️", layout="centered")

# --- FUNKCIJE ---
DB_FILE = "termini.csv"

def posalji_discord_obavijest(ime, kontakt, datum, vrijeme, usluga):
    try:
        DISCORD_WEBHOOK = st.secrets["DISCORD_WEBHOOK"]
        data = {
            "content": "🔔 **Nova rezervacija!**",
            "embeds": [{"title": f"👤 Klijent: {ime}", "color": 15418782, "fields": [
                {"name": "✂️ Usluga", "value": usluga, "inline": False},
                {"name": "📱 Kontakt", "value": kontakt, "inline": False},
                {"name": "📅 Datum", "value": datum, "inline": True},
                {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True}]}]
        }
        requests.post(DISCORD_WEBHOOK, json=data)
    except: pass

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
frizure_po_duzini = {"Kratka kosa": ["Ravnanje kose - 10€", "Uvijanje kose - 20€", "Hollywood valovi - 25€", "Elegantni repovi - 15€"], "Duga kosa": ["Ravnanje kose - 20€", "Uvijanje kose - 30€", "Hollywood valovi - 35€", "Elegantni repovi - 25€"]}

# --- UI ---
st.title("✨ Adora Beauty Concept")
stranica = st.sidebar.radio("Navigacija", ["📅 Rezervacija", "❌ Otkazivanje", "🔐 Admin Panel"])

if stranica == "📅 Rezervacija":
    col1, col2 = st.columns(2)
    with col1: ime = st.text_input("Ime i Prezime:")
    with col2: kontakt = st.text_input("Kontakt (IG/Br):")
    kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None, placeholder="Odaberite...")
    
    puna_usluga = None
    if kat:
        if kat == "Frizure":
            odabir = st.selectbox("Dužina/Frizura:", list(usluge_mapa["Frizure"]), index=None)
            if odabir and odabir in frizure_po_duzini:
                usluga = st.selectbox("Usluga:", frizure_po_duzini[odabir], index=None)
                if usluga: puna_usluga = f"{kat} -> {odabir} -> {usluga}"
        else:
            usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
            if usluga: puna_usluga = f"{kat} -> {usluga}"
    
    if puna_usluga:
        d_input = st.date_input("Datum:", min_value=datetime.today(), format="DD/MM/YYYY")
        datum_str = d_input.strftime("%d/%m/%Y")
        df = ucitaj_termine()
        zauzeti = df[df['Datum'] == datum_str]['Vrijeme'].tolist()
        dostupna = [v for v in ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"] if v not in zauzeti]
        
        if dostupna:
            vrijeme = st.selectbox("Slobodno vrijeme:", dostupna)
            if st.button("POTVRDI REZERVACIJU"):
                if time.time() - st.session_state.get('zadnji_klik', 0) < 10:
                    st.warning("Pričekajte 10 sekundi!")
                elif ime and kontakt:
                    spremi_termin(ime, kontakt, datum_str, vrijeme, puna_usluga)
                    posalji_discord_obavijest(ime, kontakt, datum_str, vrijeme, puna_usluga)
                    st.session_state['zadnji_klik'] = time.time()
                    placeholder = st.empty()
                    placeholder.success("Termin uspješno rezerviran!")
                    time.sleep(4)
                    placeholder.empty()
                    st.rerun()

elif stranica == "❌ Otkazivanje":
    st.subheader("Otkazivanje termina")
    ime_klijenta = st.text_input("Unesite ime:")
    if ime_klijenta:
        df = ucitaj_termine()
        termini = df[df['Ime'] == ime_klijenta]
        if not termini.empty:
            odabrani = st.selectbox("Odaberite termin:", termini['Datum'] + " u " + termini['Vrijeme'])
            if st.button("POTVRDI OTKAZIVANJE"):
                d_termin = datetime.strptime(odabrani.split(" u ")[0], "%d/%m/%Y")
                if d_termin - datetime.now() < timedelta(days=2):
                    st.error("Ne možete otkazati unutar 48 sati!")
                else:
                    df = df.drop(df[(df['Ime'] == ime_klijenta) & (df['Datum'] == odabrani.split