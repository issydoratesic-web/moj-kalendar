import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- CSS STILOVI ---
st.markdown("""
    <style>
    /* 1. Postavi pozadinu aplikacije */
    .stApp { background-color: #fdfbfb !important; }

    /* 2. SVA POLJA ZA UNOS (Input, Textarea, Selectbox) - Roza pozadina i crna slova */
    div[data-baseweb="base-input"], 
    div[data-baseweb="select"] > div, 
    input, 
    textarea, 
    div[role="combobox"] {
        background-color: #fff0f5 !important;
        color: black !important;
        border: 1px solid #ffb6c1 !important;
        border-radius: 10px !important;
    }

    /* 3. OSIGURAJ DA JE TEKST U POLJIMA CRN */
    input, textarea, div[role="combobox"] div, p {
        color: black !important;
    }

    /* 4. OTVORENI PADAJUĆI IZBORNICI (Ono što je bilo sivo) */
    div[role="listbox"], ul[role="listbox"] {
        background-color: #fff0f5 !important;
        color: black !important;
    }
    
    li[role="option"] {
        background-color: #fff0f5 !important;
        color: black !important;
    }
    
    /* Hover efekt unutar izbornika */
    li[role="option"]:hover {
        background-color: #ffc0cb !important;
    }

    /* 5. NASLOVI I TEKST */
    h1, h2, h3, label, p {
        color: black !important;
    }

    /* 6. PRILAGOĐENI BOX */
    .custom-box { 
        background-color: #fff0f5; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #d63384; 
        color: black !important;
    }
    
    /* 7. GUMBI */
    div.stButton > button {
        background-color: #d63384 !important;
        color: white !important;
        border-radius: 10px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNKCIJA ZA DISCORD ---
def posalji_na_discord(naslov, ime, usluga, kontakt, detalji):
    webhook_url = "TVOJ_DISCORD_WEBHOOK_URL_OVDJE" 
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
st.title("✨ Adora Beauty Concept")
st.markdown("""<div class='custom-box'><strong>Napomena:</strong><br>• Otkazivanje termina min. 24h ranije.<br>• Šminkanje: obavezna akontacija 50%.<br>IBAN: HR03 2402 0061 1406 1395 3</div>""", unsafe_allow_html=True)

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
                posalji_na_discord("🔔 Nova rezervacija!", f"{ime} {prezime}", usluga, kontakt, f"Novi: {novi_klijent}, Napomena: {napomena}")
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
                posalji_na_discord("❌ Termin otkazan", row['Ime'], row['Usluga'], row['Kontakt'], "Klijent je sam otkazao.")
                df.drop(idx).to_csv("termini.csv", index=False)
                st.success("Vaš termin je uspješno otkazan! 🌸")
                time.sleep(2); st.rerun()
