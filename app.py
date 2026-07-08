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
def posalji_discord_obavijest(ime, kontakt, datum, vrijeme, usluga, tip="rezervacija"):
    try:
        DISCORD_WEBHOOK = st.secrets["DISCORD_WEBHOOK"]
        color = 3066993 if tip == "rezervacija" else 15158332
        naslov = "🔔 Nova rezervacija!" if tip == "rezervacija" else "❌ Otkazan termin!"
        data = {"content": naslov, "embeds": [{"title": f"👤 {ime}", "color": color, "fields": [
            {"name": "✂️ Usluga", "value": usluga, "inline": False},
            {"name": "📱 Kontakt", "value": kontakt, "inline": False},
            {"name": "📅 Datum", "value": datum, "inline": True},
            {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True}]}]}
        requests.post(DISCORD_WEBHOOK, json=data)
    except: pass

def ucitaj_termine():
    if os.path.exists("termini.csv"):
        df = pd.read_csv("termini.csv")
        # Osiguravanje DD/MM/YYYY formata
        df['Datum'] = pd.to_datetime(df['Datum'], dayfirst=True, errors='coerce').dt.strftime('%d/%m/%Y')
        return df
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga"])

def spremi_termin(ime, kontakt, datum, vrijeme, usluga):
    df = ucitaj_termine()
    datum_str = datum.strftime('%d/%m/%Y')
    novi_termin = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum_str, "Vrijeme": vrijeme, "Usluga": usluga}])
    df = pd.concat([df, novi_termin], ignore_index=True)
    df.to_csv("termini.csv", index=False)

def obrisi_tocan_termin(ime, datum, vrijeme):
    df = ucitaj_termine()
    novi_df = df[~((df['Ime'].str.lower() == ime.strip().lower()) & (df['Datum'] == datum) & (df['Vrijeme'] == vrijeme))]
    novi_df.to_csv("termini.csv", index=False)

# --- UI ---
st.title("✨ Adora Beauty Concept")

st.info("""
⚠️ **Napomena:** - Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. 
- Prilikom zakazivanja termina za **šminkanje** potrebno je uplatiti akontaciju (50%) na IBAN: HR03 2402 0061 1406 1395 3.
""")

# --- REZERVACIJA ---
st.subheader("Nova rezervacija")
ime = st.text_input("Ime i Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")
# ... (ostatak forme za odabir usluge i datuma) ...

# --- OTKAZIVANJE (ZA KLIJENTE) ---
st.markdown("---")
st.subheader("🔎 Otkazivanje rezervacije")
ime_otkaz = st.text_input("Unesite svoje puno ime i prezime za otkazivanje:")
if ime_otkaz:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.lower() == ime_otkaz.strip().lower()]
    for idx, row in moji.iterrows():
        st.write(f"Termin: {row['Usluga']} | {row['Datum']} u {row['Vrijeme']}")
        if st.button(f"❌ Otkazi {row['Vrijeme']}", key=f"btn_{idx}"):
            obrisi_tocan_termin(row['Ime'], row['Datum'], row['Vrijeme'])
            st.success("Termin otkazan.")
            st.rerun()

# --- ADMIN PANEL ---
with st.sidebar:
    st.header("🔐 Admin Panel")
    if st.text_input("Lozinka:", type="password") == st.secrets.get("ADMIN_PASSWORD"):
        df_a = ucitaj_termine()
        st.subheader("Svi termini")
        st.dataframe(df_a)
        
        # Admin brisanje putem izbornika
        opcije = df_a.apply(lambda x: f"{x['Ime']} ({x['Datum']} - {x['Vrijeme']})", axis=1).tolist()
        odabrani = st.selectbox("Odaberite termin za brisanje:", opcije)
        if st.button("OBRIŠI ODABRANI TERMIN"):
            dio = odabrani.split(" (")
            ime_b = dio[0]
            datum_vr = dio[1].replace(")", "").split(" - ")
            obrisi_tocan_termin(ime_b, datum_vr[0], datum_vr[1])
            st.rerun()
