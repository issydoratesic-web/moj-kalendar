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
    datum_str = datum_obj.strftime('%d/%m/%Y')
    novi = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": datum_str, "Vrijeme": vrijeme, "Usluga": usluga, "Kod": kod}])
    df = pd.concat([df, novi], ignore_index=True)
    df.to_csv("termini.csv", index=False)

def obrisi_termin(ime, datum_str, vrijeme):
    df = ucitaj_termine()
    # Strogo filtriranje po string vrijednostima
    mask = (df['Ime'].str.lower() == ime.strip().lower()) & (df['Datum'] == datum_str) & (df['Vrijeme'] == vrijeme)
    df = df[~mask]
    df.to_csv("termini.csv", index=False)

# --- UI ---
st.title("✨ Adora Beauty Concept")

usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Masaža i piling - 35€"],
    "Frizure": ["Kratka kosa", "Duga kosa", "Punđa - 15€"],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

ime = st.text_input("Ime i Prezime:")
kontakt = st.text_input("Kontakt:")
kat = st.selectbox("Kategorija:", list(usluge_mapa.keys()), index=None)

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        datum = st.date_input("Datum:", min_value=datetime.today())
        st.markdown(f"**Odabrani datum:** `{datum.strftime('%d/%m/%Y')}`")
        
        df_svi = ucitaj_termine()
        dat_str = datum.strftime("%d/%m/%Y")
        zauzeti = df_svi[df_svi['Datum'] == dat_str]['Vrijeme'].tolist()
        slobodni = [f"{h:02d}:00" for h in range(8, 21) if f"{h:02d}:00" not in zauzeti]
        vrijeme = st.selectbox("Vrijeme:", slobodni)

        if st.button("POTVRDI REZERVACIJU"):
            if ime and kontakt:
                kod = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
                spremi_termin(ime, kontakt, datum, vrijeme, usluga, kod)
                st.success(f"Rezervirano! Kod: {kod}")
                time_module.sleep(2)
                st.rerun()

st.markdown("---")
st.subheader("🔎 Provjera i otkazivanje")
ime_pretraga = st.text_input("Ime za provjeru:")
if ime_pretraga:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.lower() == ime_pretraga.strip().lower()]
    for idx, row in moji.iterrows():
        st.write(f"{row['Usluga']} | {row['Datum']} u {row['Vrijeme']}")
        if st.button(f"❌ Otkazi termin {row['Vrijeme']}", key=f"b{idx}"):
            obrisi_termin(row['Ime'], row['Datum'], row['Vrijeme'])
            st.rerun()

# --- ADMIN PANEL ---
with st.sidebar:
    st.header("🔐 Admin")
    if st.text_input("Lozinka:", type="password") == st.secrets.get("ADMIN_PASSWORD"):
        df_admin = ucitaj_termine()
        st.dataframe(df_admin)
        
        if not df_admin.empty:
            # Izbornik za brisanje
            opcije = df_admin.apply(lambda x: f"{x['Ime']} - {x['Datum']} - {x['Vrijeme']}", axis=1).tolist()
            odabrani = st.selectbox("Odaberi za brisanje:", opcije)
            if st.button("OBRIŠI ODABRANI"):
                ime_adm, dat_adm, vr_adm = odabrani.split(" - ")
                obrisi_termin(ime_adm, dat_adm, vr_adm)
                st.rerun()
