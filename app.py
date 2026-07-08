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
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga"])

def spremi_termin(ime_puno, kontakt, dat_str, vrijeme, usluga):
    df = ucitaj_termine()
    novi = pd.DataFrame([{"Ime": ime_puno, "Kontakt": kontakt, "Datum": dat_str, "Vrijeme": vrijeme, "Usluga": usluga}])
    df = pd.concat([df, novi], ignore_index=True)
    df.to_csv("termini.csv", index=False)
    posalji_na_discord("Nova rezervacija!", ime_puno, usluga, kontakt, dat_str, vrijeme)

def obrisi_termin_po_indexu(index):
    df = ucitaj_termine()
    termin = df.loc[index]
    posalji_na_discord("Termin otkazan!", termin['Ime'], termin['Usluga'], termin['Kontakt'], termin['Datum'], termin['Vrijeme'])
    df = df.drop(index)
    df.to_csv("termini.csv", index=False)

# --- UI ---
st.title("✨ Adora Beauty Concept")

st.info("""
⚠️ **Napomena:** - Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. 
Termini otkazani unutar 24h ili nedolazak bez obavijesti naplaćuju se u iznosu 100% cijene usluge.

• Prilikom zakazivanja termina za **šminkanje** potrebno je uplatiti akontaciju u iznosu od 50% cijene usluge na IBAN: HR03 2402 0061 1406 1395 3
""")

usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Masaža i piling - 35€"],
    "Frizure": ["Kratka kosa - 20€", "Duga kosa - 30€", "Punđa - 15€"],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

# Unos klijenta
col_i, col_p = st.columns(2)
with col_i: ime = st.text_input("Ime:")
with col_p: prezime = st.text_input("Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")
kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None)

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        col1, col2, col3 = st.columns(3)
        with col1: dan = st.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
        with col2: mjesec = st.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
        with col3: godina = st.selectbox("Godina:", [str(g) for g in range(2026, 2030)])
        dat_str = f"{dan}/{mjesec}/{godina}"
        
        df_svi = ucitaj_termine()
        zauzeti = df_svi[df_svi['Datum'] == dat_str]['Vrijeme'].tolist()
        slobodni = [f"{h:02d}:00" for h in range(8, 21) if f"{h:02d}:00" not in zauzeti]
        vrijeme = st.selectbox("Vrijeme:", slobodni)

        if st.button("POTVRDI REZERVACIJU"):
            if ime and prezime and kontakt:
                spremi_termin(f"{ime} {prezime}", kontakt, dat_str, vrijeme, usluga)
                st.success("Rezervacija potvrđena!")
                time.sleep(1); st.rerun()
            else: st.error("Molimo ispunite sve podatke.")

# --- OTKAZIVANJE TERMINA ---
st.markdown("---")
st.subheader("👤 Otkazivanje termina")
ime_otkaz_input = st.text_input("Upišite puno ime i prezime za otkaz:")

if ime_otkaz_input:
    df = ucitaj_termine()
    moji_termini = df[df['Ime'].str.lower() == ime_otkaz_input.strip().lower()]
    
    if not moji_termini.empty:
        for idx, row in moji_termini.iterrows():
            if st.button(f"Otkazi: {row['Usluga']} ({row['Datum']} u {row['Vrijeme']})"):
                obrisi_termin_po_indexu(idx)
                st.success(f"Termin za {row['Usluga']} je otkazan.")
                st.rerun()
    else:
        st.warning("Nije pronađen nijedan termin za to ime.")

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
