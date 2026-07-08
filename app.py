import streamlit as st
import pandas as pd
import os
import time

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# Definiranje usluga s cijenama
usluge_mapa = {
    "Šminkanje": {"Šminkanje (40€)": "40€", "Terensko šminkanje (50€)": "50€"},
    "Obrve": {"Oblikovanje pincetom (8€)": "8€", "Oblikovanje i bojanje (15€)": "15€", "Brow lift (30€)": "30€"},
    "Tretmani lica": {"Enzimski piling (25€)": "25€", "Masaža i piling (35€)": "35€"},
    "Frizure": {"Kratka kosa (10€)": "10€", "Duga kosa (15€)": "15€", "Punđa (15€)": "15€"},
    "Little Luxe Spa": {"Mini (50€)": "50€", "Classic (70€)": "70€", "VIP (100€)": "100€"}
}

def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv")
    return pd.DataFrame(columns=["Ime", "Prezime", "Kontakt", "Datum", "Vrijeme", "Usluga"])

# UI
st.title("✨ Adora Beauty Concept")

c1, c2 = st.columns(2)
ime = c1.text_input("Ime:")
prezime = c2.text_input("Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")

kat = st.selectbox("Kategorija:", list(usluge_mapa.keys()))
usluga = st.selectbox("Usluga:", list(usluge_mapa[kat].keys()))

d, m, g, v = st.columns(4)
dan = d.selectbox("Dan:", range(1, 32))
mjesec = m.selectbox("Mjesec:", range(1, 13))
godina = g.selectbox("Godina:", [2026, 2027])
vrijeme = v.selectbox("Vrijeme:", [f"{h:02d}:00" for h in range(8, 20)])

if st.button("POTVRDI REZERVACIJU"):
    df = ucitaj_termine()
    novi = pd.DataFrame([{"Ime": ime, "Prezime": prezime, "Kontakt": kontakt, 
                          "Datum": f"{dan}/{mjesec}/{godina}", "Vrijeme": vrijeme, "Usluga": usluga}])
    df = pd.concat([df, novi], ignore_index=True)
    df.to_csv("termini.csv", index=False)
    st.success("Termin potvrđen!")
    time.sleep(1); st.rerun()

# ADMIN
with st.sidebar:
    st.header("🔐 Admin")
    if st.text_input("Lozinka:", type="password") == st.secrets.get("ADMIN_PASSWORD"):
        df = ucitaj_termine()
        st.dataframe(df)
        if not df.empty:
            idx = st.selectbox("Odaberi red za brisanje:", df.index)
            if st.button("OBRIŠI"):
                df.drop(idx).to_csv("termini.csv", index=False)
                st.rerun()
