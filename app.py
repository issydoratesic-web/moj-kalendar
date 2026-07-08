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
        "Kratka kosa - Ravnanje - 10€", "Kratka kosa - Uvijanje - 20€", 
        "Kratka kosa - Hollywood valovi - 25€", "Kratka kosa - Elegantni repovi - 15€",
        "Duga kosa - Ravnanje - 20€", "Duga kosa - Uvijanje - 30€", 
        "Duga kosa - Hollywood valovi - 35€", "Duga kosa - Elegantni repovi - 25€",
        "Punđa - 15€"
    ],
    "Little Luxe Spa": ["Mini - 50€", "Classic - 70€", "VIP - 100€"]
}

# --- FUNKCIJE ---
def posalji_na_discord(naslov, ime, usluga, kontakt, datum, vrijeme, extra_info=""):
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
            {"name": "⏰ Vrijeme", "value": vrijeme, "inline": True},
            {"name": "📝 Dodatno", "value": extra_info if extra_info else "Nema", "inline": False}
        ]
    }
    try: requests.post(webhook_url, json={"embeds": [embed]})
    except: pass

def ucitaj_termine():
    if os.path.exists("termini.csv"):
        try: return pd.read_csv("termini.csv", dtype=str)
        except: return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi klijent", "Napomena", "Laminacija_pitanje", "Alergije_pitanje"])
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi klijent", "Napomena", "Laminacija_pitanje", "Alergije_pitanje"])

def spremi_termin(ime, kontakt, dat, vrij, usl, novi, nap, lam, aler):
    df = ucitaj_termine()
    novi_red = pd.DataFrame([{"Ime": ime, "Kontakt": kontakt, "Datum": dat, "Vrijeme": vrij, "Usluga": usl, "Novi klijent": novi, "Napomena": nap, "Laminacija_pitanje": lam, "Alergije_pitanje": aler}])
    df = pd.concat([df, novi_red], ignore_index=True)
    df.to_csv("termini.csv", index=False)
    extra = f"Novi klijent: {novi}\nNapomena: {nap}\nLaminacija u 6tj: {lam}\nAlergije: {aler}"
    posalji_na_discord("Nova rezervacija!", ime, usl, kontakt, dat, vrij, extra)

# --- UI ---
st.markdown("<h1 style='text-align: center;'>ADORA BEAUTY CONCEPT</h1>", unsafe_allow_html=True)

st.info("""
**Uvjeti poslovanja**
* **Otkazivanje:** Najmanje 24h unaprijed (100% cijene u slučaju nedolaska).
* **Akontacija (šminkanje):** 50% na IBAN HR03 2402 0061 1406 1395 3. Opis: Akontacija za termin - [Datum]
""")

col_i, col_p = st.columns(2)
with col_i: ime = st.text_input("Ime:")
with col_p: prezime = st.text_input("Prezime:")
kontakt = st.text_input("Kontakt (IG/Br):")
kat = st.selectbox("Kategorija:", list(usluge_mapa.keys()), index=None)

if kat:
    usluga = st.selectbox("Usluga:", usluge_mapa[kat], index=None)
    if usluga:
        st.subheader("Dodatna pitanja")
        status_klijenta = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None)
        napomena = st.text_area("Napomena za termin (stil, inspiracija...):")
        
        # Dinamička pitanja za laminaciju
        lam_pitanje, aler_pitanje = "N/A", "N/A"
        if "Brow lift" in usluga:
            st.warning("⚠️ Za laminaciju obrva:")
            lam_pitanje = st.radio("Jeste li u posljednjih 6 tjedana radili laminaciju ili lifting trepavica?", ["Da", "Ne"], index=None)
            aler_pitanje = st.text_input("Imate li poznate alergije na kozmetičke proizvode?")

        col1, col2, col3 = st.columns(3)
        with col1: dan = st.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])
        with col2: mjesec = st.selectbox("Mjesec:", [f"{i:02d}" for i in range(1, 13)])
        with col3: godina = st.selectbox("Godina:", [str(g) for g in range(2026, 2030)])
        vrijeme = st.selectbox("Vrijeme:", [f"{h:02d}:00" for h in range(8, 21)])

        if st.button("POTVRDI REZERVACIJU"):
            if ime and prezime and kontakt and status_klijenta:
                spremi_termin(f"{ime} {prezime}", kontakt, f"{dan}/{mjesec}/{godina}", vrijeme, usluga, status_klijenta, napomena, lam_pitanje, aler_pitanje)
                st.success("Rezervacija potvrđena!")
                time.sleep(1); st.rerun()
            else: st.error("Molimo ispunite obavezna polja.")
