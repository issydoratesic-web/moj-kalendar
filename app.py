import streamlit as st
import pandas as pd
from datetime import datetime
import os
import requests
import time

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        df = pd.read_csv("termini.csv")
        # Osiguraj da stupci postoje
        for col in ["Ime", "Prezime", "Datum", "Usluga"]:
            if col not in df.columns: df[col] = ""
        return df
    return pd.DataFrame(columns=["Ime", "Prezime", "Kontakt", "Datum", "Usluga"])

def posalji_discord(ime, prezime, datum, usluga, tip="rezervacija"):
    try:
        webhook = st.secrets["DISCORD_WEBHOOK"]
        data = {"embeds": [{"title": "🔔 Rezervacija" if tip == "rezervacija" else "❌ Otkazivanje", 
                           "fields": [{"name": "Klijent", "value": f"{ime} {prezime}"}, {"name": "Usluga", "value": usluga}, {"name": "Datum", "value": datum}]}]}
        requests.post(webhook, json=data)
    except: pass

# --- UI ---
st.title("✨ Adora Beauty Concept")
st.info("⚠️ **Napomena:** Otkazivanje min. 24h prije. Akontacija 50% za šminkanje na IBAN: HR03 2402 0061 1406 1395 3.")

# REZERVACIJA
st.subheader("Nova rezervacija")
c1, c2 = st.columns(2)
ime = c1.text_input("Ime:")
prezime = c2.text_input("Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")

# (Ovdje bi išli tvoji izbornici za usluge - skraćeno radi preglednosti)
usluga = st.text_input("Usluga:") 
d, m, g = st.columns(3)
dan = d.selectbox("Dan:", range(1, 32))
mjesec = m.selectbox("Mjesec:", range(1, 13))
godina = g.selectbox("Godina:", [2026, 2027])
datum_str = f"{dan:02d}/{mjesec:02d}/{godina}"

if st.button("POTVRDI REZERVACIJU"):
    if ime and prezime:
        df = ucitaj_termine()
        df = pd.concat([df, pd.DataFrame([{"Ime": ime, "Prezime": prezime, "Kontakt": kontakt, "Datum": datum_str, "Usluga": usluga}])], ignore_index=True)
        df.to_csv("termini.csv", index=False)
        posalji_discord(ime, prezime, datum_str, usluga)
        st.success("VAŠ TERMIN JE USPJEŠNO REZERVIRAN!")
        time.sleep(2); st.rerun()

# OTKAZIVANJE
st.markdown("---")
st.subheader("🔎 Otkazivanje rezervacije")
ime_otkaz = st.text_input("Ime za otkaz:")
prezime_otkaz = st.text_input("Prezime za otkaz:")

if ime_otkaz and prezime_otkaz:
    df = ucitaj_termine()
    # Pretraga bez obzira na velika/mala slova
    maska = (df['Ime'].str.lower() == ime_otkaz.lower()) & (df['Prezime'].str.lower() == prezime_otkaz.lower())
    moji = df[maska]
    
    if moji.empty:
        st.warning("Nije pronađen termin za to ime.")
    else:
        for idx, row in moji.iterrows():
            st.write(f"Termin: {row['Usluga']} | {row['Datum']}")
            if st.button(f"❌ Otkazi termin {idx}", key=idx):
                df = df.drop(idx)
                df.to_csv("termini.csv", index=False)
                st.success("Termin otkazan.")
                st.rerun()

# ADMIN
with st.sidebar:
    st.header("🔐 Admin")
    if st.text_input("Lozinka:", type="password") == st.secrets.get("ADMIN_PASSWORD"):
        df = ucitaj_termine()
        st.dataframe(df)
