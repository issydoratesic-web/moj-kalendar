import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import time as time_module
import random
import string

st.set_page_config(page_title="Adora Beauty Concept", page_icon="✂️", layout="centered")

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Kod"])

def spremi_termin(ime, kontakt, datum_obj, vrijeme, usluga, kod):
    df = ucitaj_termine()
    datum_str = datum_obj.strftime('%d/%m/%Y') # Forsiramo DD/MM/YYYY za bazu
    novi = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum_str, "Vrijeme": vrijeme, "Usluga": usluga, "Kod": kod}])
    df = pd.concat([df, novi], ignore_index=True)
    df.to_csv("termini.csv", index=False)

def obrisi_termin(ime, datum_str, vrijeme):
    df = ucitaj_termine()
    df['Datum'] = df['Datum'].astype(str)
    mask = (df['Ime'].str.lower() == ime.strip().lower()) & (df['Datum'] == datum_str) & (df['Vrijeme'] == vrijeme)
    df = df[~mask]
    df.to_csv("termini.csv", index=False)

# --- UI ---
st.title("✨ Adora Beauty Concept")

# VRACENE NAPOMENE
st.info("""
⚠️ **Napomena:** - Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. 
Termini otkazani unutar 24h ili nedolazak bez obavijesti naplaćuju se u iznosu 100% cijene usluge.

• Prilikom zakazivanja termina za **šminkanje** potrebno je uplatiti akontaciju u iznosu od 50% cijene usluge na IBAN: HR03 2402 0061 1406 1395 3
""")

usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Masaža i piling - 35€"],
    "Frizure": ["Kratka kosa", "Duga kosa", "Punđa - 15€"],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

ime = st.text_input("Ime i Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")
kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None)

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        datum = st.date_input("Datum:", min_value=datetime.today())
        # Vizualna potvrda za tebe da znaš što ide u bazu
        st.write(f"Odabrani datum za bazu: **{datum.strftime('%d/%m/%Y')}**")
        
        df_svi = ucitaj_termine()
        dat_str = datum.strftime("%d/%m/%Y")
        zauzeti = df_svi[df_svi['Datum'] == dat_str]['Vrijeme'].tolist()
        slobodni = [f"{h:02d}:00" for h in range(8, 21) if f"{h:02d}:00" not in zauzeti]
        vrijeme = st.selectbox("Vrijeme:", slobodni)

        if st.button("POTVRDI REZERVACIJU"):
            if ime and kontakt:
                kod = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                spremi_termin(ime, kontakt, datum, vrijeme, usluga, kod)
                st.success(f"Uspješno! Kod: {kod}")
                time_module.sleep(2)
                st.rerun()

st.markdown("---")
st.subheader("🔎 Provjera i otkazivanje")
ime_pretraga = st.text_input("Ime za provjeru:")
if ime_pretraga:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.lower() == ime_pretraga.strip().lower()]
    for idx, row in moji.iterrows():
        st.write(f"Termin: {row['Usluga']} | Datum: {row['Datum']} | Vrijeme: {row['Vrijeme']}")
        if st.button(f"❌ Otkazi {row['Vrijeme']}", key=f"b{idx}"):
            obrisi_termin(row['Ime'], row['Datum'], row['Vrijeme'])
            st.rerun()

with st.sidebar:
    st.header("🔐 Admin")
    if st.text_input("Lozinka:", type="password") == st.secrets.get("ADMIN_PASSWORD"):
        st.dataframe(ucitaj_termine())
