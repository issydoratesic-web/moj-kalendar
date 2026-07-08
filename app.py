import streamlit as st
import pandas as pd
import os
import time
import requests

st.set_page_config(page_title="Adora Beauty Concept", layout="centered")

# --- FUNKCIJA ZA DISCORD ---
def posalji_na_discord(naslov, ime, usluga, kontakt, detalji):
    webhook_url = "https://discord.com/api/webhooks/1524364417167261887/vacZD177MFgx-JaegBXKT2hM9ZtsDNj_D1eZoNACpjL9NB225Ewk5_zlxpLshBdPSzS4"
    embed = {
        "title": naslov,
        "color": 16753920,
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

def ucitaj_termine():
    if os.path.exists("termini.csv"): return pd.read_csv("termini.csv", dtype=str)
    return pd.DataFrame(columns=["Ime", "Kontakt", "Datum", "Vrijeme", "Usluga", "Novi_klijent", "Napomena", "Laminacija", "Alergije"])

def spremi_ocjenu(ime, usluga, ocjena, komentar):
    df_ocjene = pd.DataFrame([{"Ime": ime, "Usluga": usluga, "Ocjena": ocjena, "Komentar": komentar}])
    if os.path.exists("ocjene.csv"): df_ocjene.to_csv("ocjene.csv", mode='a', header=False, index=False)
    else: df_ocjene.to_csv("ocjene.csv", index=False)

def ucitaj_ocjene():
    if os.path.exists("ocjene.csv"): return pd.read_csv("ocjene.csv")
    return pd.DataFrame()

# --- GLAVNI UI ---
st.title("Adora Beauty Concept")

# ... (CSS i ostali UI elementi ostaju isti kao prije) ...

col_i, col_p = st.columns(2)
ime = col_i.text_input("Ime:")
prezime = col_p.text_input("Prezime:")
kontakt = st.text_input("Kontakt:")
usluge_lista = ["Šminkanje - 40€", "Brow lift - 30€", "Laminacija obrva - 20€", "Duga kosa - 30€"]
odabrane_usluge = st.multiselect("Usluge:", usluge_lista)

# Logika pitanja
lam_da_ne, alergije = "N/A", "N/A"
if any("Brow lift" in u or "Laminacija" in u for u in odabrane_usluge):
    lam_da_ne = st.radio("Jeste li u zadnjih 6 tj. radili laminaciju?", ["Da", "Ne"], index=None, key="lam")
    alergije = st.text_input("Alergije?", key="alg")

novi_klijent = st.radio("Jeste li novi klijent?", ["Da", "Ne"], index=None, key="novi")
napomena = st.text_area("Napomena:", key="nap")
dan = st.selectbox("Dan:", [f"{i:02d}" for i in range(1, 32)])

if st.button("POTVRDI REZERVACIJU"):
    if ime and prezime and kontakt:
        df = ucitaj_termine()
        novi = pd.DataFrame([{"Ime": f"{ime} {prezime}", "Kontakt": kontakt, "Datum": dan, "Vrijeme": "08:00", "Usluga": ", ".join(odabrane_usluge), "Novi_klijent": novi_klijent, "Napomena": napomena, "Laminacija": lam_da_ne, "Alergije": alergije}])
        pd.concat([df, novi], ignore_index=True).to_csv("termini.csv", index=False)
        
        # OBAVIJEST NA DISCORD - ZAKAZIVANJE
        posalji_na_discord("🔔 Nova rezervacija!", f"{ime} {prezime}", ", ".join(odabrane_usluge), kontakt, f"Datum: {dan}")
        
        st.success("Hvala na rezervaciji! Termin je zaprimljen. Potvrdu termina primit ćete u najkraćem roku putem Instagrama ili WhatsAppa.")
        time.sleep(5); st.rerun()

# --- OTKAZIVANJE TERMINA ---
ime_otkaz = st.text_input("Ime za pronalazak termina:")
if ime_otkaz:
    df = ucitaj_termine()
    moji = df[df['Ime'].str.contains(ime_otkaz, case=False, na=False)]
    for idx, row in moji.iterrows():
        with st.expander(f"Termin: {row['Usluga']}"):
            if st.button("Otkazi termin", key=f"del_{idx}"):
                # OBAVIJEST NA DISCORD - OTKAZIVANJE
                posalji_na_discord("❌ Otkazan termin!", row['Ime'], row['Usluga'], row['Kontakt'], f"Datum: {row['Datum']}")
                df.drop(idx).to_csv("termini.csv", index=False); st.rerun()
