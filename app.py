import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import time

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

# --- PODACI ---
usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
    "Frizure": ["Kratka kosa", "Duga kosa", "Punđa - 15€"],
    "Ostale usluge": ["Relax zona - 25€"],
    "Little Luxe Spa tretman": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

# --- UI - GLAVNA NAVIGACIJA ---
st.title("✨ Adora Beauty Concept")
stranica = st.sidebar.radio("Navigacija", ["📅 Rezervacija", "❌ Otkazivanje"])

if stranica == "📅 Rezervacija":
    st.info("""⚠️ **Napomena:**
- Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. 
- Prilikom zakazivanja termina za **šminkanje** potrebno je uplatiti akontaciju (50% cijene) na IBAN: HR03 2402 0061 1406 1395 3.
- **Ako želite otkazati termin, otvorite izbornik (dvije strelice gore lijevo) i odaberite 'Otkazivanje'.**""")
    
    col1, col2 = st.columns(2)
    with col1: ime = st.text_input("Ime i Prezime:")
    with col2: kontakt = st.text_input("Kontakt (IG/Br):")
    kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None)
    
    if kat:
        usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
        if usluga:
            d_input = st.date_input("Datum:", min_value=datetime.today(), format="DD/MM/YYYY")
            datum_str = d_input.strftime("%d/%m/%Y")
            if st.button("POTVRDI REZERVACIJU"):
                if ime and kontakt:
                    spremi_termin(ime, kontakt, datum_str, "12:00", usluga)
                    posalji_discord_obavijest(ime, kontakt, datum_str, "12:00", usluga)
                    st.success("✅ Termin uspješno rezerviran!")
                    time.sleep(2)
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
                st.warning("Pričekajte provjeru termina...") 
        else:
            st.write("Nema pronađenih termina.")

# --- SKRIVENI ADMIN PANEL (Ovo je sada potpuno odvojeno) ---
st.markdown("---")
if st.button("🔐 Pristup za administratora"):
    st.session_state.admin_mode = True

if st.session_state.get("admin_mode", False):
    lozinka = st.text_input("Unesite lozinku:", type="password")
    if lozinka == st.secrets.get("ADMIN_PASSWORD"):
        st.subheader("Admin Panel")
        st.dataframe(ucitaj_termine())
        if st.button("Izlogiraj se"): 
            st.session_state.admin_mode = False
            st.rerun()
    elif lozinka:
        st.error("Pogrešna lozinka!")