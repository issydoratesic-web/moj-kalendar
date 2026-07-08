import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import time

# --- KONFIGURACIJA I PODACI ---
st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

usluge_mapa = {
    "Šminkanje": {"Šminkanje": "40€", "Terensko šminkanje": "50€"},
    "Obrve": {"Oblikovanje pincetom": "8€", "Oblikovanje i bojanje": "15€", "Brow lift": "30€"},
    "Tretmani lica": {"Enzimski piling": "25€", "Masaža i piling": "35€"},
    "Frizure": {"Kratka kosa": "10€", "Duga kosa": "15€", "Punđa": "15€"},
    "Little Luxe Spa": {"Mini": "50€", "Classic": "70€", "VIP": "100€"}
}

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv")
    return pd.DataFrame(columns=["Ime", "Prezime", "Kontakt", "Datum", "Usluga"])

def spremi_termin(ime, prezime, kontakt, datum_str, usluga):
    df = ucitaj_termine()
    novi = pd.DataFrame([{"Ime": ime, "Prezime": prezime, "Kontakt": kontakt, "Datum": datum_str, "Usluga": usluga}])
    df = pd.concat([df, novi], ignore_index=True)
    df.to_csv("termini.csv", index=False)

# --- UI ---
st.title("✨ Adora Beauty Concept")

# NAPOMENA
st.info("""
⚠️ **Napomena:** Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. Termini otkazani unutar 24h ili nedolazak bez obavijesti naplaćuju se u iznosu 100% cijene usluge.
- Prilikom zakazivanja termina za **šminkanje** potrebno je uplatiti akontaciju (50%) na IBAN: HR03 2402 0061 1406 1395 3.
""")

# REZERVACIJA
st.subheader("Nova rezervacija")
c1, c2 = st.columns(2)
ime = c1.text_input("Ime:")
prezime = c2.text_input("Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")

kat = st.selectbox("Kategorija:", list(usluge_mapa.keys()))
usluga = st.selectbox("Usluga:", list(usluge_mapa[kat].keys()))
st.write(f"Cijena: **{usluge_mapa[kat][usluga]}**")

d, m, g = st.columns(3)
dan = d.selectbox("Dan:", range(1, 32))
mjesec = m.selectbox("Mjesec:", range(1, 13))
godina = g.selectbox("Godina:", [datetime.now().year, datetime.now().year + 1])
datum_str = f"{dan:02d}/{mjesec:02d}/{godina}"

if st.button("POTVRDI REZERVACIJU"):
    if ime and prezime:
        spremi_termin(ime, prezime, kontakt, datum_str, usluga)
        st.success("Vaš termin je uspješno rezerviran!")
        time.sleep(2)
        st.rerun()
    else:
        st.warning("Molimo unesite ime i prezime.")

# KORISNIČKO OTKAZIVANJE
st.markdown("---")
st.subheader("🔎 Otkazivanje rezervacije")
ime_otkaz = st.text_input("Unesite ime za otkazivanje:")
prezime_otkaz = st.text_input("Unesite prezime za otkazivanje:")
if ime_otkaz and prezime_otkaz:
    df = ucitaj_termine()
    moji = df[(df['Ime'].str.lower() == ime_otkaz.lower()) & (df['Prezime'].str.lower() == prezime_otkaz.lower())]
    for idx, row in moji.iterrows():
        st.write(f"Termin: {row['Usluga']} | {row['Datum']}")
        if st.button(f"❌ Otkazi termin {idx}", key=idx):
            df = df.drop(idx)
            df.to_csv("termini.csv", index=False)
            st.success("Otkazano.")
            st.rerun()

# ADMIN PANEL
with st.sidebar:
    st.header("🔐 Admin")
    if st.text_input("Lozinka:", type="password") == st.secrets.get("ADMIN_PASSWORD"):
        df = ucitaj_termine()
        st.dataframe(df)
        idx_brisi = st.selectbox("Odaberi red za brisanje:", df.index)
        if st.button("OBRIŠI TERMIN"):
            df = df.drop(idx_brisi)
            df.to_csv("termini.csv", index=False)
            st.rerun()
