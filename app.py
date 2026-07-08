import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", page_icon="✂️", layout="centered")

# --- FUNKCIJE ---
def posalji_na_discord(naslov, ime, usluga, kontakt, datum, vrijeme):
    webhook_url = st.secrets.get("DISCORD_WEBHOOK")
    if not webhook_url: return
    
    embed = {
        "title": f"🔔 {naslov}",
        "color": 3066993, 
        "fields": [
            {"name": "👤 Klijent", "value": ime, "inline": False},
            {"name": "✂️ Usluga", "value": usluga, "inline": False},
            {"name": "📱 Kontakt", "value": kontakt, "inline": False},
            {"name": "📅 Datum", "value": datum, "inline": True},
            {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True}
        ]
    }
    try:
        requests.post(webhook_url, json={"embeds": [embed]})
    except:
        pass

def ucitaj_termine():
    # Osvježavamo cache kako bi se uvijek učitalo stanje iz datoteke
    st.cache_data.clear()
    if os.path.exists("termini.csv"):
        try:
            return pd.read_csv("termini.csv", dtype=str)
        except:
            return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga"])
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga"])

def spremi_termin(ime_puno, kontakt, dat_str, vrijeme, usluga):
    df = ucitaj_termine()
    novi = pd.DataFrame([{"Ime": ime_puno, "Kontakt": kontakt, "Datum": dat_str, "Vrijeme": vrijeme, "Usluga": usluga}])
    df = pd.concat([df, novi], ignore_index=True)
    df.to_csv("termini.csv", index=False)
    posalji_na_discord("Nova rezervacija!", ime_puno, usluga, kontakt, dat_str, vrijeme)

def obrisi_termin_po_indexu(index):
    df = ucitaj_termine()
    termin = df.loc[int(index)]
    posalji_na_discord("Termin otkazan!", termin['Ime'], termin['Usluga'], termin['Kontakt'], termin['Datum'], termin['Vrijeme'])
    df = df.drop(index)
    df.to_csv("termini.csv", index=False)
    st.cache_data.clear()

# --- UI ---
st.title("✨ Adora Beauty Concept")

# ... (ostatak koda za rezervaciju ostaje isti) ...

# --- OTKAZIVANJE TERMINA ---
st.markdown("---")
st.subheader("👤 Otkazivanje termina")
ime_otkaz_input = st.text_input("Upišite puno ime i prezime za otkazivanje:")

if ime_otkaz_input:
    df = ucitaj_termine()
    search_term = ime_otkaz_input.strip()
    
    # Pretraga kroz CSV
    moji_termini = df[df['Ime'].str.contains(search_term, case=False, na=False)]
    
    if not moji_termini.empty:
        for idx, row in moji_termini.iterrows():
            if st.button(f"Otkazi: {row['Usluga']} ({row['Datum']} u {row['Vrijeme']})", key=f"btn_{idx}"):
                obrisi_termin_po_indexu(idx)
                st.success("Termin je uspješno otkazan.")
                time.sleep(1)
                st.rerun()
    else:
        st.warning("Nije pronađen nijedan termin za to ime. Provjerite jeste li upisali točno ime i prezime kako je navedeno u rezervaciji.")

# --- ADMIN PANEL ---
with st.sidebar:
    st.header("🔐 Admin")
    if st.text_input("Lozinka:", type="password") == "171102":
        df = ucitaj_termine()
        st.subheader("Ručno otkazivanje termina")
        if not df.empty:
            opcije = {idx: f"{row['Ime']} - {row['Datum']} u {row['Vrijeme']}" for idx, row in df.iterrows()}
            odabir = st.selectbox("Odaberi termin za brisanje:", options=list(opcije.keys()), format_func=lambda x: opcije[x])
            if st.button("Obriši odabrani termin"):
                obrisi_termin_po_indexu(odabir)
                st.rerun()
        else: st.write("Nema termina.")
