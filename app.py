import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", page_icon="✂️", layout="centered")

# --- KONFIGURACIJA USLUGA ---
usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": [
        "Oblikovanje obrva pincetom - 8€", 
        "Oblikovanje i bojanje obrva - 15€", 
        "Brow lift - 30€",
        "Brow lift i bojanje - 35€"
    ],
    "Tretmani lica": [
        "Enzimski piling - 25€", 
        "Blagi mehanički piling - 20€",
        "Parenje toplim ručnikom i masaža uz piling - 35€"
    ],
    "Frizure": [
        "Kratka kosa - Ravnanje - 10€", 
        "Kratka kosa - Uvijanje - 20€", 
        "Kratka kosa - Hollywood valovi - 25€", 
        "Kratka kosa - Elegantni repovi - 15€",
        "Duga kosa - Ravnanje - 20€", 
        "Duga kosa - Uvijanje - 30€", 
        "Duga kosa - Hollywood valovi - 35€", 
        "Duga kosa - Elegantni repovi - 25€",
        "Punđa - 15€"
    ],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}
}

# --- FUNKCIJE ---
def posalji_na_discord(naslov, ime, usluga, kontakt, datum, vrijeme):
    webhook_url = st.secrets.get("DISCORD_WEBHOOK")
    if not webhook_url: return
    
    embed = {
        "title": f"🔔 {naslov}",
        "color": 3066993, 
        "fields": [
            {"name": "👤 Klijent", "value": ime, "inline": False},
            {"name": "✂️ Usluga", "value": usluga, "inline": False},
            {"name": "📱 Kontakt", "value": kontakt, "inline": False},
            {"name": "📅 Datum", "value": datum, "inline": True},
            {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True}
        ]
    }
    try:
        requests.post(webhook_url, json={"embeds": [embed]})
    except:
        pass

def ucitaj_termine():
    if os.path.exists("termini.csv"):
        try:
            return pd.read_csv("termini.csv", dtype=str)
        except Exception:
            return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga"])
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga"])

def spremi_termin(ime_puno, kontakt, dat_str, vrijeme, usluga):
    df = ucitaj_termine()
    novi = pd.DataFrame([{"Ime": ime_puno, "Kontakt": kontakt, "Datum": dat_str, "Vrijeme": vrijeme, "Usluga": usluga}])
    df = pd.concat([df, novi], ignore_index=True)
    df.to_csv("termini.csv", index=False)
    posalji_na_discord("Nova rezervacija!", ime_puno, usluga, kontakt, dat_str, vrijeme)

def obrisi_termin(index):
    df = ucitaj_termine()
    if index in df.index:
        termin = df.loc[index]
        posalji_na_discord("Termin otkazan!", termin['Ime'], termin['Usluga'], termin['Kontakt'], termin['Datum'], termin['Vrijeme'])
        df = df.drop(index)
        df.to_csv("termini.csv", index=False)
        return True
    return False

# --- UI ---
st.title("✨ Adora Beauty Concept")

st.info("""
⚠️ **Napomena:** - Otkazivanje termina potrebno je najaviti najmanje 24h prije termina. 
Termini otkazani unutar 24h ili nedolazak bez obavijesti naplaćuju se u iznosu 100% cijene usluge.
""")

# Unos
col_i, col_p = st.columns(2)
with col_i: ime = st.text_input("Ime:")
with col_p: prezime = st.text_input("Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")
kat = st.selectbox("Odaberite kategoriju:", list(usluge_mapa.keys()), index=None)

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        col1, col2, col3 = st.columns(3)
        with col1: dan = st.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
        with col2: mjesec = st.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
        with col3: godina = st.selectbox("Godina:", [str(g) for g in range(2026, 2030)])
        dat_str = f"{dan}/{mjesec}/{godina}"
        
        df_svi = ucitaj_termine()
        zauzeti = df_svi[df_svi['Datum'] == dat_str]['Vrijeme'].tolist()
        slobodni = [f"{h:02d}:00" for h in range(8, 21) if f"{h:02d}:00" not in zauzeti]
        vrijeme = st.selectbox("Vrijeme:", slobodni)

        if st.button("POTVRDI REZERVACIJU"):
            if ime and prezime and kontakt:
                spremi_termin(f"{ime} {prezime}", kontakt, dat_str, vrijeme, usluga)
                st.success("Rezervacija potvrđena!")
                time.sleep(1); st.rerun()
            else: st.error("Molimo ispunite sve podatke.")

# Otkazivanje
st.markdown("---")
st.subheader("👤 Otkazivanje termina")
ime_otkaz = st.text_input("Upišite puno ime i prezime za otkazivanje:")

if ime_otkaz:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.lower() == ime_otkaz.strip().lower()]
    if not moji.empty:
        for idx, row in moji.iterrows():
            if st.button(f"Otkazi: {row['Usluga']} ({row['Datum']} u {row['Vrijeme']})", key=f"btn_{idx}"):
                obrisi_termin(idx)
                st.success("Termin uspješno otkazan.")
                st.rerun()
    else:
        st.warning("Nije pronađen termin za to ime.")

# Admin
with st.sidebar:
    st.header("🔐 Admin")
    if st.text_input("Lozinka:", type="password") == "171102":
        df = ucitaj_termine()
        st.subheader("Upravljanje terminima")
        for idx, row in df.iterrows():
            st.write(f"{row['Ime']} | {row['Datum']} | {row['Vrijeme']}")
            if st.button(f"Obriši termin", key=f"del_{idx}"):
                obrisi_termin(idx)
                st.rerun()
