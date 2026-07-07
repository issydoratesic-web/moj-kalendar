import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time as time_module
import random
import string

st.set_page_config(page_title="Adora Beauty Concept", page_icon="✂️", layout="centered")

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Kod"])

def spremi_termin(ime, kontakt, dat_str, vrijeme, usluga, kod):
    df = ucitaj_termine()
    novi = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": dat_str, "Vrijeme": vrijeme, "Usluga": usluga, "Kod": kod}])
    df = pd.concat([df, novi], ignore_index=True)
    df.to_csv("termini.csv", index=False)

def obrisi_termin(ime, dat_str, vrijeme):
    df = ucitaj_termine()
    mask = (df['Ime'].str.lower() == ime.strip().lower()) & (df['Datum'] == dat_str) & (df['Vrijeme'] == vrijeme)
    df = df[~mask]
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
    "Frizure": ["Kratka kosa", "Duga kosa", "Punđa - 15€"],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

ime = st.text_input("Ime i Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")
kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None)

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        st.write("---")
        st.subheader("Odaberite datum:")
        col1, col2, col3 = st.columns(3)
        with col1: dan = st.selectbox("Dan:", [str(i).zfill(2) for i in range(1, 32)])
        with col2: mjesec = st.selectbox("Mjesec:", [str(i).zfill(2) for i in range(1, 13)])
        
        # Raspon od trenutne godine do 2035.
        aktualna_godina = datetime.now().year
        raspon_godina = [str(g) for g in range(aktualna_godina, 2036)]
        
        with col3: godina = st.selectbox("Godina:", raspon_godina)
        
        dat_str = f"{dan}/{mjesec}/{godina}"
        st.write(f"📅 Odabrani datum: **{dat_str}**")
        
        df_svi = ucitaj_termine()
        zauzeti = df_svi[df_svi['Datum'] == dat_str]['Vrijeme'].tolist()
        slobodni = [f"{h:02d}:00" for h in range(8, 21) if f"{h:02d}:00" not in zauzeti]
        vrijeme = st.selectbox("Vrijeme:", slobodni)

        if st.button("POTVRDI REZERVACIJU"):
            if ime and kontakt:
                kod = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                spremi_termin(ime, kontakt, dat_str, vrijeme, usluga, kod)
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
        df_admin = ucitaj_termine()
        st.dataframe(df_admin)
