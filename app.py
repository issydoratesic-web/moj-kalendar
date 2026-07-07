import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import time as time_module
import random
import string

# --- KONFIGURACIJA ---
st.set_page_config(page_title="Adora Beauty Concept", page_icon="✂️", layout="centered")

# --- FUNKCIJE ---
def posalji_discord_obavijest(ime, kontakt, datum, vrijeme, usluga, kod, tip="rezervacija"):
    try:
        DISCORD_WEBHOOK = st.secrets["DISCORD_WEBHOOK"]
        color = 3066993 if tip == "rezervacija" else 15158332
        data = {"content": "🔔 Nova rezervacija!" if tip == "rezervacija" else "❌ Otkazan termin!",
                "embeds": [{"title": f"👤 {ime}", "color": color, "fields": [
                    {"name": "✂️ Usluga", "value": usluga, "inline": False},
                    {"name": "📱 Kontakt", "value": kontakt, "inline": False},
                    {"name": "📅 Datum", "value": datum, "inline": True},
                    {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True},
                    {"name": "🔑 Kod", "value": kod, "inline": True}]}]}
        requests.post(DISCORD_WEBHOOK, json=data)
    except: pass

def ucitaj_termine():
    if os.path.exists("termini.csv"): return pd.read_csv("termini.csv")
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Kod"])

def spremi_termin(ime, kontakt, datum, vrijeme, usluga, kod):
    df = ucitaj_termine()
    novi_termin = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum, "Vrijeme": vrijeme, "Usluga": usluga, "Kod": kod}])
    df = pd.concat([df, novi_termin], ignore_index=True)
    df.to_csv("termini.csv", index=False)

def obrisi_termin(kod):
    df = ucitaj_termine()
    termin = df[df['Kod'] == kod]
    if not termin.empty:
        podaci = termin.iloc[0].to_dict()
        novi_df = df[df['Kod'] != kod]
        novi_df.to_csv("termini.csv", index=False)
        return podaci
    return None

# --- UI ---
st.title("✨ Adora Beauty Concept")

st.info("""⚠️ **Napomena:**
- Otkazivanje termina moguće je isključivo uz **Kod za otkazivanje** koji dobijete prilikom rezervacije.
- Prilikom zakazivanja termina za **šminkanje** potrebno je uplatiti akontaciju (50%) na IBAN: HR03 2402 0061 1406 1395 3.""")

st.subheader("Nova rezervacija")

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
            df_svi = ucitaj_termine()
            termini_na_taj_datum = df_svi[df_svi['Datum'] == datum.strftime("%d/%m/%Y")]
            zauzeti_sati = termini_na_taj_datum['Vrijeme'].tolist()
            svi_sati = [f"{h:02d}:00" for h in range(8, 21)]
            slobodni_sati = [sat for sat in svi_sati if sat not in zauzeti_sati]
            
            if slobodni_sati:
                odabrano_vrijeme = st.selectbox("Odaberite slobodno vrijeme:", slobodni_sati)
            else:
                st.error("Nažalost, za ovaj datum nema više slobodnih termina.")
                odabrano_vrijeme = None
        
        if odabrano_vrijeme and st.button("POTVRDI REZERVACIJU"):
            if not ime or not kontakt:
                st.warning("Molimo unesite ime i kontakt.")
            else:
                kod = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                spremi_termin(ime, kontakt, datum.strftime("%d/%m/%Y"), odabrano_vrijeme, usluga, kod)
                posalji_discord_obavijest(ime, kontakt, datum.strftime("%d/%m/%Y"), odabrano_vrijeme, usluga, kod)
                st.success(f"✅ Uspješno! Vaš kod za otkazivanje je: **{kod}**. Spremite ga!")
                time_module.sleep(5)
                st.rerun()

# --- OTKAZIVANJE (NA DNU) ---
st.markdown("---")
with st.expander("❌ Želim otkazati termin (potreban kod)"):
    kod_input = st.text_input("Unesite Vaš kod za otkazivanje:")
    if st.button("OTKAŽI TERMIN"):
        obrisani = obrisi_termin(kod_input)
        if obrisani:
            st.success("Termin je otkazan.")
            posalji_discord_obavijest(obrisani['Ime'], obrisani['Kontakt'], obrisani['Datum'], obrisani['Vrijeme'], obrisani['Usluga'], kod_input, tip="otkazivanje")
            time_module.sleep(1)
            st.rerun()
        else:
            st.error("Kod nije pronađen.")

# --- ADMIN SIDEBAR ---
with st.sidebar:
    st.header("🔐 Admin")
    lozinka = st.text_input("Lozinka:", type="password")
    if lozinka == st.secrets.get("ADMIN_PASSWORD"):
        st.subheader("Popis svih termina")
        st.dataframe(ucitaj_termine())