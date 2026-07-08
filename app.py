import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- CSS STILOVI ---
st.markdown("""
    <style>
    /* 1. Pozadina stranice */
    .stApp { background-color: #fff0f5 !important; }

    /* 2. Naslov */
    .simple-luxury-title {
        color: #d63384 !important;
        font-family: 'Georgia', serif !important;
        font-size: 35px !important;
        text-align: center !important;
        text-transform: uppercase !important;
        margin-bottom: 30px;
    }

    /* 3. Polja za unos (Input, Selectbox) - Bijela s roza rubom */
    div[data-baseweb="base-input"], div[data-baseweb="select"] > div, input, textarea {
        background-color: #ffffff !important;
        color: black !important;
        border: 1px solid #ffb6c1 !important;
        border-radius: 0px !important; 
    }

    /* 4. Padajući izbornici (Rješava sivu boju) */
    div[role="listbox"], ul[role="listbox"], li[role="option"] {
        background-color: #fff0f5 !important;
        color: black !important;
    }
    li[role="option"]:hover { background-color: #ffc0cb !important; }

    /* 5. Gumbi */
    div.stButton > button {
        background-color: #d63384 !important;
        color: white !important;
        border-radius: 0px !important;
        border: none !important;
        font-family: 'Georgia', serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCIJE ---
def posalji_na_discord(naslov, poruka):
    webhook_url = "TVOJ_DISCORD_WEBHOOK_URL_OVDJE" 
    if "TVOJ_DISCORD" in webhook_url: return
    data = {"embeds": [{"title": naslov, "description": poruka, "color": 16753920}]}
    try: requests.post(webhook_url, json=data)
    except: pass

def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Usluga", "Novi_klijent", "Napomena"])

# --- ADMIN PANEL ---
with st.sidebar:
    st.header("🔐 Admin Panel")
    pwd = st.text_input("Lozinka:", type="password")
    if pwd == "171102":
        st.subheader("Upravljanje terminima")
        df = ucitaj_termine()
        for idx, row in df.iterrows():
            with st.expander(f"{row['Ime']} - {row['Datum']}"):
                st.write(f"Usluga: {row['Usluga']}")
                if st.button(f"OBRIŠI", key=f"del_{idx}"):
                    df.drop(idx).to_csv("termini.csv", index=False)
                    st.rerun()

# --- GLAVNI UI ---
st.markdown("<h1 class='simple-luxury-title'>ADORA BEAUTY CONCEPT</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
ime = col1.text_input("Ime:")
prezime = col2.text_input("Prezime:")
kontakt = st.text_input("Kontakt (mobitel/Instagram):")

kat = st.selectbox("Odaberite kategoriju:", ["Šminkanje", "Oblikovanje obrva", "Tretmani lica"], index=None)

if kat:
    usluga = st.selectbox("Usluga:", ["Usluga 1", "Usluga 2"], index=None)
    if usluga:
        novi = st.radio("Novi klijent?", ["Da", "Ne"], index=None)
        napomena = st.text_area("Napomena:")
        
        c1, c2, c3 = st.columns(3)
        dan = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
        mjesec = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
        godina = c3.selectbox("Godina:", ["2026", "2027", "2028"])
        
        if st.button("POTVRDI REZERVACIJU"):
            if ime and prezime and kontakt:
                novi_termin = pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": f"{dan}.{mjesec}.{godina}", "Usluga": usluga}])
                df = pd.concat([ucitaj_termine(), novi_termin], ignore_index=True)
                df.to_csv("termini.csv", index=False)
                posalji_na_discord("Nova rezervacija", f"Klijent: {ime} {prezime}\nKontakt: {kontakt}\nUsluga: {usluga}")
                st.success("Uspješno rezervirano!")
                time.sleep(2); st.rerun()
            else:
                st.error("Ispunite podatke!")
