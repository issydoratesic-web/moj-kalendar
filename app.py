import streamlit as st
import pandas as pd
from datetime import datetime, time as dt_time
import os
import requests
import time as time_module

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Adora Beauty Concept", page_icon="✂️", layout="centered")

# --- FUNKCIJE ---
def posalji_discord_obavijest(ime, kontakt, datum, vrijeme, usluga, tip="rezervacija"):
    try:
        DISCORD_WEBHOOK = st.secrets["DISCORD_WEBHOOK"]
        color = 3066993 if tip == "rezervacija" else 15158332
        data = {"content": "🔔 Nova rezervacija!" if tip == "rezervacija" else "❌ Otkazan termin!",
                "embeds": [{"title": f"👤 {ime}", "color": color, "fields": [
                    {"name": "✂️ Usluga", "value": usluga, "inline": False},
                    {"name": "📱 Kontakt", "value": kontakt, "inline": False},
                    {"name": "📅 Datum", "value": datum, "inline": True},
                    {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True}]}]}
        requests.post(DISCORD_WEBHOOK, json=data)
    except: pass

def ucitaj_termine():
    if os.path.exists("termini.csv"): return pd.read_csv("termini.csv")
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga"])

def spremi_termin(ime, kontakt, datum, vrijeme, usluga):
    df = ucitaj_termine()
    novi_termin = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum, "Vrijeme": vrijeme, "Usluga": usluga}])
    df = pd.concat([df, novi_termin], ignore_index=True)
    df.to_csv("termini.csv", index=False)

# --- DIALOG ZA OTKAZIVANJE ---
@st.dialog("❌ Otkazivanje termina")
def prozor_otkazivanje():
    st.write("Unesite ime i prezime kako bismo pronašli vaš termin.")
    ime_klijenta = st.text_input("Ime i prezime:")
    
    if st.button("Pronađi moj termin"):
        df = ucitaj_termine()
        termini = df[df['Ime'] == ime_klijenta]
        if not termini.empty:
            st.write(termini)
            st.warning("Za potvrdu otkazivanja nas kontaktirajte izravno.")
        else:
            st.error("Nema pronađenih termina.")
    
    if st.button("Zatvori"):
        st.rerun()

# --- UI ---
st.title("✨ Adora Beauty Concept")

# Napomena
st.info("""⚠️ **Napomena:**
- Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. Termini otkazani unutar 24h ili nedolazak bez obavijesti naplaćuju se u iznosu 100% cijene usluge.
- Prilikom zakazivanja termina za **šminkanje** potrebno je uplatiti akontaciju u iznosu od 50% cijene usluge na IBAN: HR03 2402 0061 1406 1395 3.""")

# Gumb za otkazivanje
if st.button("❌ Želim otkazati termin"):
    prozor_otkazivanje()

st.markdown("---")
st.subheader("Nova rezervacija")

# Podaci
usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
    "Frizure": ["Kratka kosa", "Duga kosa", "Punđa - 15€"],
    "Ostale usluge": ["Relax zona - 25€"],
    "Little Luxe Spa tretman": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

ime = st.text_input("Ime i Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")
kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None)

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        col1, col2 = st.columns(2)
        with col1: datum = st.date_input("Datum:", min_value=datetime.today())
        with col2: 
            # Ograničenje vremena od 08:00 do 20:00
            vrijeme = st.time_input("Vrijeme:", value=dt_time(8, 0), min_value=dt_time(8, 0), max_value=dt_time(20, 0))
        
        if st.button("POTVRDI REZERVACIJU"):
            if ime and kontakt:
                vrijeme_str = vrijeme.strftime("%H:%M")
                spremi_termin(ime, kontakt, datum.strftime("%d/%m/%Y"), vrijeme_str, usluga)
                posalji_discord_obavijest(ime, kontakt, datum.strftime("%d/%m/%Y"), vrijeme_str, usluga)
                st.success("✅ Termin uspješno rezerviran!")
                time_module.sleep(2)
                st.rerun()

# --- ADMIN (Skriveno na dnu) ---
st.markdown("---")
if st.button("🔐"):
    st.session_state.admin_mode = True

if st.session_state.get("admin_mode", False):
    lozinka = st.text_input("Lozinka:", type="password")
    if lozinka == st.secrets.get("ADMIN_PASSWORD"):
        st.subheader("Admin Panel")
        st.dataframe(ucitaj_termine())
        if st.button("Izlogiraj se"): 
            st.session_state.admin_mode = False
            st.rerun()
    elif lozinka:
        st.error("Pogrešna lozinka!")