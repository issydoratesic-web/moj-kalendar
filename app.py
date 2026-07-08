import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- FUNKCIJA ZA DISCORD ---
def posalji_na_discord(naslov, ime, narudzba, kontakt):
    webhook_url = "https://discord.com/api/webhooks/1524364417167261887/vacZD177MFgx-JaegBXKT2hM9ZtsDNj_D1eZoNACpjL9NB225Ewk5_zlxpLshBdPSzS4"
    embed = {
        "title": naslov,
        "color": 16753920,
        "fields": [
            {"name": "👤 Klijent", "value": ime, "inline": False},
            {"name": "📋 Narudžba", "value": narudzba, "inline": False},
            {"name": "📱 Kontakt", "value": kontakt, "inline": False}
        ]
    }
    requests.post(webhook_url, json={"embeds": [embed]})

# --- FUNKCIJE ---
def ucitaj_termine():
    if os.path.exists("termini.csv"):
        return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Narudzba"])

# --- SESSION STATE ---
if 'kosarica' not in st.session_state: st.session_state.kosarica = []

# --- GLAVNI UI ---
st.title("✨ Adora Beauty Concept")

ime_prezime = st.text_input("Ime i Prezime:")
kontakt = st.text_input("Broj mobitela ili instagram korisničko ime:")

st.markdown("---")
st.subheader("🛠️ Dodaj usluge u narudžbu")

kat = st.selectbox("Odaberite kategoriju:", ["Šminkanje", "Oblikovanje i korekcija obrva", "Tretmani lica", "Frizure", "Little Luxe Spa"])
usluge_mapa = {
    "Šminkanje": ["Šminkanje", "Terensko šminkanje"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva", "Brow lift"],
    "Tretmani lica": ["Piling", "Masaža"],
    "Frizure": ["Ravnanje", "Uvijanje", "Hollywood valovi", "Punđa"],
    "Little Luxe Spa": ["Mini", "Classic", "VIP"]
}

usluga = st.selectbox("Usluga:", usluge_mapa[kat])
broj_osoba = st.selectbox("Broj osoba za ovu uslugu:", options=[i for i in range(1, 11)])

if st.button("➕ Dodaj u narudžbu"):
    st.session_state.kosarica.append({"Usluga": usluga, "Osobe": broj_osoba})
    st.rerun()

st.markdown("---")
st.subheader("📋 Vaša trenutna narudžba:")
if st.session_state.kosarica:
    for i, item in enumerate(st.session_state.kosarica):
        st.write(f"{i+1}. **{item['Usluga']}** - {item['Osobe']} osoba")
        if st.button(f"Ukloni stavku {i+1}", key=f"del_{i}"):
            st.session_state.kosarica.pop(i)
            st.rerun()
else:
    st.info("Košarica je prazna. Dodajte usluge.")

st.markdown("---")
st.subheader("📅 Datum termina")
c1, c2, c3 = st.columns(3)
dan = c1.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
mjesec = c2.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
godina = c3.selectbox("Godina:", ["2026", "2027", "2028"])

if st.button("✅ POTVRDI CIJELU REZERVACIJU"):
    if ime_prezime and kontakt and st.session_state.kosarica:
        narudzba_tekst = ", ".join([f"{x['Usluga']} ({x['Osobe']} os.)" for x in st.session_state.kosarica])
        
        # Spremanje u CSV
        df = ucitaj_termine()
        novi = pd.DataFrame([{"Ime": ime_prezime, "Kontakt": kontakt, "Datum": f"{dan}/{mjesec}/{godina}", "Narudzba": narudzba_tekst}])
        pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
        
        # Slanje na Discord
        posalji_na_discord("🔔 Nova rezervacija", ime_prezime, narudzba_tekst, kontakt)
        
        st.success("Hvala! Vaša narudžba je zaprimljena.")
        st.session_state.kosarica = []
        time.sleep(2)
        st.rerun()
    else:
        st.error("Molimo ispunite ime, kontakt i dodajte barem jednu uslugu u košaricu.")
