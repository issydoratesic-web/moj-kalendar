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

# --- UI ---
st.title("✨ Adora Beauty Concept")

# JEDNOSTAVNA NAVIGACIJA (Gumbi na vrhu za mobitele)
col_res, col_otk = st.columns(2)
if col_res.button("📅 Nova Rezervacija"): st.session_state.stranica = "Rezervacija"
if col_otk.button("❌ Otkazivanje"): st.session_state.stranica = "Otkazivanje"

if "stranica" not in st.session_state: st.session_state.stranica = "Rezervacija"

if st.session_state.stranica == "Rezervacija":
    st.info("""⚠️ **Napomena:** - Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. 
- Prilikom zakazivanja termina za **šminkanje** potrebno je uplatiti akontaciju (50% cijene) na IBAN: HR03 2402 0061 1406 1395 3.""")
    
    ime = st.text_input("Ime i Prezime:")
    kontakt = st.text_input("Kontakt (IG/Br):")
    kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None)
    
    if kat:
        usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
        if usluga:
            datum = st.date_input("Datum:", min_value=datetime.today())
            if st.button("POTVRDI REZERVACIJU"):
                if ime and kontakt:
                    spremi_termin(ime, kontakt, datum.strftime("%d/%m/%Y"), "12:00", usluga)
                    posalji_discord_obavijest(ime, kontakt, datum.strftime("%d/%m/%Y"), "12:00", usluga)
                    st.success("✅ Termin uspješno rezerviran!")
                    time.sleep(1)
                    st.rerun()

elif st.session_state.stranica == "Otkazivanje":
    st.subheader("❌ Otkazivanje termina")
    ime_klijenta = st.text_input("Unesite ime i prezime za pretragu:")
    if ime_klijenta:
        df = ucitaj_termine()
        termini = df[df['Ime'] == ime_klijenta]
        if not termini.empty:
            st.write("Vaši termini:", termini)
            st.warning("Za otkazivanje nas kontaktirajte izravno.")
        else:
            st.write("Nema pronađenih termina za to ime.")

# --- SKRIVENI ADMIN PANEL ---
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