import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- CSS STILOVI ---
st.markdown("""
    <style>
    /* 1. Pozadina cijele stranice */
    .stApp { background-color: #fffafc !important; }

    /* 2. STILIZIRANI NASLOV */
    .custom-title {
        color: #d63384 !important;
        font-size: 50px !important;
        font-weight: bold !important;
        text-align: center !important;
        text-shadow: 2px 2px 4px #ffc0cb;
        margin-bottom: 30px;
    }

    /* 3. POLJA ZA UNOS (Input, Selectbox) - Bijela s roza rubom */
    div[data-baseweb="base-input"], div[data-baseweb="select"] > div, input, textarea {
        background-color: #ffffff !important;
        color: black !important;
        border: 2px solid #ffb6c1 !important;
        border-radius: 10px !important;
    }

    /* 4. OTVORENI PADAJUĆI IZBORNICI (Roza podloga) */
    div[role="listbox"], ul[role="listbox"] {
        background-color: #fff0f5 !important;
        color: black !important;
    }
    
    li[role="option"] { color: black !important; }
    li[role="option"]:hover { background-color: #ffc0cb !important; }

    /* 5. GUMBI */
    div.stButton > button {
        background-color: #d63384 !important;
        color: white !important;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCIJA ZA DISCORD ---
def posalji_na_discord(naslov, ime, usluga, kontakt, detalji):
    webhook_url = "https://discord.com/api/webhooks/1524364417167261887/vacZD177MFgx-JaegBXKT2hM9ZtsDNj_D1eZoNACpjL9NB225Ewk5_zlxpLshBdPSzS4" 
    if not webhook_url.startswith("http"): return # Sprječava rušenje ako URL nije unesen
    
    embed = {
        "title": naslov, "color": 16753920,
        "fields": [
            {"name": "👤 Klijent", "value": ime, "inline": False},
            {"name": "✂️ Usluga", "value": usluga, "inline": False},
            {"name": "📱 Kontakt", "value": kontakt, "inline": False},
            {"name": "📝 Detalji", "value": detalji, "inline": False}
        ]
    }
    data = {"embeds": [embed]}
    try: requests.post(webhook_url, json=data)
    except: pass

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Usluga", "Novi_klijent", "Napomena"])

# --- ADMIN PANEL ---
with st.sidebar:
    st.header("🔐 Admin Panel")
    if 'admin_auth' not in st.session_state: st.session_state.admin_auth = False
    
    if not st.session_state.admin_auth:
        pwd = st.text_input("Lozinka:", type="password")
        if st.button("Prijava"):
            if pwd == "171102": st.session_state.admin_auth = True; st.rerun()
            else: st.error("Pogrešna lozinka!")
    else:
        if st.button("Odjava"): st.session_state.admin_auth = False; st.rerun()
        st.subheader("Upravljanje terminima")
        df = ucitaj_termine()
        for idx, row in df.iterrows():
            with st.expander(f"{row['Ime']} - {row['Datum']}"):
                st.write(f"Usluga: {row['Usluga']}")
                if st.button(f"OBRIŠI {row['Ime']}", key=f"del_{idx}"):
                    df.drop(idx).to_csv("termini.csv", index=False)
                    st.rerun()

# --- GLAVNI UI ---
st.markdown("<h1 class='custom-title'>ADORA BEAUTY CONCEPT</h1>", unsafe_allow_html=True)

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")

kat = st.selectbox("Odaberite kategoriju:", ["Šminkanje", "Oblikovanje i korekcija obrva", "Tretmani lica", "Frizure", "Little Luxe Spa"], index=None)

usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
    "Frizure": ["Kratka kosa - Ravnanje - 10€", "Duga kosa - Uvijanje - 30€"],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        st.subheader("Dodatna pitanja")
        novi_klijent = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None)
        napomena = st.text_area("Napomena:")
        
        c1, c2, c3 = st.columns(3)
        dan = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
        mjesec = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
        godina = c3.selectbox("Godina:", ["2026", "2027", "2028", "2029", "2030"])
        
        if st.button("POTVRDI REZERVACIJU"):
            if ime and prezime and kontakt and novi_klijent:
                df = ucitaj_termine()
                novi = pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": f"{dan}/{mjesec}/{godina}", "Usluga": usluga, "Novi_klijent": novi_klijent, "Napomena": napomena}])
                pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
                posalji_na_discord("🔔 Nova rezervacija!", f"{ime} {prezime}", usluga, kontakt, f"Novi: {novi_klijent}")
                st.success("Hvala na rezervaciji! 🌸")
                time.sleep(2); st.rerun()
            else: st.error("Molimo ispunite obavezna polja.")

st.markdown("---")
st.subheader("👤 Otkazivanje termina")
ime_otkaz = st.text_input("Upišite ime za otkazivanje:")
if ime_otkaz:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.lower() == ime_otkaz.strip().lower()]
    if not moji.empty:
        for idx, row in moji.iterrows():
            if st.button(f"Otkazi: {row['Usluga']} ({row['Datum']})"):
                posalji_na_discord("❌ Termin otkazan", row['Ime'], row['Usluga'], row['Kontakt'], "Klijent otkazao.")
                df.drop(idx).to_csv("termini.csv", index=False)
                st.success("Vaš termin je otkazan! 🌸")
                time.sleep(2); st.rerun()
