import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import time
import random
import string

st.set_page_config(page_title="Adora Beauty Concept", page_icon="✂️", layout="centered")

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

def obrisi_termin(ime, datum, vrijeme):
    df = ucitaj_termine()
    df = df[~((df['Ime'].str.lower() == ime.strip().lower()) & (df['Datum'] == datum) & (df['Vrijeme'] == vrijeme))]
    df.to_csv("termini.csv", index=False)

st.title("✨ Adora Beauty Concept")

# --- REZERVACIJA ---
ime = st.text_input("Ime i Prezime:")
kontakt = st.text_input("Kontakt:")
datum = st.date_input("Datum:", min_value=datetime.today())
st.caption(f"Odabrani datum za bazu: {datum.strftime('%d/%m/%Y')}")

df_svi = ucitaj_termine()
dat_str = datum.strftime("%d/%m/%Y")
zauzeti = df_svi[df_svi['Datum'] == dat_str]['Vrijeme'].tolist()
slobodni = [f"{h:02d}:00" for h in range(8, 21) if f"{h:02d}:00" not in zauzeti]
vrijeme = st.selectbox("Vrijeme:", slobodni)

if st.button("POTVRDI REZERVACIJU"):
    if ime and kontakt:
        kod = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        spremi_termin(ime, kontakt, datum, vrijeme, "Usluga", kod)
        st.success(f"Rezervirano! Kod: {kod}")
        time.sleep(2)
        st.rerun()

# --- PROVJERA ---
st.markdown("---")
st.subheader("🔎 Provjera")
ime_pretraga = st.text_input("Ime za provjeru:")
if ime_pretraga:
    moji = df_svi[df_svi['Ime'].str.lower() == ime_pretraga.strip().lower()]
    for idx, row in moji.iterrows():
        st.write(f"{row['Datum']} u {row['Vrijeme']}")
        if st.button(f"Otkazi {row['Vrijeme']}", key=f"b{idx}"):
            obrisi_termin(row['Ime'], row['Datum'], row['Vrijeme'])
            st.rerun()

# --- ADMIN ---
with st.sidebar:
    st.header("🔐 Admin")
    if st.text_input("Lozinka:", type="password") == st.secrets.get("ADMIN_PASSWORD"):
        st.dataframe(ucitaj_termine())