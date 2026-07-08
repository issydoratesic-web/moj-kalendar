import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- KONFIGURACIJA ---
usluge_mapa = {
    "Šminkanje": ["Šminkanje - 40€", "Terensko šminkanje - 50€"],
    "Oblikovanje i korekcija obrva": ["Oblikovanje obrva pincetom - 8€", "Oblikovanje i bojanje obrva - 15€", "Brow lift - 30€", "Brow lift i bojanje - 35€"],
    "Tretmani lica": ["Enzimski piling - 25€", "Blagi mehanički piling - 20€", "Parenje toplim ručnikom i masaža uz piling - 35€"],
    "Frizure": ["Kratka kosa - Ravnanje - 10€", "Kratka kosa - Uvijanje - 20€", "Kratka kosa - Hollywood valovi - 25€", "Kratka kosa - Elegantni repovi - 15€", "Duga kosa - Ravnanje - 20€", "Duga kosa - Uvijanje - 30€", "Duga kosa - Hollywood valovi - 35€", "Duga kosa - Elegantni repovi - 25€", "Punđa - 15€"],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

def posalji_na_discord(naslov, ime, usluga, kontakt, datum, vrijeme, extra=""):
    webhook_url = st.secrets.get("DISCORD_WEBHOOK")
    if not webhook_url: return
    embed = {"title": f"🔔 {naslov}", "color": 3066993, "fields": [
        {"name": "👤 Klijent", "value": ime, "inline": False},
        {"name": "✂️ Usluga", "value": usluga, "inline": False},
        {"name": "📱 Kontakt", "value": kontakt, "inline": False},
        {"name": "📅 Datum", "value": datum, "inline": True},
        {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True},
        {"name": "📝 Detalji", "value": extra, "inline": False}
    ]}
    try: requests.post(webhook_url, json={"embeds": [embed]})
    except: pass

def ucitaj_termine():
    kolone = ["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena", "Laminacija_DA_NE", "Alergije"]
    if os.path.exists("termini.csv"):
        try: return pd.read_csv("termini.csv", dtype=str)
        except: return pd.DataFrame(columns=kolone)
    return pd.DataFrame(columns=kolone)

# --- UI ---
st.markdown("<h1 style='text-align: center;'>Adora Beauty Concept</h1>", unsafe_allow_html=True)

st.info("""
**Uvjeti poslovanja**
* **Otkazivanje:** Najmanje 24h unaprijed (100% cijene u slučaju nedolaska).
* **Akontacija (šminkanje):** 50% na IBAN HR03 2402 0061 1406 1395 3. Opis: Akontacija za termin - [Datum]
""")

col1, col2 = st.columns(2)
ime = col1.text_input("Ime:")
prezime = col2.text_input("Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")
kat = st.selectbox("Kategorija:", list(usluge_mapa.keys()), index=None)

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        st.subheader("Dodatna pitanja")
        novi_klijent = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None)
        napomena = st.text_area("Napomena (stil, inspiracija...):")
        
        lam_da_ne, alergije = "N/A", "N/A"
        if "Brow lift" in usluga:
            st.warning("⚠️ Za laminaciju obrva:")
            lam_da_ne = st.radio("Jeste li u posljednjih 6 tjedana radili laminaciju ili lifting trepavica?", ["Da", "Ne"], index=None)
            alergije = st.text_input("Imate li poznate alergije na kozmetičke proizvode?")

        d, m, g = st.columns(3)
        dat_str = f"{d.selectbox('Dan:', [f'{i:02d}' for i in range(1, 32)])}/{m.selectbox('Mjesec:', [f'{i:02d}' for i in range(1, 13)])}/{g.selectbox('Godina:', ['2026', '2027'])}"
        vrijeme = st.selectbox("Vrijeme:", [f"{h:02d}:00" for h in range(8, 21)])

        if st.button("POTVRDI REZERVACIJU"):
            if ime and prezime and kontakt and novi_klijent:
                df = ucitaj_termine()
                novi = pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": dat_str, "Vrijeme": vrijeme, "Usluga": usluga, "Novi_klijent": novi_klijent, "Napomena": napomena, "Laminacija_DA_NE": lam_da_ne, "Alergije": alergije}])
                pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
                posalji_na_discord("Nova rezervacija!", f"{ime} {prezime}", usluga, kontakt, dat_str, vrijeme, f"Novi: {novi_klijent}, Lam: {lam_da_ne}, Aler: {alergije}")
                st.success("Rezervacija potvrđena!"); time.sleep(1); st.rerun()
            else: st.error("Molimo ispunite obavezna polja.")

st.markdown("---")
st.subheader("👤 Otkazivanje termina")
ime_otkaz = st.text_input("Upišite ime i prezime za otkazivanje:")
if ime_otkaz:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.lower() == ime_otkaz.strip().lower()]
    if not moji.empty:
        for idx, row in moji.iterrows():
            if st.button(f"Otkazi: {row['Usluga']} ({row['Datum']} u {row['Vrijeme']})", key=idx):
                posalji_na_discord("Termin otkazan!", row['Ime'], row['Usluga'], row['Kontakt'], row['Datum'], row['Vrijeme'])
                df.drop(idx).to_csv("termini.csv", index=False)
                st.success("Termin je uspješno otkazan."); time.sleep(2); st.rerun()
    else:
        st.warning("Nije pronađen termin za to ime.")
