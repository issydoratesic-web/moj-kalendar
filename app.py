import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import time

# --- KONFIGURACIJA ---
st.set_config = st.set_page_config(page_title="Adora Studio", page_icon="✂️", layout="centered")

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

# --- UI ---
st.title("✨ Adora Beauty Concept")

# Ovdje je navigacija bez Admin Panela
stranica = st.sidebar.radio("Navigacija", ["📅 Rezervacija", "❌ Otkazivanje"])

if stranica == "📅 Rezervacija":
    st.info("""⚠️ **Napomena:**
- Otkazivanje termina potrebno je najaviti najmanje 24h prije termina.
- Prilikom zakazivanja termina za **šminkanje** potrebno je uplatiti akontaciju u iznosu od 50% cijene usluge na IBAN: HR03 2402 0061 1406 1395 3.
- **Ako želite otkazati termin, otvorite izbornik (dvije strelice gore lijevo) i odaberite 'Otkazivanje'.**""")
    
    # ... (ostatak koda za rezervaciju ostaje isti) ...

elif stranica == "❌ Otkazivanje":
    # ... (kod za otkazivanje ostaje isti) ...

# --- SKRIVENI ADMIN PANEL ---
st.markdown("---")
if st.button("🔐 Pristup za administratora"):
    st.session_state.admin_mode = True

if st.session_state.get("admin_mode", False):
    lozinka = st.text_input("Unesite lozinku:", type="password")
    if lozinka == st.secrets.get("ADMIN_PASSWORD"):
        st.subheader("Admin Panel")
        st.dataframe(ucitaj_termine())
        if st.button("Izlogiraj se"): st.session_state.admin_mode = False
    elif lozinka:
        st.error("Pogrešna lozinka!")